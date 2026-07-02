import asyncio
import os
import sys

# Ensure cognee is available
try:
    import cognee
except ImportError:
    print("Cognee not installed.")
    sys.exit(1)

async def main():
    print("--- SPIKE 1 ---")
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["LLM_MODEL"] = "gemini-1.5-flash"
    
    if "GEMINI_API_KEY" in os.environ:
        os.environ["LLM_API_KEY"] = os.environ["GEMINI_API_KEY"]
    else:
        print("WARNING: GEMINI_API_KEY not found in environment, make sure LLM_API_KEY is set.")
    
    try:
        result1 = await cognee.remember(
            "spike 1 test content", 
            dataset_name="spike_test", 
            node_set="commits", 
            self_improvement=False, 
            run_in_background=True
        )
        print(f"Spike 1 return type: {type(result1)}")
        print(f"Spike 1 return value: {result1}")
    except Exception as e:
        print(f"Spike 1 failed: {e}")
    
    # Give background task time if it's running
    await asyncio.sleep(2)
    
    print("\n--- SPIKE 2 ---")
    try:
        result2a = await cognee.remember(
            ["spike2 item1", "spike2 item2"], 
            dataset_name="spike_test", 
            node_set="commits", 
            self_improvement=False
        )
        print(f"Spike 2a return type: {type(result2a)}")
        print(f"Spike 2a return value: {result2a}")
    except Exception as e:
        print(f"Spike 2a failed: {e}")
        
    try:
        result2b = await cognee.remember(
            ["spike2 decision1"], 
            dataset_name="spike_test", 
            node_set="decisions", 
            self_improvement=False
        )
        print(f"Spike 2b return type: {type(result2b)}")
        print(f"Spike 2b return value: {result2b}")
    except Exception as e:
        print(f"Spike 2b failed: {e}")
    
    print("\n--- SPIKE 3 ---")
    try:
        recall1 = await cognee.recall("spike2 item1", node_set="commits", query_type="vector")
        print(f"Recall from 'commits' (vector): {recall1}")
    except Exception as e:
        print(f"Spike 3 (commits) failed: {e}")
        
    try:
        recall2 = await cognee.recall("spike2 decision1", node_set="decisions", query_type="graph-completion")
        print(f"Recall from 'decisions' (graph-completion): {recall2}")
    except Exception as e:
        print(f"Spike 3 (decisions) failed: {e}")

    print("\n--- SPIKE 4 ---")
    try:
        if 'result2a' in locals() and result2a:
            data_id_to_forget = result2a if isinstance(result2a, str) else (result2a[0] if isinstance(result2a, list) else str(result2a))
            print(f"Attempting to forget data_id: {data_id_to_forget}")
            
            await cognee.forget(data_id=data_id_to_forget)
            print("Forget called successfully.")
            
            recall_after_forget = await cognee.recall("spike2 item1", node_set="commits", query_type="vector")
            print(f"Recall after forget: {recall_after_forget}")
        else:
            print("Could not obtain data_id to forget from Spike 2a.")
    except Exception as e:
        print(f"Spike 4 failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
