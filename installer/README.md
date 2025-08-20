# PipelineApp Installer

This directory contains everything needed to build a Windows installer for PipelineApp that runs without showing a console window.

## 🚀 Quick Start

### Option 1: PowerShell (Recommended)
```powershell
cd installer
.\build_installer.ps1
```

### Option 2: Batch File
```cmd
cd installer
build_installer.bat
```

## 📋 Prerequisites

### Required Software:
1. **Python 3.7+** with pip
2. **NSIS (Nullsoft Scriptable Install System)**
   - Download from: https://nsis.sourceforge.io/
   - Default installation path: `C:\Program Files (x86)\NSIS\`

### Python Dependencies:
All dependencies are automatically installed by the build script:
- PyInstaller (for executable creation)
- PyQt5, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn
- paramiko, python-dotenv, statsmodels, pyyaml

## 🔧 Build Process

The build process consists of 5 steps:

1. **Dependency Installation** - Installs PyInstaller and project requirements
2. **Clean Previous Builds** - Removes old build artifacts
3. **Executable Creation** - Uses PyInstaller to create PipelineApp.exe
4. **Installer Creation** - Uses NSIS to create Windows installer
5. **Validation** - Tests the created files

## 📁 Output Files

After successful build:

```
installer/
├── PipelineApp_Setup.exe    # Windows installer (distributable)
dist/
├── PipelineApp.exe          # Standalone executable
```

## 🎯 Key Features

### No Console Window
- **console=False** in PyInstaller spec ensures no terminal appears
- Application runs as a windowed GUI application
- Error logging is handled internally via log files

### Complete Installer Package
- **Desktop shortcut** creation
- **Start Menu** integration
- **Uninstaller** included
- **Registry entries** for proper Windows integration
- **Icon** integration throughout

### Professional Appearance
- Application icon in executable and installer
- Version information embedded in executable
- Proper Windows application registration

## 🛠️ Advanced Usage

### Custom Build Options (PowerShell only):

```powershell
# Skip dependency installation (if already installed)
.\build_installer.ps1 -SkipDeps

# Only build executable (skip installer creation)
.\build_installer.ps1 -SkipInstaller

# Clean build (remove all previous artifacts)
.\build_installer.ps1 -Clean

# Skip executable build (only create installer)
.\build_installer.ps1 -SkipBuild
```

### Custom NSIS Path:
If NSIS is installed in a non-standard location, edit the script:
```powershell
$NSIS_PATH = "C:\Your\Custom\Path\NSIS\makensis.exe"
```

## 📂 File Structure

```
installer/
├── PipelineApp.nsi          # NSIS installer script
├── PipelineApp.spec         # PyInstaller specification
├── version_info.py          # Windows version information
├── build_installer.ps1     # PowerShell build script
├── build_installer.bat     # Batch build script
└── README.md               # This file
```

## 🎛️ Customization

### Application Information:
Edit these files to customize:

- **PipelineApp.nsi**: App name, version, publisher, install location
- **version_info.py**: Version numbers, company info, file description
- **PipelineApp.spec**: Build configuration, hidden imports, data files

### Installer Behavior:
- **Install Location**: Currently set to `%LOCALAPPDATA%\PipelineApp`
- **Shortcuts**: Desktop and Start Menu shortcuts created
- **Registry**: Minimal registry entries for uninstallation

## 🔍 Troubleshooting

### Common Issues:

**"Python not found"**
- Ensure Python is installed and in PATH
- Try `python --version` in command prompt

**"NSIS not found"**
- Install NSIS from official website
- Check installation path matches script expectation

**"PyInstaller failed"**
- Check for missing dependencies
- Try installing requirements manually: `pip install -r requirements.txt`

**"Executable won't run"**
- Check Windows Defender / antivirus isn't blocking
- Try running from command line to see error messages
- Verify all required DLLs are included

**"Console window still appears"**
- Verify `console=False` in PipelineApp.spec
- Check no print() statements redirect to console
- Ensure logging is configured to file only

### Debug Mode:
To enable debugging, edit `PipelineApp.spec`:
```python
exe = EXE(
    # ... other parameters ...
    console=True,  # Change to True for debugging
    debug=True,    # Enable debug mode
)
```

## 📋 Installation Details

When users run `PipelineApp_Setup.exe`:

1. **Welcome Screen** with application icon
2. **License Agreement** (if LICENSE.txt exists)
3. **Installation Directory** selection
4. **File Installation** with progress bar
5. **Shortcut Creation** (Desktop + Start Menu)
6. **Registry Entries** for uninstallation
7. **Completion** with option to launch app

### Uninstallation:
- Available via Windows "Add/Remove Programs"
- Start Menu uninstaller shortcut
- Removes all files, shortcuts, and registry entries

## 🔒 Security Notes

- Executable is not code-signed (consider code signing for distribution)
- Windows may show "Unknown Publisher" warning
- Users may need to allow execution in Windows Defender
- Consider including virus scan results for distribution

## 📈 Distribution Checklist

Before distributing the installer:

- [ ] Test installer on clean Windows machine
- [ ] Verify no console windows appear during execution
- [ ] Test application functionality after installation
- [ ] Verify uninstaller works completely
- [ ] Check file associations and shortcuts
- [ ] Test on different Windows versions (if needed)
- [ ] Consider code signing for production releases

## 📞 Support

For build issues:
1. Check this README for common solutions
2. Verify all prerequisites are installed
3. Try a clean build with `-Clean` parameter
4. Check build logs for specific error messages

The installer creates a fully self-contained, professional Windows application package ready for distribution.
