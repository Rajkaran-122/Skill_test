$ErrorActionPreference = "Stop"

Write-Host "Starting Store Intelligence Platform - Local Mode" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Install python dependencies and run backend
Write-Host "`n[1/2] Starting API Backend..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command `"cd services\api; if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -e .; pip install aiosqlite sqlmodel; uvicorn src.main:app --reload --port 8000`""

# Wait a couple of seconds for backend to start
Start-Sleep -Seconds 3

# Install node dependencies and run frontend
Write-Host "[2/2] Starting React Dashboard..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command `"cd services\dashboard; npm install; npm run dev`""

Write-Host "`nAll services starting! " -ForegroundColor Green
Write-Host "API: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C in this window to exit (you may need to close the spawned windows manually)." -ForegroundColor Gray
