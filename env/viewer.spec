# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

APP_NAME = 'E57-Image-and-Point-Cloud-Overlay-Viewer'
ENV_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = ENV_DIR.parent

# Conda stores native dependencies outside site-packages. Make them available
# to PyInstaller even when this spec is used without activating the environment.
CONDA_DLL_DIR = Path(sys.prefix) / 'Library' / 'bin'
if os.name == 'nt' and (Path(sys.prefix) / 'conda-meta').is_dir() and CONDA_DLL_DIR.is_dir():
    os.environ['PATH'] = str(CONDA_DLL_DIR) + os.pathsep + os.environ.get('PATH', '')

binaries = []
datas = [
    (str(PROJECT_ROOT / 'tools'), 'tools'),
    (str(PROJECT_ROOT / 'assets'), 'assets'),
]
hiddenimports = [
    'pye57',
    'pyquaternion',
]

# pye57 includes native components on Windows. These helpers are safe even if
# the package layout changes; PyInstaller will include what it can discover.
try:
    binaries += collect_dynamic_libs('pye57')
    hiddenimports += collect_submodules('pye57')
except Exception:
    pass


a = Analysis(
    [str(ENV_DIR / 'run_viewer_packaged.py')],
    pathex=[str(PROJECT_ROOT), str(PROJECT_ROOT / 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    icon=str(PROJECT_ROOT / 'assets' / 'imvisionlabs-main-logoonly.png'),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
