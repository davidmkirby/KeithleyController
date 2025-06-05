# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Keithley Dual Controller
This file defines how to package the application into a standalone executable
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Add project root to sys.path
project_root = os.path.abspath('.')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Collect data files and binary dependencies for all packages
datas = []
binaries = []
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'pyqtgraph.graphicsItems',
    'pyqtgraph.exporters',
    'numpy',
    'pandas',
    'serial',
    'pyvisa'
]

# PyQt6 data files
qt_data = collect_all('PyQt6')[0]
datas.extend(qt_data)

# PyQtGraph data files
pyqtgraph_data = collect_all('pyqtgraph')[0]
datas.extend(pyqtgraph_data)

# Add application specific files
app_datas = [
    ('src/', 'src/'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
]

# Only add logs directory if it exists (not in CI environments)
if os.path.exists('logs'):
    app_datas.append(('logs/', 'logs/'))

datas.extend(app_datas)

# Create the Analysis object
a = Analysis(
    ['keithley_controller.py'],  # Use the launcher script as entry point
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create the PYZ object (archive of Python modules)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KeithleyDualController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # No icon for now - can be added later
)

# Create the collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KeithleyDualController',
)

# For macOS, create a .app bundle
app = BUNDLE(
    coll,
    name='KeithleyDualController.app',
    icon=None,  # No icon for now - can be added later
    bundle_identifier='com.keithleycontroller',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleGetInfoString': 'Keithley 2290-5 & 6485 Dual Controller',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',  # For dark mode support
    },
)
