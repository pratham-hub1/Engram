$ErrorActionPreference = "Stop"

Write-Host "Starting Engram Backend..." -ForegroundColor Green

# Check if virtual environment exists, if not, create and install
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    .\.venv\Scripts\Activate.ps1
}

# Run the FastAPI server
python -m backend.main
