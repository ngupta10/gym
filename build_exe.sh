#!/bin/bash
# Build script for creating Windows .exe from Gym Management System
# Note: This script is for reference. PyInstaller should be run on Windows.

echo "========================================"
echo "Gym Management System - Build Script"
echo "========================================"
echo ""
echo "NOTE: PyInstaller works best on Windows."
echo "For cross-platform builds, consider using:"
echo "  - Docker with Windows container"
echo "  - Windows VM"
echo "  - GitHub Actions with Windows runner"
echo ""
echo "If you're on Windows, use build_exe.bat instead."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

echo "Step 1: Installing/Updating PyInstaller..."
python3 -m pip install --upgrade pyinstaller

echo ""
echo "Step 2: Installing all dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "Step 3: Building executable..."
pyinstaller build_exe.spec --clean

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Your .exe file is located at:"
echo "dist/GymManagementSystem.exe"
echo ""

