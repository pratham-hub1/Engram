import contextlib
import structlog
import asyncio
from fastapi import FastAPI
from backend.config import settings

logger = structlog.get_logger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure environment requirements are set before anything initializes
    settings.set_environment()
    logger.info("Starting Engram backend", environment=settings.environment)
    
    # Initialize SQLite state database
    from backend.db.state import init_db
    await init_db()
    
    # Initialize Cognee Local API
    import cognee
    
    # Point Cognee to the Decoupled Sidecar Gateway (Port 5001)
    cognee.config.set_llm_config({
        "llm_provider": "openai",
        "llm_model": "gpt-4o", # Dummy model for sidecar translation
        "llm_endpoint": "http://127.0.0.1:5001/v1",
        "llm_api_key": settings.cognee_llm_api_key
    })
    
    cognee.config.set_embedding_config({
        "embedding_provider": "openai_compatible",
        "embedding_model": "text-embedding-3-large", # Dummy model for sidecar translation
        "embedding_endpoint": "http://127.0.0.1:5001/v1",
        "embedding_api_key": settings.cognee_embedding_api_key
    })
    
    from backend.observer.watcher import observer_service, event_queue
    from backend.pipeline.processor import process_event
    dataset_name = settings.cognee_dataset_name
    
    async def consume_events():
        while True:
            try:
                event = await event_queue.queue.get()
                await process_event(event, dataset_name)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Pipeline processor error", error=str(e))
                
    pipeline_task = asyncio.create_task(consume_events())
    
    async def scheduled_dream_cycle():
        from backend.memory.cognee_client import improve_dataset
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
            try:
                logger.info("Running scheduled Dream Cycle (improve_dataset)")
                await improve_dataset(dataset_name)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Scheduled Dream Cycle failed", error=str(e))
                
    dream_task = asyncio.create_task(scheduled_dream_cycle())
    
    # Start Observer Service
    observer_service.start()
    
    # Run Initial Backfill if Database is empty
    from backend.db.state import get_indexing_status, set_indexing_status
    status = await get_indexing_status(dataset_name)
    if status == 'UNINDEXED':
        logger.info("Database is UNINDEXED. Running initial auto-seeder...")
        await set_indexing_status(dataset_name, 'INDEXING')
        
        import os
        import time
        from backend.observer.queue import RawEvent
        from backend.observer.filters import is_ignored
        
        # 1. Backfill explicitly specified core docs
        core_docs = ["README.md", "ARCHITECTURE.md", "CODEBASE_MEMORY.md", "PRODUCT_SPEC.md"]
        for doc in core_docs:
            if os.path.exists(doc):
                event_queue.push_event(RawEvent(event_type="FILE_MODIFIED", path=doc, timestamp=time.time()))
                
        # 2. Backfill backend files
        for root, dirs, filenames in os.walk("backend"):
            for filename in filenames:
                path = os.path.join(root, filename)
                rel_path = os.path.relpath(path, start=".").replace("\\", "/")
                if not is_ignored(rel_path):
                    event_queue.push_event(RawEvent(event_type="FILE_MODIFIED", path=rel_path, timestamp=time.time()))
                    
        logger.info("Initial backfill events pushed to event queue.")
        await set_indexing_status(dataset_name, 'COMPLETED')
        
    yield
    
    # Stop Pipeline, Observer, and Dream Cycle
    pipeline_task.cancel()
    dream_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await pipeline_task
        await dream_task
    await observer_service.stop()
    
    logger.info("Shutting down Engram backend")

app = FastAPI(
    title="Engram",
    description="Local-first AI memory layer",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.routes import router as api_router
app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.port, reload=True)