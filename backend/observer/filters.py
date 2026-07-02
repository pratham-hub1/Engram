import re
from pathlib import Path

# Hard Ignore Rules
IGNORE_DIRS = {
    "node_modules", ".venv", "venv", "env", ".env", "__pycache__",
    "dist", "build", ".cache", ".cognee_system", ".idea", ".vscode"
}

IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".log", ".tmp", ".temp", ".swp"
}

def is_ignored(path_str: str) -> bool:
    """Returns True if the path should be completely ignored by the Observer."""
    path = Path(path_str)
    
    # Check directory parts against ignore list
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    
    # Ignore specific git internals, EXCEPT .git/logs/HEAD which we need for commits
    if ".git" in path.parts:
        if path.parts[-2:] == (".git", "logs") or path.parts[-3:] == (".git", "logs", "HEAD"):
            return False # We need this for git commit detection
        return True
        
    if path.suffix in IGNORE_EXTENSIONS:
        return True
        
    return False

def is_high_signal(path_str: str) -> bool:
    """
    Returns True if a file modification is considered high-signal.
    High-signal files are sent to the queue. Source code changes (*.py, etc.)
    are intentionally ignored because they are captured via git commits instead.
    """
    path = Path(path_str)
    
    if is_ignored(path_str):
        return False

    # 1. Dependency files
    if path.name in ("package.json", "requirements.txt", "pyproject.toml", "Cargo.toml", "Gemfile", "go.mod"):
        return True
        
    # 2. Config files
    if path.name in ("docker-compose.yml", ".env.example") or path.name.endswith(".yml") or path.name.endswith(".yaml"):
        return True
        
    # 3. Documentation
    if path.suffix == ".md":
        return True
        
    return False
