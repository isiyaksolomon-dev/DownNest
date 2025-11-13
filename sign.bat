@echo off
REM ===================================================================
REM DownNest Code Signing Script for Codegic (Sectigo) Certificate
REM Windows Kits 10 Edition - WITH SHA256 DIGEST
REM ===================================================================

setlocal enabledelayedexpansion

REM Define paths
set CERT_PATH=certificate.pfx
set CERT_PASSWORD=DownNest@#2025
set TIMESTAMP_URL=http://timestamp.digicert.com
set EXE_PATH=dist\downnest.exe
set INSTALLER_PATH=Output\DownNest_Setup_1.0.1.exe
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"

REM Colors for output
color 0A

echo.
echo ===================================================================
echo DownNest Code Signing - Codegic Certificate (Windows Kits 10)
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
    echo Please run build.bat first to create the executable.
    pause
    exit /b 1
)

if not exist "%INSTALLER_PATH%" (
    color 0C
    echo ERROR: Installer not found at "%INSTALLER_PATH%"
    echo Please run Inno Setup compiler first to create the installer.
    pause
    exit /b 1
)

REM Check if signtool.exe exists
if not exist %SIGNTOOL% (
    color 0C
    echo ERROR: signtool.exe not found at %SIGNTOOL%
    echo Please verify Windows Kits 10 installation.
    pause
    exit /b 1
)

color 0A
echo [✓] All files verified successfully
echo.

REM Sign the main executable WITH SHA256 DIGEST
echo [2/4] Signing main executable: %EXE_PATH%
color 0B
%SIGNTOOL% sign /f "%CERT_PATH%" /p "%CERT_PASSWORD%" /fd SHA256 /t "%TIMESTAMP_URL%" /d "DownNest - Downloads Organizer" "%EXE_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Failed to sign main executable!
    echo Please verify:
    echo - Certificate password is correct
    echo - Certificate file is valid
    echo - Internet connection is available for timestamping
    pause
    exit /b 1
)
color 0A
echo [✓] Main executable signed successfully
echo.

REM Sign the installer WITH SHA256 DIGEST
echo [3/4] Signing installer: %INSTALLER_PATH%
color 0B
%SIGNTOOL% sign /f "%CERT_PATH%" /p "%CERT_PASSWORD%" /fd SHA256 /t "%TIMESTAMP_URL%" /d "DownNest Setup - Downloads Organizer" "%INSTALLER_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Failed to sign installer!
    echo Please verify certificate and connection settings.
    pause
    exit /b 1
)
color 0A
echo [✓] Installer signed successfully
echo.

REM Verify signatures
echo [4/4] Verifying signatures...
echo.
echo Verifying: %EXE_PATH%
color 0B
%SIGNTOOL% verify /pa "%EXE_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Main executable signature verification failed!
    pause
    exit /b 1
)
color 0A
echo.
echo Verifying: %INSTALLER_PATH%
color 0B
%SIGNTOOL% verify /pa "%INSTALLER_PATH%"

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Installer signature verification failed!
    pause
    exit /b 1
)
color 0A

echo.
echo ===================================================================
echo [✓] ALL SIGNATURES VERIFIED SUCCESSFULLY!
echo ===================================================================
echo.
echo Both files are now code signed with Codegic certificate:
echo - %EXE_PATH%
echo - %INSTALLER_PATH%
echo.
echo Your application will display as a trusted publisher!
echo.
pause
