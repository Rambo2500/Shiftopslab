@echo off
title ShiftOps-OS Platform Launcher
echo ==========================================
echo    ShiftOps-OS - Core Intelligence
echo ==========================================
echo.

:: 1. Start Core Backend
echo [1/4] Starting Core Architecture API (8000)...
start "ShiftOps Core" cmd /k "python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Start Surface Projector Bridge
echo [2/4] Starting Surface Projector (8001)...
:: Using port 8001 to avoid conflict with Core API
start "ShiftOps Surface" cmd /k "python -m uvicorn surface_orchestrator:app --host 127.0.0.1 --port 8001 --reload"

:: Wait for backends
timeout /t 5 /nobreak > nul

:: 3. Start Frontend Studio
echo [3/4] Starting ShiftOps Studio (Vite)...
cd shiftops_studio
start "ShiftOps Studio" cmd /k "npm run dev -- --port 5173"

:: 4. Launch Projector
echo [4/4] Projecting Showroom...
timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo ==========================================
echo    SYSTEM ONLINE: http://localhost:5173
echo    SURFACE ACTIVE: 127.0.0.1:8001
echo ==========================================
echo.
pause
