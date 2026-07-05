import asyncio
from backend.db.state import get_indexing_status
from backend.config import settings

async def main():
    status = await get_indexing_status(settings.cognee_dataset_name)
    print(f"STATUS: {status}")

asyncio.run(main())
