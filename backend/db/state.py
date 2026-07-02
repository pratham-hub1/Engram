import aiosqlite
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)

DB_PATH = Path(".cognee_system") / "memory_ai_state.db"

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
