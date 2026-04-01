@echo off
REM FITS Database Viewer Launcher
REM This batch file launches the FITS Database GUI application

echo.
echo ================================================
echo   FITS Database Viewer
echo ================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ or run FITS_Database.exe instead
    pause
    exit /b 1
)

REM Launch the application
echo Starting FITS Database Viewer...
python fits_gui_database.py

REM If script ends, show a message
echo.
echo FITS Database Viewer closed
pause
