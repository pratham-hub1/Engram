import os
import sys
import asyncio

os.environ["LLM_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["LLM_API_KEY"] = "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"
os.environ["OPENAI_BASE_URL"] = "https://integrate.api.nvidia.com/v1"
os.environ["LLM_ENDPOINT"] = "https://integrate.api.nvidia.com/v1"
# For litellm to recognize custom openai endpoint correctly, prefix the model with openai/
os.environ["LLM_MODEL"] = "openai/nvidia/nemotron-3-super-120b-a12b"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

try:
    import cognee
except ImportError:
    print("Cognee not installed.")
    sys.exit(1)

async def main():
    print("--- FOLLOW-UP SPIKE 1A (RETRY 2) ---")
    try:
        result1a = await cognee.remember(
            "test content spike 1a retry 2", 
            dataset_name="spike_test_1a_2", 
            node_set="commits", 
            self_improvement=False
        )
        print(f"Spike 1A return type: {type(result1a)}")
        print(f"Spike 1A return value: {result1a}")
    except Exception as e:
        print(f"Spike 1A failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
