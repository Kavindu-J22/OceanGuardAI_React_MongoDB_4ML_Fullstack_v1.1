@echo off
TITLE OceanGuard AI — Full-Stack Launcher
echo ====================================================================
echo Starting OceanGuard AI Full-Stack Platform...
echo ====================================================================

REM Set root directory
set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"

echo [1/2] Launching OceanGuard AI FastAPI Backend on http://localhost:8000 ...
start "OceanGuard Backend" cmd /k "cd /d %ROOT_DIR%\backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo [2/2] Launching OceanGuard AI React Frontend on http://localhost:5173 ...
start "OceanGuard Frontend" cmd /k "cd /d %ROOT_DIR%\frontend && npm run dev"

echo.
echo ====================================================================
echo Services successfully launched:
echo  - Backend API:    http://localhost:8000
echo  - Swagger Docs:   http://localhost:8000/docs
echo  - React Frontend: http://localhost:5173
echo ====================================================================
