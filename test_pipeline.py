import os
import asyncio
import structlog
from unittest.mock import patch
from datetime import datetime

from backend.config import settings
from backend.db.state import init_db
from backend.observer.queue import RawEvent
from backend.pipeline.processor import process_event
from backend.pipeline.state_manager import check_and_get_previous_state
from backend.pipeline.normalizer import normalize_event

logger = structlog.get_logger(__name__)

async def run_tests():
    settings.set_environment()
    await init_db()
    
    dataset_name = "test-dataset"
    
    # We will patch ingest_event to not actually run Cognee logic (which takes a long time)
    # but still return a data_id so the rest of the pipeline works.
    async def mock_ingest(event, dataset_name, node_set, content, old_data_id=None):
        logger.info("MOCK INGEST CALLED", path=event.path, node_set=node_set, old_data_id=old_data_id)
        return f"mock_id_{event.hash[:8]}"
        
    with patch("backend.pipeline.processor.ingest_event", side_effect=mock_ingest):
        
        print("\n--- Test 1: File Modify (No LLM, should just ingest) ---")
        # Create a dummy file
        with open("dummy_config.yml", "w") as f:
            f.write("port: 8080")
            
        evt1 = RawEvent(event_type="FILE_MODIFIED", path="dummy_config.yml", timestamp=datetime.now())
        res1 = await process_event(evt1, dataset_name)
        print(f"Result 1: {res1.dict()}")
        
        print("\n--- Test 2: File Modify Duplicate (Should be skipped) ---")
        res2 = await process_event(evt1, dataset_name)
        print(f"Result 2: {res2.dict()}")
        
        print("\n--- Test 3: File Modify Changed (Should forget old data_id) ---")
        with open("dummy_config.yml", "w") as f:
            f.write("port: 9000")
        evt3 = RawEvent(event_type="FILE_MODIFIED", path="dummy_config.yml", timestamp=datetime.now())
        res3 = await process_event(evt3, dataset_name)
        print(f"Result 3: {res3.dict()}")
        
        print("\n--- Test 4: Git Commit with Reasoning (LLM extraction) ---")
        # For this we need a real commit or we mock get_git_commit_info
        # We will mock the git info to avoid needing a real commit here
        with patch("backend.pipeline.normalizer.get_git_commit_info") as mock_git:
            mock_git.return_value = (
                "Update database schema because the old one caused deadlocks",
                " dummy_config.yml | 1 +"
            )
            evt4 = RawEvent(
                event_type="GIT_COMMIT", 
                path="fake_hash", 
                timestamp=datetime.now(), 
                metadata={"hash": "fake_hash"}
            )
            res4 = await process_event(evt4, dataset_name)
            print(f"Result 4: {res4.dict()}")
            
        print("\n--- Test 5: Git Commit without Reasoning (No LLM) ---")
        with patch("backend.pipeline.normalizer.get_git_commit_info") as mock_git:
            mock_git.return_value = (
                "Update formatting",
                " dummy_config.yml | 1 +"
            )
            evt5 = RawEvent(
                event_type="GIT_COMMIT", 
                path="fake_hash_2", 
                timestamp=datetime.now(), 
                metadata={"hash": "fake_hash_2"}
            )
            res5 = await process_event(evt5, dataset_name)
            print(f"Result 5: {res5.dict()}")

if __name__ == "__main__":
    asyncio.run(run_tests())
