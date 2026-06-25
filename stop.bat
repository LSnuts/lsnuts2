@echo off
chcp 65001 >nul
echo ================================================
echo           LSnuts2 Quick Stop Script
echo ================================================
echo.

echo [1/3] Stopping Backend Server...
taskkill /f /im python.exe /t 2>nul
if %errorlevel% equ 0 (
    echo       [OK] Backend Server stopped.
) else (
    echo       [INFO] No backend server running.
)

echo [2/3] Stopping Frontend Server...
taskkill /f /im node.exe /t 2>nul
if %errorlevel% equ 0 (
    echo       [OK] Frontend Server stopped.
) else (
    echo       [INFO] No frontend server running.
)

echo [3/3] Stopping Related Processes...
taskkill /f /im py.exe /t 2>nul

echo.
echo ================================================
echo              All Servers Stopped!
echo ================================================
echo.
echo Press any key to close this window...
pause >nul