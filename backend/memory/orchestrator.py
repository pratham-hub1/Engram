import structlog
from backend.config import settings
from backend.memory.cognee_client import recall_memory

logger = structlog.get_logger(__name__)

async def query_decision(question: str) -> str:
    """
    Query strictly for architectural decisions and "why" questions.
    Uses GRAPH_COMPLETION with a zero-hallucination constraint.
    """
    system_prompt = (
        "You are a machine that outputs ONLY valid JSON. Explain WHY architectural decisions were made based strictly on the provided context graph. "
        "CRITICAL: You MUST output ONLY a valid JSON ARRAY. No preamble, no markdown blocks, no ```json tags. "
        "Every object in the array MUST have exactly these string keys: 'decision', 'reason', 'source', 'confidence'. "
        "If you output any text other than the JSON array, the system will crash. "
        "Example output: [{\"decision\": \"...\", \"reason\": \"...\", \"source\": \"...\", \"confidence\": \"Confirmed\"}]"
    )
    
    logger.info("Executing decision query", question=question)
    
    return await recall_memory(
        query=question,
        dataset_name=settings.cognee_dataset_name,
        query_type="GRAPH_COMPLETION",
        system_prompt=system_prompt
    )

async def query_history(question: str) -> str:
    """
    Query for historical timelines, e.g. "What changed last week?"
    """
    system_prompt = (
        "You are a strict JSON data formatter for project history. Answer based on the provided commit and file changes context. "
        "You MUST output a valid JSON ARRAY containing historical events. "
        "Do NOT output any preamble, markdown formatting, or plain text strings. ONLY output a valid JSON array. "
        "Every object in the array MUST have exactly two keys: 'date' (string) and 'event' (string). "
        "Example:\n[\n  {\"date\": \"2024-06-28\", \"event\": \"Evaluated Flat RAG...\"}\n]\n"
    )
    
    logger.info("Executing history query", question=question)
    
    return await recall_memory(
        query=question,
        dataset_name=settings.cognee_dataset_name,
        query_type="TEMPORAL",
        system_prompt=system_prompt
    )

async def query_general(question: str) -> str:
    """
    Standard open-ended query.
    """
    system_prompt = (
        "You are a project intelligence assistant. Answer the user's question using the context graph. "
        "You MUST return a raw JSON object with the exact keys: "
        "'answer', 'reasoning_path'. "
        "'reasoning_path' must be an array of objects explicitly mapping the graph traversal path you took. "
        "Each object must have 'type' (string, e.g., 'commit', 'document', 'component', 'decision') and 'name' (string). "
        "Example: {\"answer\": \"...\", \"reasoning_path\": [{\"type\": \"commit\", \"name\": \"Commit #34\"}, {\"type\": \"document\", \"name\": \"ARCHITECTURE.md\"}]}\n"
        "DO NOT wrap the response in markdown blocks like ```json."
    )
    
    logger.info("Executing general query", question=question)
    
    return await recall_memory(
        query=question,
        dataset_name=settings.cognee_dataset_name,
        query_type="GRAPH_COMPLETION",
        system_prompt=system_prompt
    )

async def query_onboarding() -> str:
    """
    Executes a heavy graph search to build a high-level project onboarding summary.
    """
    import os
    try:
        backend_files = sum([len(f) for r, d, f in os.walk('backend') if 'node_modules' not in r and '__pycache__' not in r])
        frontend_files = sum([len(f) for r, d, f in os.walk('frontend') if 'node_modules' not in r and '__pycache__' not in r])
        stats = f"Currently, there are roughly {backend_files} backend files and {frontend_files} frontend files."
    except Exception:
        stats = ""

    system_prompt = (
        "You are a Senior Engineer acting as an expert onboarding mentor for a brand new developer joining the team today. "
        "Analyze the entire project architecture and recent changes. Write highly detailed, empathetic, and comprehensive summaries "
        "that explain WHAT was changed, WHY it matters, and HOW the architecture works. "
        f"Hard Metrics to include: {stats} "
        "You MUST return a raw JSON object with the exact keys: "
        "'project_scale_and_layout' (array of strings: concise bullet points explaining the scale of the codebase, directories, and how pieces fit together), "
        "'current_architecture' (array of strings: concise bullet points explaining the system's data flow and components), "
        "'last_change' (object with 'time' and 'quote' strings explaining the most recent meaningful change in deep context), "
        "'current_focus' (array of objects: each object must have 'title' (string) and 'details' (array of strings)), "
        "'welcome_message' (string: The overarching goal and elevator pitch of the software), "
        "'blocker' (array of strings: concise bullet points explaining any technical blockers), "
        "'next_task' (array of strings: concise bullet points of exactly what the team is doing next), "
        "'onboarding_time_mins' (integer). "
        "DO NOT wrap the response in markdown blocks like ```json."
    )
    
    logger.info("Executing onboarding query")
    
    return await recall_memory(
        query="Analyze the full project architecture, recent decisions, and current focus.",
        dataset_name=settings.cognee_dataset_name,
        query_type="GRAPH_COMPLETION",
        system_prompt=system_prompt
    )
