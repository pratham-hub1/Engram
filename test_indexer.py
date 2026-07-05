import os
import asyncio
from backend.config import settings
from backend.db.state import init_db
from backend.memory.indexer import run_initial_indexing

async def main():
    settings.set_environment()
    await init_db()
    
    project_path = os.path.abspath(".")
    print(f"Running initial indexing for {project_path}")
    
    await run_initial_indexing(project_path)
    print("Done indexing")

if __name__ == "__main__":
    asyncio.run(main())
