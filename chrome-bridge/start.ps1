# Start the Chrome Gemini Nano bridge (port 8081)
# Requires Chrome Dev or Canary with flags enabled — see SETUP.md

if (-not (Test-Path ".\node_modules")) {
    Write-Host "Installing dependencies..."
    npm install --silent
}

Write-Host "Starting Chrome Gemini Nano bridge on http://localhost:8081 ..."
node server.js
