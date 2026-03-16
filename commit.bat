@echo off
set /p msg="Enter commit message (or press enter for 'Auto-commit'): "
if "%msg%"=="" set msg=Auto-commit

echo Adding changes...
git add .

echo Committing...
git commit -m "%msg%"

echo.
echo Current Status:
git status

echo.
pause
