# PipelineApp Complete Build and Installer Script
# This script builds the executable and creates a Windows installer

param(
    [switch]$SkipDeps,
    [switch]$SkipBuild,
    [switch]$SkipInstaller,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Configuration
$APP_NAME = "PipelineApp"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$INSTALLER_DIR = "$PROJECT_ROOT\installer"
$DIST_DIR = "$PROJECT_ROOT\dist"
$BUILD_DIR = "$PROJECT_ROOT\build"
$NSIS_PATH = "${env:ProgramFiles(x86)}\NSIS\makensis.exe"

Write-Host "Building $APP_NAME Installer..." -ForegroundColor Green
Write-Host "Project Root: $PROJECT_ROOT" -ForegroundColor Blue

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Clean previous builds if requested
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    
    if (Test-Path $BUILD_DIR) {
        Remove-Item -Recurse -Force $BUILD_DIR
        Write-Host "  Removed build directory" -ForegroundColor Green
    }
    
    if (Test-Path $DIST_DIR) {
        Remove-Item -Recurse -Force $DIST_DIR
        Write-Host "  Removed dist directory" -ForegroundColor Green
    }
    
    if (Test-Path "$INSTALLER_DIR\*.exe") {
        Remove-Item "$INSTALLER_DIR\*.exe"
        Write-Host "  Removed old installers" -ForegroundColor Green
    }
}

# Install dependencies
if (-not $SkipDeps) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install PyInstaller
    python -m pip install pyinstaller
    
    # Install project requirements
    if (Test-Path "$PROJECT_ROOT\requirements.txt") {
        python -m pip install -r "$PROJECT_ROOT\requirements.txt"
    }
    else {
        Write-Host "No requirements.txt found, installing essential packages..." -ForegroundColor Yellow
        python -m pip install PyQt5 pandas numpy matplotlib seaborn scipy scikit-learn paramiko python-dotenv statsmodels pyyaml
    }
    
    Write-Host "  Dependencies installed" -ForegroundColor Green
}

# Build executable
if (-not $SkipBuild) {
    Write-Host "Building executable..." -ForegroundColor Yellow
    
    # Change to project root for build
    Push-Location $PROJECT_ROOT
    
    try {
        # Build using spec file
        python -m PyInstaller "$INSTALLER_DIR\PipelineApp.spec" --clean --noconfirm
        
        if (Test-Path "$DIST_DIR\PipelineApp.exe") {
            Write-Host "  Executable built successfully: $DIST_DIR\PipelineApp.exe" -ForegroundColor Green
        }
        else {
            throw "Executable not found after build"
        }
    }
    catch {
        Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Create installer
if (-not $SkipInstaller) {
    Write-Host "Creating installer..." -ForegroundColor Yellow
    
    # Check if NSIS is installed
    if (-not (Test-Path $NSIS_PATH)) {
        Write-Host "NSIS not found at $NSIS_PATH" -ForegroundColor Red
        Write-Host "Please install NSIS from: https://nsis.sourceforge.io/" -ForegroundColor Yellow
        exit 1
    }
    
    # Ensure required files exist
    if (-not (Test-Path "$DIST_DIR\PipelineApp.exe")) {
        Write-Host "Executable not found. Run build first or use -SkipBuild:$false" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path "$PROJECT_ROOT\resources\rat_icon.ico")) {
        Write-Host "Icon file not found at $PROJECT_ROOT\resources\rat_icon.ico" -ForegroundColor Red
        exit 1
    }
    
    # Change to installer directory
    Push-Location $INSTALLER_DIR
    
    try {
        # Run NSIS compiler
        & $NSIS_PATH "PipelineApp.nsi"
        
        if ($LASTEXITCODE -eq 0) {
            $installerPath = Get-ChildItem -Path . -Name "*.exe" | Select-Object -First 1
            if ($installerPath) {
                Write-Host "  Installer created: $INSTALLER_DIR\$installerPath" -ForegroundColor Green
                
                # Get installer size
                $installerSize = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
                Write-Host "  Installer size: $installerSize MB" -ForegroundColor Blue
            }
            else {
                Write-Host "  Installer compilation succeeded but file not found" -ForegroundColor Yellow
            }
        }
        else {
            throw "NSIS compilation failed with exit code: $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "Installer creation failed: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Summary
Write-Host ""
Write-Host "Build process completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Build Summary:" -ForegroundColor Cyan

if (Test-Path "$DIST_DIR\PipelineApp.exe") {
    $exeSize = [math]::Round((Get-Item "$DIST_DIR\PipelineApp.exe").Length / 1MB, 2)
    Write-Host "  Executable: $DIST_DIR\PipelineApp.exe ($exeSize MB)" -ForegroundColor Green
}

$installerFiles = Get-ChildItem -Path "$INSTALLER_DIR\*.exe" -ErrorAction SilentlyContinue
foreach ($installer in $installerFiles) {
    $installerSize = [math]::Round($installer.Length / 1MB, 2)
    Write-Host "  Installer: $($installer.FullName) ($installerSize MB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation Notes:" -ForegroundColor Cyan
Write-Host "  - The executable runs without console window" -ForegroundColor Green
Write-Host "  - Installer creates desktop and start menu shortcuts" -ForegroundColor Green
Write-Host "  - Application installs to: %LOCALAPPDATA%\PipelineApp" -ForegroundColor Green
Write-Host "  - Uninstaller is included for easy removal" -ForegroundColor Green

Write-Host ""
Write-Host "Ready for distribution!" -ForegroundColor Green
