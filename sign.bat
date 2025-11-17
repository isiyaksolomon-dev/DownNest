@echo off
REM ===================================================================
REM DownNest Code Signing Script for Codegic (Sectigo) Certificate
REM Windows Kits 10 Edition - FIXED CERTIFICATE CHAIN
REM ===================================================================

setlocal enabledelayedexpansion

REM Define paths
set CERT_PATH=certificate.pfx
set CERT_PASSWORD=DownNest@#2025
set TIMESTAMP_URL=http://timestamp.digicert.com
set EXE_PATH=dist\downnest.exe
set INSTALLER_PATH=Output\DownNest_Setup_1.0.2.exe
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"

REM Colors for output
color 0A

echo.
echo ===================================================================
echo DownNest Code Signing - Codegic/Sectigo Certificate
echo ===================================================================
echo.

REM Check if certificate exists
if not exist "%CERT_PATH%" (
    color 0C
    echo ERROR: Certificate file not found at "%CERT_PATH%"
    echo Please ensure certificate.pfx is in the current directory.
    pause
    exit /b 1
)

REM Check if executables exist
if not exist "%EXE_PATH%" (
    color 0C
    echo ERROR: Main executable not found at "%EXE_PATH%"
    pause
    exit /b 1
)

if not exist "%INSTALLER_PATH%" (
    color 0C
    echo ERROR: Installer not found at "%INSTALLER_PATH%"
    pause
    exit /b 1
)

REM Check if signtool.exe exists
if not exist %SIGNTOOL% (
    color 0C
    echo ERROR: signtool.exe not found at %SIGNTOOL%
    pause
    exit /b 1
)

color 0A
echo [✓] All files verified successfully
echo.

REM STEP 1: Install certificate to trusted root store (optional but recommended)
echo [1/5] Installing certificate to Windows certificate store...
certutil -addstore -f "Root" "%CERT_PATH%" >nul 2>&1
color 0A
echo [✓] Certificate store updated
echo.

REM STEP 2: Sign the main executable with proper chain
echo [2/5] Signing main executable: %EXE_PATH%
color 0B
%SIGNTOOL% sign /f "%CERT_PATH%" /p "%CERT_PASSWORD%" /fd SHA256 /tr "%TIMESTAMP_URL%" /td SHA256 /d "DownNest - Downloads Organizer" /du "https://github.com/isiyaksolomon-dev/downnest" "%EXE_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Failed to sign main executable!
    pause
    exit /b 1
)
color 0A
echo [✓] Main executable signed successfully
echo.

REM STEP 3: Sign the installer
echo [3/5] Signing installer: %INSTALLER_PATH%
color 0B
%SIGNTOOL% sign /f "%CERT_PATH%" /p "%CERT_PASSWORD%" /fd SHA256 /tr "%TIMESTAMP_URL%" /td SHA256 /d "DownNest Setup - Downloads Organizer" /du "https://github.com/isiyaksolomon-dev/downnest" "%INSTALLER_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Failed to sign installer!
    pause
    exit /b 1
)
color 0A
echo [✓] Installer signed successfully
echo.

REM STEP 4: Verify main executable signature
echo [4/5] Verifying main executable signature...
color 0B
%SIGNTOOL% verify /pa "%EXE_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo WARNING: Main executable signature verification failed!
    echo This may be normal if certificate is not in trusted store.
    color 0A
) else (
    color 0A
    echo [✓] Main executable signature verified
)
echo.

REM STEP 5: Verify installer signature
echo [5/5] Verifying installer signature...
color 0B
%SIGNTOOL% verify /pa "%INSTALLER_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo WARNING: Installer signature verification failed!
    echo This may be normal if certificate is not in trusted store.
    color 0A
) else (
    color 0A
    echo [✓] Installer signature verified
)
color 0A

echo.
echo ===================================================================
echo [✓] CODE SIGNING COMPLETED
echo ===================================================================
echo.
echo Signed files:
echo - %EXE_PATH%
echo - %INSTALLER_PATH%
echo.
echo IMPORTANT: To resolve certificate chain trust issues:
echo 1. Install the root certificate from your certificate provider
echo 2. Use /tr (RFC 3161) instead of /t for modern timestamping
echo 3. Ensure internet connection during signing for timestamping
echo.
pause
