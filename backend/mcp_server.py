from mcp.server.fastmcp import FastMCP
import structlog
from backend.memory.orchestrator import query_decision, query_general, query_history

logger = structlog.get_logger(__name__)

# Create the main MCP Server instance
mcp = FastMCP("engram-mcp")

@mcp.tool()
async def recall_context(query: str, intent: str = "general") -> str:
    """
    Retrieve deep project context and architectural knowledge.
    
    Args:
        query: The question or topic to search for (e.g. 'Why did we use PostgreSQL?')
        intent: The type of query. Must be 'decision' (for why/architecture), 'history' (for what changed), or 'general'.
    """
    logger.info("MCP Tool called: recall_context", query=query, intent=intent)
    try:
        if intent == "decision":
            return await query_decision(query)
        elif intent == "history":
            return await query_history(query)
        else:
            return await query_general(query)
    except Exception as e:
        logger.error("MCP recall_context failed", error=str(e))
        return f"Error retrieving context: {str(e)}"

@mcp.tool()
async def get_project_summary() -> str:
    """
    Retrieve a high-level summary of the project's current architecture and state.
    """
    logger.info("MCP Tool called: get_project_summary")
    try:
        # We can implement a specialized Orchestrator query for this, or use general.
        return await query_general("Summarize the current project architecture, key technologies, and main components.")
    except Exception as e:
        return f"Error retrieving summary: {str(e)}"

@mcp.tool()
async def get_recent_changes(days: int = 7) -> str:
    """
    Retrieve a timeline of recent architectural changes and commits.
    
    Args:
        days: Number of days to look back (default 7).
    """
    logger.info("MCP Tool called: get_recent_changes", days=days)
    try:
        return await query_history(f"What were the most significant file changes and commits in the last {days} days?")
    except Exception as e:
        return f"Error retrieving changes: {str(e)}"

@mcp.tool()
async def add_decision(text: str) -> str:
    """
    Record an architectural decision or manual note.
    Bypasses the observer and enters the memory pipeline directly.
    
    Args:
        text: The architectural decision or note to record.
    """
    logger.info("MCP Tool called: add_decision")
    try:
        import hashlib
        from backend.pipeline.processor import process_event
        from backend.pipeline.models import StructuredEvent
        from backend.config import settings
        
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        event = StructuredEvent(
            event_type="MANUAL_NOTE",
            path="manual_note", # Pseudo-path for manual notes
            content=text,
            hash=content_hash,
            metadata={"message": text, "hash": content_hash, "source": "mcp"}
        )
        
        result = await process_event(event, settings.cognee_dataset_name)
        
        if result.success:
            return f"Decision captured successfully. Data ID: {result.data_id}"
        else:
            return "Failed to capture decision."
    except Exception as e:
        return f"Error capturing decision: {str(e)}"
