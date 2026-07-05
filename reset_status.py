import asyncio
from backend.db.state import set_indexing_status
from backend.config import settings

async def main():
    await set_indexing_status(settings.cognee_dataset_name, 'UNINDEXED')
    print("Reset status to UNINDEXED.")

asyncio.run(main())
