import asyncio
import cognee
from cognee.modules.search.types.SearchType import SearchType

async def run_query():
    query = "Provide a high-level summary of the project architecture and recent state."
    dataset_name = "engram_core"
    
    results = await cognee.search(
        query_text=query,
        query_type=SearchType.GRAPH_COMPLETION,
        system_prompt=None,
        datasets=[dataset_name]
    )
    
    print("RAW RESULTS:", results)
    
    formatted = []
    for r in results:
        print("TYPE OF R:", type(r))
        print("VALUE OF R:", r)
        
        if hasattr(r, "model_dump"):
            r_dict = r.model_dump()
            print("Pydantic dump:", r_dict)
            val = r_dict.get("search_result", str(r_dict))
            print("Pydantic search_result:", val)
            if isinstance(val, list):
                formatted.extend([str(v) for v in val])
            else:
                formatted.append(str(val))
        elif isinstance(r, dict):
            val = r.get("search_result", str(r))
            print("DICT SEARCH_RESULT:", val)
            if isinstance(val, list):
                formatted.extend([str(v) for v in val])
            else:
                formatted.append(str(val))
        elif hasattr(r, "answer"):
            print("HAS ANSWER:", r.answer)
            formatted.append(str(r.answer))
        elif hasattr(r, "text"):
            print("HAS TEXT:", r.text)
            formatted.append(str(r.text))
        else:
            print("FALLBACK:", str(r))
            formatted.append(str(r))
            
    print("\nFINAL FORMATTED:")
    print("\n\n".join(formatted))

if __name__ == "__main__":
    asyncio.run(run_query())
