@echo off
setlocal enabledelayedexpansion

set VS_VCVARS="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
set VS_DEV_CMD="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"

if exist %VS_VCVARS% (
    echo [INFO] Initialising MSVC build environment via vcvarsall.bat...
    call %VS_VCVARS% arm64
    if errorlevel 1 (
        echo [ERROR] vcvarsall.bat failed to configure the environment.
        exit /b %errorlevel%
    )
) else if exist %VS_DEV_CMD% (
    echo [WARN] vcvarsall.bat not found. Falling back to VsDevCmd.bat.
    call %VS_DEV_CMD% -arch=arm64 -host_arch=arm64
    if errorlevel 1 (
        echo [ERROR] VsDevCmd.bat failed to configure the environment.
        exit /b %errorlevel%
    )
) else (
    echo [ERROR] Unable to locate either vcvarsall.bat or VsDevCmd.bat.
    echo         Ensure the "Desktop development with C++" or "MSVC v143" workload is installed.
    exit /b 1
)

echo [INFO] Installing tokenizers via pip...
pip install tokenizers
set ERRLEV=%errorlevel%

if %ERRLEV% NEQ 0 (
    echo [ERROR] pip install tokenizers failed with exit code %ERRLEV%.
    exit /b %ERRLEV%
)

echo [SUCCESS] tokenizers installed successfully.
exit /b 0
