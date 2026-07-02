import contextlib
import structlog
from fastapi import FastAPI
from backend.config import settings

logger = structlog.get_logger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure environment requirements are set before anything initializes
    settings.set_environment()
    logger.info("Starting Memory AI backend", environment=settings.environment)
    
    # Initialize SQLite state database
    from backend.db.state import init_db
    await init_db()
    
    # Start Observer Service
    from backend.observer.watcher import observer_service
    observer_service.start()
    
    # Init Cognee connections here later
    yield
    
    # Stop Observer Service
    await observer_service.stop()
    logger.info("Shutting down Memory AI backend")

app = FastAPI(
    title="Memory AI",
    description="Local-first AI memory layer",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.port, reload=True)
