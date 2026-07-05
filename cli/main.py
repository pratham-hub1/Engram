import os
import sys
import requests
import typer
from pathlib import Path

app = typer.Typer(help="Engram Command Line Interface")

BASE_URL = "http://localhost:8000"

@app.command()
def note(text: str):
    """
    Record an architectural decision or manual note.
    Bypasses the observer and enters the memory pipeline directly.
    """
    try:
        response = requests.post(f"{BASE_URL}/api/notes", json={"text": text})
        if response.status_code == 200:
            data = response.json()
            typer.secho(f"[OK] {data.get('status')} Data ID: {data.get('data_id')}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"Error: Server returned {response.status_code}\n{response.text}", fg=typer.colors.RED)
    except requests.exceptions.ConnectionError:
        typer.secho("Error: Engram backend is not running. Please start it first.", fg=typer.colors.RED)

@app.command()
def install_hook():
    """
    Installs an optional git post-commit hook to prompt for architectural decision reasoning.
    """
    git_dir = Path(".git")
    if not git_dir.exists() or not git_dir.is_dir():
        typer.secho("Error: Not a git repository (no .git directory found).", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / "post-commit"
    
    hook_script = """#!/bin/bash
# Engram - Optional Git Post-Commit Hook

# Check if running in an interactive terminal
if [ ! -t 1 ]; then
    # Not a terminal (e.g., GUI client like VSCode or GitHub Desktop)
    # Silently skip to prevent hanging the GUI
    exit 0
fi

exec < /dev/tty

echo -e "\n\033[1;34mEngram:\033[0m Architectural change detected."
read -p "Reason? (Enter to skip): " REASON

if [ ! -z "$REASON" ]; then
    echo "Recording decision..."
    # Call the local CLI
    python -m cli.main note "$REASON"
else
    echo "Skipped."
fi
"""
    
    try:
        with open(hook_path, "w", newline='\n') as f:
            f.write(hook_script)
            
        # Make executable (Linux/macOS)
        if os.name != 'nt':
            os.chmod(hook_path, 0o755)
            
        typer.secho(f"[OK] Installed Engram post-commit hook at {hook_path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error installing hook: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
