import structlog
from typing import Optional

from backend.observer.queue import RawEvent
from backend.pipeline.models import PipelineResult
from backend.pipeline.normalizer import normalize_event
from backend.pipeline.state_manager import check_and_get_previous_state
from backend.pipeline.extractor import extract_reasoning, log_nudge_if_needed
from backend.pipeline.ingestor import ingest_event

logger = structlog.get_logger(__name__)

async def process_event(raw: RawEvent, dataset_name: str) -> PipelineResult:
    """
    Passes a raw event through the complete memory pipeline.
    """
    logger.info("Processing event", type=raw.event_type, path=raw.path)
    
    # 1. Normalizer
    event = await normalize_event(raw)
    if not event.content:
        logger.warning("Event normalization produced empty content, skipping", path=raw.path)
        return PipelineResult(success=True, skipped=True)
        
    # 2. Deduplicator / State Manager
    is_dup, old_data_id = await check_and_get_previous_state(event, dataset_name)
    if is_dup:
        logger.debug("Duplicate event, skipping", path=event.path, hash=event.hash)
        return PipelineResult(success=True, skipped=True)
        
    # 3. Extraction (LLM)
    has_reasoning, decision = await extract_reasoning(event)
    
    content_to_ingest = event.content
    node_set = "files"
    
    if has_reasoning and decision:
        # We have extracted a decision
        content_to_ingest = f"[{event.event_type} - DECISION]\n" + decision.decision + "\nContext: " + decision.context
        node_set = "decisions"
        if event.event_type == "GIT_COMMIT":
            event.event_type = "GIT_COMMIT_WITH_REASON"
        logger.info("Extracted decision", path=event.path)
    else:
        # Check nudge queue
        await log_nudge_if_needed(event)
        # Structural event direct path
        content_to_ingest = f"[{raw.event_type} - STRUCTURAL]\n" + event.content
        if "package" in event.path or "requirements" in event.path:
            node_set = "dependencies"
        elif "config" in event.path or "yml" in event.path or "env" in event.path:
            node_set = "config"
        elif "GIT_COMMIT" in event.event_type:
            node_set = "commits"
            
    # 4. Ingestor
    data_id = await ingest_event(
        event=event,
        dataset_name=dataset_name,
        node_set=node_set,
        content=content_to_ingest,
        old_data_id=old_data_id
    )
    
    if data_id:
        return PipelineResult(success=True, data_id=data_id, node_set=node_set)
    else:
        return PipelineResult(success=False, error="Ingestion returned no data_id")
