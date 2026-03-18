@echo off
title ShiftOps Lab - Operational Kernel
echo ==========================================
echo    ShiftOps Lab - Unified Platform
echo ==========================================
echo.

:: 1. Start Unified Backend (Port 8000)
set PYTHONPATH=%CD%\ShiftOps-OS;%CD%
echo [1/2] Starting Unified Core API (8000)...
start "ShiftOps Core" cmd /k "cd ShiftOps-OS\core_intelligence && python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Start Unified Studio (Port 5173)
echo [2/2] Starting ShiftOps Studio...
start "ShiftOps Studio" cmd /k "cd ShiftOps-OS\core_intelligence\shiftops_studio && npm run dev -- --port 5173"

echo.
echo ==========================================
echo    SYSTEM ONLINE: http://localhost:5173
echo    BACKEND ACTIVE: http://localhost:8000
echo ==========================================
echo.
pause
