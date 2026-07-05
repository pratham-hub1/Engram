import aiosqlite
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)

DB_PATH = Path(".cognee_system") / "engram_state.db"

async def init_db():
    """Initializes the SQLite database schema for the application state."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Table for mapping our documents to Cognee's internal data_id
        await db.execute('''
            CREATE TABLE IF NOT EXISTS memories_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_id TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                source_path TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for tracking high-signal events lacking a confirmed reason
        await db.execute('''
            CREATE TABLE IF NOT EXISTS nudge_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for pipeline failures
        await db.execute('''
            CREATE TABLE IF NOT EXISTS retry_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_payload TEXT NOT NULL,
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                next_retry_at DATETIME
            )
        ''')
        
        # Table for project settings (like initial indexing status)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS project_settings (
                dataset_name TEXT PRIMARY KEY,
                is_indexed BOOLEAN DEFAULT FALSE,
                indexing_status TEXT DEFAULT 'UNINDEXED',
                indexed_at DATETIME
            )
        ''')
        
        # Add indexing_status column if it doesn't exist (migration)
        try:
            await db.execute('ALTER TABLE project_settings ADD COLUMN indexing_status TEXT DEFAULT "UNINDEXED"')
        except Exception:
            pass # Column likely already exists
            
        # Table for caching heavy API responses
        await db.execute('''
            CREATE TABLE IF NOT EXISTS key_value_cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.commit()
    
    logger.info("Application state database initialized", db_path=str(DB_PATH))

async def get_db():
    """Dependency provider for FastAPI or pipeline usage."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def get_indexing_status(dataset_name: str) -> str:
    """Gets the exact state of indexing (UNINDEXED, INDEXING, COMPLETED)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT indexing_status, is_indexed FROM project_settings WHERE dataset_name = ?', (dataset_name,)) as cursor:
            row = await cursor.fetchone()
            if row:
                if row[0]: return row[0]
                if row[1]: return 'COMPLETED'
            return 'UNINDEXED'

async def set_indexing_status(dataset_name: str, status: str):
    """Sets the exact state of indexing."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO project_settings (dataset_name, indexing_status, is_indexed, indexed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(dataset_name) DO UPDATE SET
            indexing_status=?, is_indexed=?, indexed_at=CURRENT_TIMESTAMP
        ''', (dataset_name, status, 1 if status == 'COMPLETED' else 0, status, 1 if status == 'COMPLETED' else 0))
        await db.commit()

async def has_recent_decision(source_path: str, hours: int = 24) -> bool:
    """Checks if a decision note or commit reason was logged for this file in the last N hours."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT 1 FROM memories_log 
            WHERE event_type IN ('MANUAL_NOTE', 'GIT_COMMIT_WITH_REASON')
            AND source_path = ?
            AND timestamp >= datetime('now', ?)
        ''', (source_path, f'-{hours} hours',)) as cursor:
            row = await cursor.fetchone()
            return bool(row)

async def add_nudge(event_type: str, file_path: str):
    """Adds a high-signal event to the nudge queue if not already present."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Avoid duplicate nudges for the same file
        await db.execute('''
            DELETE FROM nudge_queue WHERE file_path = ?
        ''', (file_path,))
        await db.execute('''
            INSERT INTO nudge_queue (event_type, file_path)
            VALUES (?, ?)
        ''', (event_type, file_path))
        await db.commit()

async def get_nudges():
    """Returns all unresolved nudges."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM nudge_queue ORDER BY timestamp DESC') as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def remove_nudge(file_path: str):
    """Removes a nudge when a decision is recorded."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM nudge_queue WHERE file_path = ?', (file_path,))
        await db.commit()

async def get_expired_memories() -> list[dict]:
    """Returns a list of expired memory data_ids and paths."""
    expired = []
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT data_id, source_path, metadata FROM memories_log WHERE metadata LIKE "%expires_at%"') as cursor:
            rows = await cursor.fetchall()
            from datetime import datetime
            now = datetime.now().date()
            import json
            for row in rows:
                try:
                    meta = json.loads(row['metadata'] or '{}')
                    expires_at = meta.get('expires_at')
                    if expires_at:
                        exp_date = datetime.strptime(expires_at, "%Y-%m-%d").date()
                        if exp_date < now:
                            expired.append({
                                "data_id": row["data_id"],
                                "source_path": row["source_path"]
                            })
                except Exception as e:
                    logger.error("Error parsing expired memory", data_id=row["data_id"], error=str(e))
    return expired

async def delete_memory_log(data_id: str):
    """Deletes a memory log entry from SQLite after it has been forgotten by Cognee."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM memories_log WHERE data_id = ?', (data_id,))
        await db.commit()

async def get_cache(key: str) -> str:
    """Retrieves a cached value by key."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT value FROM key_value_cache WHERE key = ?', (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_cache(key: str, value: str):
    """Sets a cached value by key."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO key_value_cache (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
            value=?, updated_at=CURRENT_TIMESTAMP
        ''', (key, value, value))
        await db.commit()

