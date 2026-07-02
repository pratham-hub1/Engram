import asyncio
import os
import sys
import inspect

os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

try:
    import cognee
    from cognee.modules.search.types import SearchType
except ImportError:
    print("Cognee not installed.")
    sys.exit(1)

NVIDIA_KEY = "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"
BASE_URL = "https://integrate.api.nvidia.com/v1"

def configure_cognee(embed_model="nvidia/nv-embedqa-e5-v5"):
    # Prefixing with openai/ to satisfy litellm for custom endpoints
    cognee.config.set_llm_config({
        "llm_provider": "openai",
        "llm_model": "openai/nvidia/nemotron-3-super-120b-a12b",
        "llm_endpoint": BASE_URL,
        "llm_api_key": NVIDIA_KEY
    })
    
    cognee.config.set_embedding_config({
        "embedding_provider": "openai",
        "embedding_model": f"openai/{embed_model}",
        "embedding_endpoint": BASE_URL,
        "embedding_api_key": NVIDIA_KEY
    })

async def main():
    print("--- FINAL SPIKE A ---")
    embed_models = [
        "nvidia/nv-embedqa-e5-v5",
        "nvidia/nv-embed-v1",
        "baai/bge-m3"
    ]
    
    result_a = None
    captured_dataset_id = None
    
    for embed_model in embed_models:
        print(f"\nTrying embedding model: {embed_model}")
        configure_cognee(embed_model)
        try:
            result_a = await cognee.remember(
                "test content spike A final", 
                dataset_name="spike_final_ds", 
                self_improvement=False
            )
            print(f"Success with {embed_model}!")
            print(f"Return type: {type(result_a)}")
            print(f"Return value: {result_a}")
            break
        except Exception as e:
            err_msg = str(e)
            print(f"Failed with {embed_model}: {err_msg[:200]}...")
            if "404" not in err_msg and "422" not in err_msg and "NotFoundError" not in err_msg:
                print("Unexpected error, continuing loop anyway.")

    if not result_a:
        print("Spike A completely failed.")
        return

    # Extract dataset_id
    if isinstance(result_a, list) and len(result_a) > 0:
        item = result_a[0]
        if hasattr(item, 'dataset_id'):
            captured_dataset_id = item.dataset_id
    else:
        if hasattr(result_a, 'dataset_id'):
            captured_dataset_id = result_a.dataset_id
            
    if not captured_dataset_id:
        print("Could not extract dataset_id from Spike A result.")
        return
        
    print(f"\nCaptured dataset_id: {captured_dataset_id}")

    print("\n--- FINAL SPIKE B ---")
    try:
        recall_vec = await cognee.recall(
            "test content", 
            datasets=["spike_final_ds"], 
            query_type=SearchType.VECTOR
        )
        print(f"Recall (VECTOR) return type: {type(recall_vec)}")
        print(f"Recall (VECTOR) length: {len(recall_vec) if isinstance(recall_vec, list) else 'N/A'}")
    except Exception as e:
        print(f"Recall (VECTOR) failed: {e}")

    try:
        recall_graph = await cognee.recall(
            "test content", 
            datasets=["spike_final_ds"], 
            query_type=SearchType.GRAPH_COMPLETION
        )
        print(f"Recall (GRAPH_COMPLETION) return type: {type(recall_graph)}")
        print(f"Recall (GRAPH_COMPLETION) length: {len(recall_graph) if isinstance(recall_graph, list) else 'N/A'}")
    except Exception as e:
        print(f"Recall (GRAPH_COMPLETION) failed: {e}")

    print("\n--- FINAL SPIKE C ---")
    try:
        print("Testing recall with scope='document'...")
        recall_scope = await cognee.recall(
            "test content", 
            datasets=["spike_final_ds"], 
            query_type=SearchType.VECTOR,
            scope="document"
        )
        print(f"Recall with scope successful, returned {len(recall_scope)} items.")
    except Exception as e:
        print(f"Recall with scope='document' failed: {e}")

    print("\n--- FINAL SPIKE D ---")
    try:
        print(f"Attempting to forget dataset_id: {captured_dataset_id}")
        await cognee.forget(dataset_id=captured_dataset_id)
        print("Forget called successfully.")
        
        # Verify it's forgotten
        recall_after = await cognee.recall(
            "test content", 
            datasets=["spike_final_ds"], 
            query_type=SearchType.VECTOR
        )
        print(f"Recall after forget length: {len(recall_after) if isinstance(recall_after, list) else 'N/A'}")
    except Exception as e:
        print(f"Forget failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
