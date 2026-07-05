import asyncio
from backend.config import settings
from backend.db.state import init_db
from backend.memory.orchestrator import query_decision, query_general, query_history

async def main():
    settings.set_environment()
    await init_db()
    
    print("=== Testing Memory Orchestrator ===")
    
    q1 = "Why are we using Cognee?"
    print(f"\nQuerying (Decision): {q1}")
    ans1 = await query_decision(q1)
    print(f"Answer:\n{ans1}")

    q2 = "What is the name of this project?"
    print(f"\nQuerying (General): {q2}")
    ans2 = await query_general(q2)
    print(f"Answer:\n{ans2}")

if __name__ == "__main__":
    asyncio.run(main())
