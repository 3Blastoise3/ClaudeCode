# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building standalone census-extract executable.

Build with: pyinstaller census_extract.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Determine platform-specific settings
if sys.platform == "win32":
    exe_name = "census-extract.exe"
elif sys.platform == "darwin":
    exe_name = "census-extract"
else:
    exe_name = "census-extract"

a = Analysis(
    ['census_extract/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'openpyxl.cell._writer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'PIL',
        'tkinter',
        'PyQt5',
        'PyQt6',
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
    name=exe_name.replace('.exe', ''),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
