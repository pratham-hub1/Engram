import os
import asyncio
from pathlib import Path
from structlog import get_logger
from backend.db.state import get_indexing_status, set_indexing_status
from backend.memory.cognee_client import remember_event, improve_dataset
from backend.config import settings

logger = get_logger(__name__)

async def run_initial_indexing(project_path: str):
    """
    Runs once per project to backfill historical knowledge.
    Extracts core config files and last 50 commits.
    """
    dataset_name = settings.cognee_dataset_name
    # Architecturally robust state check
    indexing_status = await get_indexing_status(dataset_name)
    
    if indexing_status == 'COMPLETED':
        logger.info("Project already indexed (status COMPLETED), skipping initial backfill", dataset=dataset_name)
        return
    elif indexing_status == 'INDEXING':
        logger.warning("Project crashed mid-indexing. Cleaning up graph and restarting", dataset=dataset_name)
        try:
            import cognee
            await cognee.prune.prune_data()
        except Exception as e:
            logger.error("Failed to prune data on restart", error=str(e))
    
    await set_indexing_status(dataset_name, 'INDEXING')
    logger.info("Starting initial indexing backfill", dataset=dataset_name, project_path=project_path)
    
    payloads = []
    
    # We need to import DataItem and uuid to inject deterministic IDs during backfill
    from cognee.tasks.ingestion.data_item import DataItem
    import uuid

    # 1. Dynamic Context Sweeper & Code Topology Extractor
    from backend.observer.filters import is_high_signal, is_ignored
    import re
    
    def extract_code_topology(content: str, file_ext: str) -> str:
        """Extracts lightweight AST topology (classes/functions) from raw code."""
        names = []
        if file_ext == '.py':
            for match in re.finditer(r'^\s*(?:async\s+)?(class|def)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE):
                names.append(f"{match.group(1)} {match.group(2)}")
        elif file_ext in ('.js', '.jsx', '.ts', '.tsx'):
            for match in re.finditer(r'^\s*(?:export\s+)?(?:default\s+)?(class|function)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE):
                names.append(f"{match.group(1)} {match.group(2)}")
            for match in re.finditer(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>', content):
                names.append(f"function {match.group(1)}")
        
        if not names:
            return ""
        return "Topology Map:\n- " + "\n- ".join(names)

    project_dir = Path(project_path)
    for filepath in project_dir.rglob("*"):
        if not filepath.is_file():
            continue
            
        rel_path = str(filepath.relative_to(project_dir))
        
        # Skip noisy/ignored files
        if is_ignored(rel_path):
            continue
            
        try:
            content = filepath.read_text(encoding="utf-8")
            
            # Case A: High-Signal Documentation / Configs
            if is_high_signal(rel_path):
                semantic_content = (
                    f"Project File: {rel_path}\n"
                    f"Type: Documentation/Config\n"
                    f"Content:\n{content}"
                )
                deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, rel_path)
                payloads.append(DataItem(data_id=deterministic_id, data=semantic_content))
                logger.debug("Indexed high-signal file", file=rel_path)
                
            # Case B: Code Topology Extraction
            elif filepath.suffix in ('.py', '.js', '.jsx', '.ts', '.tsx'):
                topology = extract_code_topology(content, filepath.suffix)
                if topology:
                    semantic_content = (
                        f"Project File: {rel_path}\n"
                        f"Type: Code Topology\n"
                        f"{topology}"
                    )
                    deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, rel_path)
                    payloads.append(DataItem(data_id=deterministic_id, data=semantic_content))
                    logger.debug("Indexed code topology", file=rel_path)
                    
        except Exception as e:
            logger.debug("Skipping unreadable file during indexing", file=rel_path)

    # 2. Backfill Commits (last 50)
    # Using a simple git subprocess command to get the last 50 commit hashes
    try:
        import subprocess
        result = subprocess.run(
            ["git", "-C", project_path, "log", "-n", "50", "--format=%H"],
            capture_output=True,
            text=True,
            check=True
        )
        hashes = [h.strip() for h in result.stdout.splitlines() if h.strip()]
        
        for commit_hash in hashes:
            # We need to get the message and stats for each
            commit_info = subprocess.run(
                ["git", "-C", project_path, "show", "-s", "--format=%B", commit_hash],
                capture_output=True,
                text=True
            )
            stats_info = subprocess.run(
                ["git", "-C", project_path, "show", "--stat", "--oneline", commit_hash],
                capture_output=True,
                text=True
            )
            
            message = commit_info.stdout.strip()
            diff = stats_info.stdout.strip()
            
            semantic_content = (
                f"Git Commit: {commit_hash}\n"
                f"Message: {message}\n"
                f"Changes:\n{diff}"
            )
            commit_id = uuid.uuid5(uuid.NAMESPACE_URL, commit_hash)
            payloads.append(DataItem(data_id=commit_id, data=semantic_content))
            
        logger.info("Extracted recent commits for indexing", count=len(hashes))
        
    except Exception as e:
        logger.warning("Failed to extract git history during indexing", error=str(e))

    # 3. Bulk Ingest (Natural Backpressure)
    if payloads:
        logger.info("Starting backpressure ingestion in background", count=len(payloads))
        
        async def process_batches():
            try:
                # Gentle pacing for the proxy server
                BATCH_SIZE = 5
                for i in range(0, len(payloads), BATCH_SIZE):
                    batch = payloads[i:i+BATCH_SIZE]
                    logger.info("Processing ingestion batch", batch_index=i//BATCH_SIZE + 1, total_batches=(len(payloads)+BATCH_SIZE-1)//BATCH_SIZE)
                    
                    # 1. Ingest the raw batch
                    await remember_event(batch, dataset_name)
                    
                # 2. Trigger graph extraction ONLY ONCE after all batches complete!
                logger.info("All batches ingested, triggering extraction (Dream Cycle)")
                await improve_dataset(dataset_name)
                
                # Mark as done only after all batches and extraction successfully finish
                await set_indexing_status(dataset_name, 'COMPLETED')
                logger.info("Initial indexing complete", dataset=dataset_name)
            except Exception as e:
                await set_indexing_status(dataset_name, 'UNINDEXED') # Allow retry
                logger.error("Initial indexing failed during batch ingestion", error=str(e))
                
        # Run it entirely in the background so the server boots instantly and UI never hangs
        asyncio.create_task(process_batches())
    else:
        logger.info("No initial data found to index")
        await set_indexing_status(dataset_name, 'COMPLETED')
