import re
import aiosqlite
import structlog
from typing import Optional, Tuple
from litellm import completion

from backend.config import settings
from backend.db.state import DB_PATH
from backend.pipeline.models import StructuredEvent, ExtractedDecision

logger = structlog.get_logger(__name__)

REASONING_KEYWORDS = {
    "because", "since", "instead of", "replace", "migrate", "avoid", "due to",
    "therefore", "thus", "reason", "fix", "issue"
}

def has_reasoning_language(text: str) -> bool:
    """Returns True if the text contains explicit reasoning language."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in REASONING_KEYWORDS)

async def extract_reasoning(event: StructuredEvent) -> Tuple[bool, Optional[ExtractedDecision]]:
    """
    If the event is a Git Commit with reasoning language, extracts the decision.
    Returns (has_reasoning, extracted_decision).
    """
    if event.event_type not in ("GIT_COMMIT", "MANUAL_NOTE"):
        return False, None
        
    message = event.metadata.get("message", "")
    if event.event_type == "GIT_COMMIT":
        if not has_reasoning_language(message):
            return False, None
            
    # Check for expiry tag
    expiry_match = re.search(r'#expires:(\d{4}-\d{2}-\d{2})', message)
    if expiry_match:
        event.metadata["expires_at"] = expiry_match.group(1)
        logger.info("Found technical debt expiry tag", expires_at=event.metadata["expires_at"])
    
    logger.info("Reasoning language or manual note detected, running LLM extraction", hash=event.metadata.get("hash"))
    
    prompt = f"""
    You are an architectural decision extractor.
    Analyze the following git commit and extract the explicit architectural or design decision made, and the context/reasoning behind it.
    Do not fabricate reasons. Only extract what is explicitly stated or strongly implied by the diff/message.
    
    Commit Details:
    {event.content}
    """
    
    try:
        response = completion(
            model=settings.app_llm_model,
            messages=[{"role": "user", "content": prompt}],
            api_base=settings.app_llm_endpoint,
            api_key=settings.app_llm_api_key,
            # We don't use max_tokens or streaming here to keep it simple, but litellm handles it
            timeout=30
        )
        
        extracted_text = response.choices[0].message.content
        
        decision = ExtractedDecision(
            decision="Extracted Decision", # In a full version, we'd use function calling to get a JSON struct
            context=extracted_text
        )
        
        return True, decision
        
    except Exception as e:
        logger.error("LLM Extraction failed", error=str(e))
        return False, None

async def log_nudge_if_needed(event: StructuredEvent):
    """
    If this is a high-signal file modification but we didn't find reasoning, log a nudge.
    """
    # Note: A real implementation would check if a manual note was added recently for this path.
    # For MVP, if a dependency/config file is modified directly (not via commit), we log a nudge.
    if event.event_type in ("FILE_MODIFIED", "FILE_CREATED"):
        if not event.path.endswith(".md"): # MD files are their own reasons
            try:
                from backend.db.state import has_recent_decision, add_nudge
                
                # Check if we already have a recent decision for this path
                if await has_recent_decision(event.path, hours=24):
                    logger.debug("Skipping nudge, recent decision found", path=event.path)
                    return
                    
                # High-signal check
                is_high_signal = any(x in event.path for x in ["package.json", "requirements.txt", "pyproject.toml", "docker-compose", ".env", "config"])
                # Could also check for module creation/deletion, which is structurally significant
                
                if is_high_signal:
                    await add_nudge(event.event_type, event.path)
                    logger.debug("Logged nudge for unreasoned high-signal file change", path=event.path)
            except Exception as e:
                logger.error("Failed to log nudge", error=str(e))
