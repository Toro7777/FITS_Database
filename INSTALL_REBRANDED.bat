@echo off
REM FITS Database Viewer Installation Script
REM This script sets up the FITS Database Viewer for Windows

echo.
echo ================================================
echo   FITS Database Viewer Installation
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install required Python packages
echo Installing required Python packages...
echo.

python -m pip install --upgrade pip setuptools wheel
python -m pip install astropy pillow numpy pandas matplotlib

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo [OK] All packages installed successfully!
echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To launch the FITS Database Viewer, double-click:
echo   launch_fits_gui.bat
echo.
pause
