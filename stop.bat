@echo off
chcp 65001 >nul
echo ================================================
echo           LSnuts2 Quick Stop Script
echo ================================================
echo.

echo [1/2] Stopping Backend Server...
taskkill /f /im python.exe /t 2>nul
taskkill /f /im py.exe /t 2>nul

echo [2/2] Stopping Frontend Server...
taskkill /f /im node.exe /t 2>nul

echo.
echo ================================================
echo              All Servers Stopped!
echo ================================================
echo.
echo Press any key to close this window...
pause >nul