@echo off
REM Build script for creating Windows .exe from Gym Management System
REM Run this script on Windows to build the executable

echo ========================================
echo Gym Management System - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Step 1: Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Installing all dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 3: Building executable...
echo.
echo Choose build type:
echo   1. Release build (no console, optimized)
echo   2. Debug build (shows console, easier to debug)
set /p buildtype="Enter choice (1 or 2): "

if "%buildtype%"=="2" (
    echo Building DEBUG version...
    pyinstaller build_exe_debug.spec --clean
    if errorlevel 1 (
        echo ERROR: Build failed
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo DEBUG Build Complete!
    echo ========================================
    echo.
    echo Your .exe file is located at:
    echo dist\GymManagementSystem_DEBUG.exe
    echo.
    echo NOTE: This version shows a console window to help debug issues.
) else (
    echo Building RELEASE version...
    pyinstaller build_exe.spec --clean
    if errorlevel 1 (
        echo ERROR: Build failed
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo RELEASE Build Complete!
    echo ========================================
    echo.
    echo Your .exe file is located at:
    echo dist\GymManagementSystem.exe
)
echo.
echo You can distribute this file along with:
echo - The icon folder (if not bundled)
echo - A README with instructions
echo.
pause

