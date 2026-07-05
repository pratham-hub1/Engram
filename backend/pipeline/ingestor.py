import structlog
from typing import Optional
from backend.pipeline.models import StructuredEvent
from backend.pipeline.state_manager import record_ingestion
from backend.memory.cognee_client import remember_event, forget_event

logger = structlog.get_logger(__name__)

import uuid

async def ingest_event(
    event: StructuredEvent, 
    dataset_name: str, 
    node_set: str, 
    content: str,
    old_data_id: Optional[str] = None
) -> Optional[str]:
    """
    Ingests content into Cognee.
    If old_data_id is provided, forgets the stale state first.
    Returns the new data_id.
    """
    try:
        # Branch the deterministic ID minting logic
        if event.event_type in ("GIT_COMMIT", "GIT_COMMIT_WITH_REASON", "MANUAL_NOTE"):
            # Append-only events: use the unique payload hash to prevent overwriting
            deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_URL, event.hash))
        else:
            # Files: use the machine-agnostic relative path to allow surgical updates
            deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_URL, event.path))
        
        # Forget the old state to prevent accumulation
        if old_data_id:
            logger.info("Forgetting stale state", old_data_id=old_data_id, path=event.path)
            await forget_event(old_data_id, dataset_name)
        
        # Ingest the new state using our deterministic ID
        logger.info("Ingesting new state", path=event.path, dataset=dataset_name, node_set=node_set)
        
        # `node_set` is passed for logging purposes, but `remember_event` doesn't take it
        # because the API doesn't support it anymore. The content itself contains semantic tags.
        result = await remember_event(content=content, dataset_name=dataset_name, data_id=deterministic_id)
        
        # No need to extract ID from result, we already dictated it
        await record_ingestion(event, deterministic_id, dataset_name)
        return deterministic_id
            
    except Exception as e:
        logger.error("Ingestion failed", error=str(e), path=event.path)
        return None
