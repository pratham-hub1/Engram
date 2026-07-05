import json
import aiosqlite
import structlog
from typing import Optional, Tuple
from backend.db.state import DB_PATH
from backend.pipeline.models import StructuredEvent

logger = structlog.get_logger(__name__)

async def check_and_get_previous_state(event: StructuredEvent, dataset_name: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if the event is a duplicate. If not, returns (is_duplicate=False, old_data_id).
    We need old_data_id so we can forget() the stale state before ingesting the new one.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Check for exact duplicate first
            cursor = await db.execute(
                "SELECT id FROM memories_log WHERE source_path = ? AND content_hash = ? AND dataset_name = ?",
                (event.path, event.hash, dataset_name)
            )
            row = await cursor.fetchone()
            if row:
                return True, None # It's an exact duplicate, drop it
                
            # It's not a duplicate. Let's find the most recent data_id for this path
            # so we can forget it. (We only forget file states, not git commits)
            old_data_id = None
            if event.event_type != "GIT_COMMIT":
                cursor = await db.execute(
                    "SELECT data_id FROM memories_log WHERE source_path = ? AND dataset_name = ? ORDER BY timestamp DESC LIMIT 1",
                    (event.path, dataset_name)
                )
                old_row = await cursor.fetchone()
                if old_row:
                    old_data_id = old_row["data_id"]
                    
            return False, old_data_id
            
    except Exception as e:
        logger.error("Database error during state check", error=str(e))
        # Fail open: assume not duplicate, no old data_id
        return False, None

async def record_ingestion(event: StructuredEvent, data_id: str, dataset_name: str):
    """
    Records a successful ingestion in the SQLite log.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO memories_log 
                (data_id, dataset_name, source_path, event_type, content_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data_id,
                    dataset_name,
                    event.path,
                    event.event_type,
                    event.hash,
                    json.dumps(event.metadata)
                )
            )
            await db.commit()
    except Exception as e:
        logger.error("Failed to record ingestion", error=str(e))
