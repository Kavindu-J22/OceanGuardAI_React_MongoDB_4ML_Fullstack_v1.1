# OceanGuard AI — PowerShell Fullstack Launch Script
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "Starting OceanGuard AI Full-Stack Platform..." -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $PSScriptRoot

Write-Host "[1/2] Launching OceanGuard AI FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootDir\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching OceanGuard AI React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootDir\frontend'; npm run dev"

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "OceanGuard AI Platform is running!" -ForegroundColor Cyan
Write-Host " - Backend API:    http://localhost:8000" -ForegroundColor Yellow
Write-Host " - Swagger Docs:   http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host " - React Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
