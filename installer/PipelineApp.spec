# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the absolute path to the source directory
script_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(script_dir)
source_dir = os.path.join(project_root, 'source')

block_cipher = None

# Hidden imports for all dependencies
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'seaborn',
    'scipy',
    'scipy.stats',
    'sklearn',
    'paramiko',
    'dotenv',
    'statsmodels',
    'statsmodels.api',
    'statsmodels.formula.api',
    'statsmodels.stats.anova',
    'statsmodels.stats.multicomp',
    'yaml',
    'logging',
    'pathlib',
    'typing',
    'datetime',
    'os',
    'sys',
]

# Data files to include
datas = [
    # Include the icon file
    (os.path.join(project_root, 'resources', 'rat_icon.ico'), 'resources'),
    # Include any configuration files if they exist
]

# Check for .env file
env_path = os.path.join(source_dir, 'cluster_networking', '.env')
if os.path.exists(env_path):
    datas.append((env_path, 'cluster_networking'))

a = Analysis(
    [os.path.join(source_dir, 'main_window.py')],
    pathex=[source_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude tkinter if not needed
        'matplotlib.backends.backend_tkagg',  # Exclude tk backend
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PipelineApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # CRITICAL: No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'resources', 'rat_icon.ico'),  # Application icon
    version_file=os.path.join(script_dir, 'version_info.py'),  # Version information
)
