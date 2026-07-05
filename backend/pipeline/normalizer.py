import os
import re
import hashlib
import subprocess
import structlog
from pathlib import Path

from backend.observer.queue import RawEvent
from backend.pipeline.models import StructuredEvent
from backend.observer.filters import is_high_signal
import asyncio

logger = structlog.get_logger(__name__)

def get_file_content(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.warning("Could not read file content", path=path, error=str(e))
        return ""

def get_git_commit_info(hash: str) -> tuple[str, str]:
    """Returns (commit_message, diff_stat)"""
    try:
        # Get commit message
        msg_result = subprocess.run(
            ["git", "show", "-s", "--format=%B", hash],
            capture_output=True, text=True, check=True
        )
        message = msg_result.stdout.strip()
        
        # Get diff stat (files changed) instead of full noisy diff
        stat_result = subprocess.run(
            ["git", "show", "--stat", "--oneline", hash],
            capture_output=True, text=True, check=True
        )
        # Skip the first line which is just the hash + subject
        stat_lines = stat_result.stdout.strip().split('\n')[1:]
        stat = '\n'.join(stat_lines)
        
        return message, stat
    except Exception as e:
        logger.error("Failed to extract git commit info", hash=hash, error=str(e))
        return "", ""

def get_git_commit_files(hash: str) -> list[str]:
    """Returns a list of files modified in the commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", hash],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except Exception:
        return []

def extract_dependencies(file_path: str, content: str) -> str:
    """Extracts imports/requires using regex to build structural edges."""
    ext = os.path.splitext(file_path)[1].lower()
    deps = set()
    
    if ext == ".py":
        # Match 'import X' or 'from X import Y'
        matches = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
        deps.update(matches)
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        # Match 'import X from "Y"' or 'require("Y")'
        matches = re.findall(r'(?:import.*?from\s+[\'"](.*?)[\'"]|require\([\'"](.*?)[\'"]\))', content)
        for m in matches:
            deps.add(m[0] if m[0] else m[1])
            
    if not deps:
        return ""
    return f"File {file_path} imports: {', '.join(deps)}"

async def normalize_event(raw: RawEvent) -> StructuredEvent:
    """
    Converts a RawEvent into a StructuredEvent with semantic context and content hashing.
    """
    metadata = raw.metadata or {}
    
    if raw.event_type == "GIT_COMMIT":
        commit_hash = metadata.get("hash", "")
        message, stat = get_git_commit_info(commit_hash)
        
        # AST Matrix Vision Extraction
        files_changed = get_git_commit_files(commit_hash)
        ast_context = []
        for file_path in files_changed:
            if os.path.exists(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in (".py", ".js", ".ts", ".jsx", ".tsx"):
                    content = await asyncio.to_thread(get_file_content, file_path)
                    deps = extract_dependencies(file_path, content)
                    if deps:
                        ast_context.append(deps)
                        
        ast_string = "\n".join(ast_context) if ast_context else "No structural dependencies extracted."
        
        # Semantic formatting for Cognee
        semantic_content = (
            f"Git Commit: {commit_hash}\n"
            f"Message: {message}\n"
            f"Changes:\n{stat}\n"
            f"Structural Dependencies (Matrix Vision):\n{ast_string}"
        )
        
        content_hash = hashlib.sha256(commit_hash.encode()).hexdigest()
        
        return StructuredEvent(
            event_type=raw.event_type,
            path=commit_hash, # For commits, the 'path' is the hash
            content=semantic_content,
            hash=content_hash,
            metadata={
                "hash": commit_hash,
                "message": message,
                "timestamp": raw.timestamp
            }
        )
        
    elif raw.event_type == "MANUAL_NOTE":
        text = metadata.get("message", "")
        content_hash = metadata.get("hash", "")
        
        semantic_content = f"Manual Architectural Note:\n{text}"
        
        return StructuredEvent(
            event_type=raw.event_type,
            path=raw.path,
            content=semantic_content,
            hash=content_hash,
            metadata=metadata
        )
        
    else:
        # File System Event
        file_content = ""
        if raw.event_type != "FILE_DELETED":
            if is_high_signal(raw.path):
                file_content = await asyncio.to_thread(get_file_content, raw.path)
            else:
                file_content = "[Content not indexed - Structural change only]"
            
        semantic_content = (
            f"Project File: {raw.path}\n"
            f"Status: {raw.event_type}\n"
            f"Content:\n{file_content}"
        )
        
        # Hash based on path + content
        hash_input = f"{raw.path}:{file_content}"
        content_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        return StructuredEvent(
            event_type=raw.event_type,
            path=raw.path,
            content=semantic_content,
            hash=content_hash,
            metadata={
                "timestamp": raw.timestamp
            }
        )
