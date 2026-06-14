# Start the local LLM API server (port 9000)
# Run this from the api-server directory

$venv = ".\.venv"

if (-not (Test-Path $venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venv
    & "$venv\Scripts\pip.exe" install -r requirements.txt --quiet
    Write-Host "Dependencies installed."
}

Write-Host "Starting Local LLM API on http://localhost:9000 ..."
Write-Host "  Web UI:  http://localhost:9000"
Write-Host "  Models:  http://localhost:9000/v1/models"
Write-Host "  Chat:    POST http://localhost:9000/v1/chat/completions"
Write-Host ""
& "$venv\Scripts\python.exe" server.py
