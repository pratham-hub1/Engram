import uuid
from typing import List, Union
import cognee
from structlog import get_logger

logger = get_logger(__name__)

from cognee.tasks.ingestion.data_item import DataItem

async def remember_event(content: Union[str, List[str]], dataset_name: str, data_id: str = None):
    """
    Ingests content into Cognee Cloud.
    If data_id is provided, wraps content in a deterministic DataItem.
    """
    logger.info("Calling cognee.remember", dataset_name=dataset_name)
    try:
        if data_id and isinstance(content, str):
            # Deterministic injection
            data_uuid = uuid.UUID(data_id) if isinstance(data_id, str) else data_id
            payload = DataItem(data_id=data_uuid, data=content)
        else:
            payload = content

        result = await cognee.remember(
            data=payload,
            dataset_name=dataset_name,
            self_improvement=False,
            run_in_background=False
        )
        logger.info("Cognee remember completed", status=getattr(result, "status", "unknown"))
        return result
    except Exception as e:
        logger.error("Cognee remember failed", error=str(e))
        raise

async def forget_event(data_id_str: str, dataset_name: str = "engram_core") -> None:
    """
    Safely deletes a node by parsing the string to uuid.UUID.
    """
    try:
        data_uuid = uuid.UUID(data_id_str)
        logger.info("Calling cognee.forget", data_id=data_id_str, dataset=dataset_name)
        await cognee.forget(data_id=data_uuid, dataset=dataset_name)
    except ValueError:
        logger.warning("Invalid UUID format for forget", data_id=data_id_str)
    except Exception as e:
        logger.error("Cognee forget failed", data_id=data_id_str, error=str(e))

async def improve_dataset(dataset_name: str) -> None:
    """
    Triggers the Cloud cognee.improve() task.
    """
    logger.info("Starting cognee.improve", dataset_name=dataset_name)
    try:
        await cognee.improve(dataset_name)
        logger.info("Cognee improve completed", dataset_name=dataset_name)
    except Exception as e:
        logger.error("Cognee improve failed", dataset_name=dataset_name, error=str(e))

async def recall_memory(query: str, dataset_name: str, query_type: str = "GRAPH_COMPLETION", system_prompt: str = None) -> str:
    """
    Exposes cognee.search for Phase 5 orchestrator.
    """
    logger.info("Calling cognee.search", query=query, dataset_name=dataset_name, query_type=query_type)
    try:
        from cognee.modules.search.types.SearchType import SearchType
        
        # Parse string query_type into SearchType Enum
        search_enum = getattr(SearchType, query_type, SearchType.GRAPH_COMPLETION)
        
        # cognee.search returns a list of SearchResult objects
        results = await cognee.search(
            query_text=query,
            query_type=search_enum,
            system_prompt=system_prompt,
            datasets=[dataset_name]
        )
        
        # We need to extract the answer from the results
        # A SearchResult object typically has an answer or text field, or we can just stringify it
        # For a clean answer, we look for 'answer', 'text', or just return the whole stringified list if not simple
        if not results:
            return "No information found."
            
        formatted = []
        for r in results:
            if isinstance(r, dict):
                # .get() safely extracts the text, or falls back to stringifying 
                # the whole object if 'search_result' is missing
                val = r.get("search_result", str(r))
                if isinstance(val, list):
                    formatted.extend([str(v) for v in val])
                else:
                    formatted.append(str(val))
            elif hasattr(r, "answer"):
                formatted.append(str(r.answer))
            elif hasattr(r, "text"):
                formatted.append(str(r.text))
            else:
                formatted.append(str(r))
                
        return "\n\n".join(formatted)
        
    except Exception as e:
        logger.error("Cognee search failed", error=str(e))
        return ""
