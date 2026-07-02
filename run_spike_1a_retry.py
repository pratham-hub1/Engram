import os
import sys
import asyncio

# Set environment variables BEFORE importing cognee
os.environ["LLM_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["LLM_API_KEY"] = "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"
os.environ["OPENAI_BASE_URL"] = "https://integrate.api.nvidia.com/v1"
os.environ["LLM_ENDPOINT"] = "https://integrate.api.nvidia.com/v1"
os.environ["LLM_MODEL"] = "nvidia/nemotron-3-super-120b-a12b"

try:
    import cognee
except ImportError:
    print("Cognee not installed.")
    sys.exit(1)

async def main():
    print("--- FOLLOW-UP SPIKE 1A (RETRY) ---")
    try:
        result1a = await cognee.remember(
            "test content spike 1a retry", 
            dataset_name="spike_test_1a", 
            node_set="commits", 
            self_improvement=False
        )
        print(f"Spike 1A return type: {type(result1a)}")
        print(f"Spike 1A return value: {result1a}")
    except Exception as e:
        print(f"Spike 1A failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
