@echo off
REM Fix build error by cleaning and ensuring dist folder exists

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Creating dist folder...
mkdir dist

echo Now try building again:
echo pyinstaller build_exe_debug.spec --clean
pause

