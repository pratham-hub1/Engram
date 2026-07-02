import asyncio
import os
import sys
import inspect

try:
    import cognee
except ImportError:
    print("Cognee not installed.")
    sys.exit(1)

async def main():
    print("--- Configuring LLM ---")
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "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"
    os.environ["LLM_API_KEY"] = "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"
    os.environ["OPENAI_BASE_URL"] = "https://integrate.api.nvidia.com/v1"
    os.environ["LLM_ENDPOINT"] = "https://integrate.api.nvidia.com/v1"
    os.environ["LLM_MODEL"] = "nvidia/nemotron-3-super-120b-a12b"
    
    print("--- FOLLOW-UP SPIKE 1A ---")
    try:
        result1a = await cognee.remember(
            "test content spike 1a", 
            dataset_name="spike_test_1a", 
            node_set="commits", 
            self_improvement=False
        )
        print(f"Spike 1A return type: {type(result1a)}")
        print(f"Spike 1A return value: {result1a}")
        if isinstance(result1a, list):
            for i, item in enumerate(result1a):
                print(f"  Item {i}: {type(item)} = {item}")
    except Exception as e:
        print(f"Spike 1A failed: {e}")

    print("\n--- FOLLOW-UP SPIKE 1B ---")
    try:
        # Use the dataset_id from the previous failed run
        ds_id = "ac83ab1e-0888-5778-95b0-7b94e20c64c3"
        print(f"Attempting to forget dataset_id: {ds_id}")
        await cognee.forget(dataset_id=ds_id)
        print("Forget called successfully.")
    except Exception as e:
        print(f"Spike 1B failed: {e}")

    print("\n--- FOLLOW-UP SPIKE 3A ---")
    try:
        print("Signature of cognee.recall:")
        print(inspect.signature(cognee.recall))
    except Exception as e:
        print(f"Could not print signature: {e}")
        
    try:
        print("\nTesting recall with query_type='vector'...")
        recall_vec = await cognee.recall("test query", query_type="vector")
        print(f"Recall vector successful. Type: {type(recall_vec)}, length: {len(recall_vec) if isinstance(recall_vec, list) else 'N/A'}")
    except Exception as e:
        print(f"Recall vector failed: {e}")
        
    try:
        print("\nTesting recall with query_type='graph-completion'...")
        recall_graph = await cognee.recall("test query", query_type="graph-completion")
        print(f"Recall graph-completion successful. Type: {type(recall_graph)}, length: {len(recall_graph) if isinstance(recall_graph, list) else 'N/A'}")
    except Exception as e:
        print(f"Recall graph-completion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
