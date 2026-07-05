from pydantic import BaseModel
from typing import Dict, Any, Optional

class StructuredEvent(BaseModel):
    """
    The normalized internal format for any project event.
    Produced by the Normalizer, consumed by the Pipeline.
    """
    event_type: str  # "FILE_MODIFIED", "FILE_CREATED", "FILE_DELETED", "GIT_COMMIT"
    path: str
    content: str     # For semantic graphs: The natural language description of the diff, or the commit message
    hash: str        # For deduplication: hash of the content
    metadata: Dict[str, Any]
    
class ExtractedDecision(BaseModel):
    """
    Output of the LLM Interpretation stage.
    """
    decision: str
    context: str
    
class PipelineResult(BaseModel):
    """
    Result of processing an event through the pipeline.
    """
    success: bool
    data_id: Optional[str] = None
    node_set: Optional[str] = None
    error: Optional[str] = None
    skipped: bool = False
