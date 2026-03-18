@echo off
title Elkhart Command Center Launcher
echo --------------------------------------------------
echo 🚀 Cleaning up previous instances...
echo --------------------------------------------------

:: Kill any existing python processes running the engine or server
taskkill /f /im python.exe /t >nul 2>&1

echo 🚀 Starting Elkhart Command Engine...
echo --------------------------------------------------

:: 1. Start the Python Engine in a new minimized window
:: It now has a persistent loop
start "ElkhartEngine" /min cmd /c "python engine.py"

echo ✅ Engine Started (Watching data_inputs folder every 10s)
echo --------------------------------------------------
echo 🌐 Starting Web Dashboard...
echo --------------------------------------------------

:: 2. Open the dashboard in your default browser
:: We use fallback to Python's server as it's most reliable for local dev
start "" http://localhost:8000
python -m http.server 8000

pause
