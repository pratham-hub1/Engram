import time
import os
import structlog
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from backend.observer.filters import is_ignored, is_high_signal
from backend.observer.git_monitor import handle_git_logs_head
from backend.observer.queue import event_queue, RawEvent

logger = structlog.get_logger(__name__)

class MemoryAIEventHandler(FileSystemEventHandler):
    """
    Handles raw file system events, filters them, and pushes them to the queue.
    """
    def _process_event(self, event: FileSystemEvent, event_type: str):
        if event.is_directory:
            # We care about directory creation/deletion for structural mapping,
            # but usually it's noisy. The spec says "Directory/file creation or deletion".
            # We'll allow it if it passes is_ignored.
            pass
            
        path = event.src_path
        
        # Git Commit detection (Special Case)
        # We explicitly check for .git/logs/HEAD modifications
        # We need to normalize paths for Windows/Linux
        path_obj = Path(path)
        if len(path_obj.parts) >= 3 and path_obj.parts[-3:] == (".git", "logs", "HEAD"):
            if event_type == "FILE_MODIFIED":
                handle_git_logs_head(path, event_queue)
            return

        # General filtering
        if is_ignored(path):
            return
            
        if event_type in ("FILE_CREATED", "FILE_DELETED") or is_high_signal(path):
            raw_event = RawEvent(
                event_type=event_type,
                path=path,
                timestamp=time.time()
            )
            event_queue.push_event(raw_event)

    def on_created(self, event: FileSystemEvent):
        self._process_event(event, "FILE_CREATED")

    def on_deleted(self, event: FileSystemEvent):
        self._process_event(event, "FILE_DELETED")

    def on_modified(self, event: FileSystemEvent):
        self._process_event(event, "FILE_MODIFIED")

    def on_moved(self, event: FileSystemEvent):
        # We treat moves as a deletion of the old path and creation of the new path
        self._process_event(event, "FILE_DELETED")
        
        # Create a mock event for the destination
        class MockEvent:
            is_directory = event.is_directory
            src_path = event.dest_path
            
        self._process_event(MockEvent(), "FILE_CREATED")

class ObserverService:
    def __init__(self, watch_dir: str = "."):
        self.watch_dir = watch_dir
        self.observer = Observer()
        self.handler = MemoryAIEventHandler()
        
    def start(self):
        """Starts the watchdog observer and the debouncer queue."""
        logger.info("Starting Observer Service", watch_dir=self.watch_dir)
        event_queue.start()
        
        self.observer.schedule(self.handler, self.watch_dir, recursive=True)
        self.observer.start()
        
    async def stop(self):
        """Stops the watchdog observer and the debouncer queue."""
        logger.info("Stopping Observer Service")
        self.observer.stop()
        self.observer.join()
        await event_queue.stop()

# Global observer instance
observer_service = ObserverService()
