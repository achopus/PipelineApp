@echo off
setlocal enabledelayedexpansion

:: PipelineApp Build and Installer Script (Batch Version)
echo ========================================
echo  PipelineApp Build and Installer
echo ========================================

set "PROJECT_ROOT=%~dp0.."
set "INSTALLER_DIR=%PROJECT_ROOT%\installer"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "BUILD_DIR=%PROJECT_ROOT%\build"
set "NSIS_PATH=%ProgramFiles(x86)%\NSIS\makensis.exe"

echo Project Root: %PROJECT_ROOT%
echo.

:: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)
python --version
echo OK: Python is available
echo.

:: Clean previous builds
echo [2/5] Cleaning previous builds...
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
    echo OK: Removed build directory
)
if exist "%DIST_DIR%" (
    rmdir /s /q "%DIST_DIR%"
    echo OK: Removed dist directory
)
if exist "%INSTALLER_DIR%\*.exe" (
    del /q "%INSTALLER_DIR%\*.exe"
    echo OK: Removed old installers
)
echo.

:: Install dependencies
echo [3/5] Installing dependencies...
echo Installing PyInstaller...
python -m pip install pyinstaller

echo Installing project requirements...
if exist "%PROJECT_ROOT%\requirements.txt" (
    python -m pip install -r "%PROJECT_ROOT%\requirements.txt"
) else (
    echo No requirements.txt found, installing essential packages...
    python -m pip install PyQt5 pandas numpy matplotlib seaborn scipy scikit-learn paramiko python-dotenv statsmodels pyyaml
)
echo OK: Dependencies installed
echo.

:: Build executable
echo [4/5] Building executable...
cd /d "%PROJECT_ROOT%"
python -m PyInstaller "%INSTALLER_DIR%\PipelineApp.spec" --clean --noconfirm

if exist "%DIST_DIR%\PipelineApp.exe" (
    echo OK: Executable built successfully
) else (
    echo ERROR: Executable build failed
    pause
    exit /b 1
)
echo.

:: Create installer
echo [5/5] Creating installer...

:: Check if NSIS is installed
if not exist "%NSIS_PATH%" (
    echo ERROR: NSIS not found at %NSIS_PATH%
    echo Please install NSIS from: https://nsis.sourceforge.io/
    pause
    exit /b 1
)

:: Check required files
if not exist "%DIST_DIR%\PipelineApp.exe" (
    echo ERROR: Executable not found
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\resources\rat_icon.ico" (
    echo ERROR: Icon file not found
    pause
    exit /b 1
)

:: Run NSIS compiler
cd /d "%INSTALLER_DIR%"
"%NSIS_PATH%" "PipelineApp.nsi"

if errorlevel 1 (
    echo ERROR: Installer creation failed
    pause
    exit /b 1
) else (
    echo OK: Installer created successfully
)

echo.
echo ========================================
echo  Build Completed Successfully!
echo ========================================
echo.
echo Files created:
if exist "%DIST_DIR%\PipelineApp.exe" (
    echo   - Executable: %DIST_DIR%\PipelineApp.exe
)
for %%f in ("%INSTALLER_DIR%\*.exe") do (
    echo   - Installer: %%f
)
echo.
echo Installation Notes:
echo   - The executable runs without console window
echo   - Installer creates desktop and start menu shortcuts
echo   - Application installs to: %%LOCALAPPDATA%%\PipelineApp
echo   - Uninstaller is included for easy removal
echo.
echo Ready for distribution!
echo.
pause
