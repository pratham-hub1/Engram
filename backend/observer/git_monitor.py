import os
import time
import structlog
from pathlib import Path
from backend.observer.queue import RawEvent

logger = structlog.get_logger(__name__)

# To prevent processing the same commit multiple times (since watchdog might emit multiple events)
_last_processed_commit = None

def handle_git_logs_head(path: str, event_queue):
    """
    Parses .git/logs/HEAD and pushes a GIT_COMMIT event to the queue
    if a new commit is detected.
    """
    global _last_processed_commit
    
    try:
        if not os.path.exists(path):
            return
            
        with open(path, 'r', encoding='utf-8') as f:
            # Read all lines and get the last one
            lines = f.readlines()
            if not lines:
                return
            last_line = lines[-1].strip()
            
            # Format: old_hash new_hash Name <email> timestamp tz action: message
            parts = last_line.split('\t')
            if len(parts) < 2:
                return
                
            metadata_str = parts[0]
            action_str = parts[1]
            
            metadata_parts = metadata_str.split(' ')
            if len(metadata_parts) < 2:
                return
                
            new_hash = metadata_parts[1]
            
            # We only care if it's an actual commit, merge, or rebase 
            # (not just a checkout)
            if action_str.startswith("commit") or action_str.startswith("merge") or action_str.startswith("rebase"):
                if new_hash != _last_processed_commit:
                    _last_processed_commit = new_hash
                    
                    event = RawEvent(
                        event_type="GIT_COMMIT",
                        path=path,
                        timestamp=time.time(),
                        metadata={"hash": new_hash, "action": action_str}
                    )
                    
                    event_queue.push_event(event)
                    logger.info("Detected new git commit via logs/HEAD", hash=new_hash, action=action_str)
                    
    except Exception as e:
        logger.error("Failed to parse .git/logs/HEAD", error=str(e))
