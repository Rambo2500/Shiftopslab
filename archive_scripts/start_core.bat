@echo off
echo Starting ShiftOps-OS Core Intelligence...

:: Start Backend in a new window
start "ShiftOps Core" cmd /k "python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload"

:: Wait a moment for backend to initialize
timeout /t 3

:: Start Frontend in a new window
cd shiftops_studio
start "ShiftOps Studio" cmd /k "npm run dev -- --port 5173"

echo.
echo Launching browser...
timeout /t 5
start http://localhost:5173

echo.
echo ShiftOps-OS is now running.
echo Keep these windows open while working.
