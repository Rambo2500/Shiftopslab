# start-dev.ps1
# Starts both the Backend and Frontend

$BACKEND_DIR = 'C:\Users\thoms\ShiftOps-OSCoremobile\shiftopspro-workforce-engine'
$FRONTEND_DIR = "$BACKEND_DIR\shiftops-ui"

# Start Backend
Write-Host "ðŸš€ Starting Backend (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$BACKEND_DIR`"; uvicorn workforce_engine.main:app --reload --port 8000"

# Start Frontend
Write-Host "ðŸš€ Starting Frontend (Vite)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$FRONTEND_DIR`"; npm run dev"

Write-Host "âœ… Both services are starting." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:5173"

