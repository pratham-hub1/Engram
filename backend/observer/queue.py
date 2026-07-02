import asyncio
import time
import structlog
from dataclasses import dataclass
from typing import Dict, Any

logger = structlog.get_logger(__name__)

@dataclass
class RawEvent:
    event_type: str # "FILE_MODIFIED", "FILE_CREATED", "FILE_DELETED", "GIT_COMMIT"
    path: str
    timestamp: float
    metadata: Dict[str, Any] = None

class ObserverQueue:
    def __init__(self, debounce_seconds: int = 30):
        self.queue = asyncio.Queue()
        self.debounce_seconds = debounce_seconds
        
        # Debounce dictionary: path -> RawEvent
        self._pending_file_events = {}
        self._debounce_task = None
        
    def start(self):
        """Starts the background debouncer task."""
        if not self._debounce_task:
            self._debounce_task = asyncio.create_task(self._debounce_loop())
            
    async def stop(self):
        """Stops the background debouncer task."""
        if self._debounce_task:
            self._debounce_task.cancel()
            try:
                await self._debounce_task
            except asyncio.CancelledError:
                pass
            self._debounce_task = None

    def push_event(self, event: RawEvent):
        """Pushes an event into the queue. File events are debounced, git commits pass instantly."""
        if event.event_type == "GIT_COMMIT":
            # Git commits are instantly pushed
            logger.info("Pushing git commit to queue instantly", hash=event.metadata.get('hash', 'unknown'))
            self.queue.put_nowait(event)
        else:
            # File system events are debounced based on the path
            logger.debug("Debouncing file event", path=event.path, event_type=event.event_type)
            self._pending_file_events[event.path] = event
            
    async def _debounce_loop(self):
        """Periodically flushes file events that have passed the debounce window."""
        while True:
            await asyncio.sleep(5) # Check every 5 seconds
            
            now = time.time()
            flushed = []
            
            for path, event in list(self._pending_file_events.items()):
                if now - event.timestamp >= self.debounce_seconds:
                    flushed.append(path)
                    self.queue.put_nowait(event)
                    
            for path in flushed:
                del self._pending_file_events[path]
                
            if flushed:
                logger.info("Flushed debounced file events to queue", count=len(flushed))

# Global queue instance
event_queue = ObserverQueue()
