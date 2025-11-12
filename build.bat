@echo off
setlocal enabledelayedexpansion

cls
echo.
echo ====================================================================
echo                   DownNest Build Script v1.0
echo                  Smart Downloads Organizer
echo ====================================================================
echo.

REM ----------------------------
REM Check Python Installation
REM ----------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
echo ✅ Python detected
python --version
echo.

REM ----------------------------
REM Install/Upgrade pip
REM ----------------------------
echo Installing/upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM ----------------------------
REM Install Dependencies
REM ----------------------------
echo.
echo Installing dependencies...
echo   - watchdog
echo   - psutil
echo   - pywin32
echo   - winotify
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to install dependencies
    echo.
    pause
    exit /b 1
)

REM ----------------------------
REM Install PyInstaller if missing
REM ----------------------------
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller >nul 2>&1
)

REM ----------------------------
REM Clean previous builds
REM ----------------------------
if exist dist (
    echo Cleaning previous dist folder...
    rmdir /s /q dist >nul 2>&1
)
if exist build (
    rmdir /s /q build >nul 2>&1
)
if exist *.spec (
    del /q *.spec >nul 2>&1
)

REM ----------------------------
REM Build Main Executable
REM ----------------------------
echo.
echo ====================================================================
echo Building DownNest (organizer.exe) with PyInstaller...
echo ====================================================================
echo.

pyinstaller --onefile --windowed --name downnest --icon=icon.ico src/organizer.py --add-data "src\config_default.json;."

if errorlevel 1 (
    echo.
    echo ❌ ERROR: PyInstaller build failed
    echo.
    pause
    exit /b 1
)

REM ----------------------------
REM Verify Build
REM ----------------------------
if not exist dist\downnest.exe (
    echo.
    echo ❌ ERROR: Build completed but executable not found
    echo.
    pause
    exit /b 1
)

REM ----------------------------
REM Build Summary
REM ----------------------------
echo.
echo ====================================================================
echo ✅ Build Successful!
echo ====================================================================
echo.
echo Build artifacts:
echo   ✓ dist\downnest.exe (Main application)
echo   ✓ src\config_default.json (Configuration)
echo   ✓ icon.ico (Application icon)
echo   ✓ nssm.exe (Service manager - to be included in installer)
echo.
echo Next steps to create installer:
echo   1. Download Inno Setup 6.x from https://jrsoftware.org/isdl.php
echo   2. Make sure installer_script.iss points to dist\downnest.exe and nssm.exe
echo   3. Run: iscc installer_script.iss
echo   4. Execute: DownNest_Setup_1.0.0.exe
echo.
echo ====================================================================
echo.
pause
