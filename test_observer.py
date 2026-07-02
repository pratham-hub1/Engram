import asyncio
import os
import shutil
from backend.observer.watcher import observer_service
from backend.observer.queue import event_queue
import subprocess

async def test_observer():
    print("Starting Observer...")
    event_queue.debounce_seconds = 5
    observer_service.start()
    
    print("\n--- Test 1: Noisy file (should be ignored) ---")
    with open(".venv/test_noise.txt", "w") as f:
        f.write("noise")
    await asyncio.sleep(1) # Wait for watchdog
    
    print("\n--- Test 2: Source code file (should be ignored for modification) ---")
    with open("backend/main.py", "a") as f:
        f.write("\n# test comment")
    await asyncio.sleep(1)
    
    print("\n--- Test 3: High-signal file (should be debounced) ---")
    with open("requirements.txt", "a") as f:
        f.write("\n# test dep")
    await asyncio.sleep(1)
    print(f"Queue size before debounce window: {event_queue.queue.qsize()}")
    
    print("\n--- Test 4: Git commit (should be instant) ---")
    subprocess.run(["git", "add", "requirements.txt", "backend/main.py"])
    subprocess.run(["git", "commit", "-m", "Test commit for observer"])
    await asyncio.sleep(1)
    print(f"Queue size after git commit: {event_queue.queue.qsize()}")
    
    # Process instantly available items
    while not event_queue.queue.empty():
        item = await event_queue.queue.get()
        print(f"POPPED FROM QUEUE: {item.event_type} - {item.path}")
        
    print("\nWaiting 6 seconds for debounce to flush...")
    await asyncio.sleep(6)
    
    print(f"Queue size after debounce: {event_queue.queue.qsize()}")
    while not event_queue.queue.empty():
        item = await event_queue.queue.get()
        print(f"POPPED FROM QUEUE: {item.event_type} - {item.path}")
        
    await observer_service.stop()
    print("Observer stopped.")

if __name__ == "__main__":
    # Ensure .venv exists for test 1
    os.makedirs(".venv", exist_ok=True)
    asyncio.run(test_observer())
