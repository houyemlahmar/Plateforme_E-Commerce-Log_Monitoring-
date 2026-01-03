@echo off
echo ============================================================
echo Starting E-Commerce Log Platform with JWT Authentication
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking services...
python check_services.py
if errorlevel 1 (
    echo.
    echo ERROR: Required services are not running!
    echo Please start services with: docker-compose up -d
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Flask application...
echo.
python main.py

pause
