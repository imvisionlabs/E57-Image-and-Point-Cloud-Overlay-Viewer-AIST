# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

binaries = []
datas = [
    ('tools', 'tools'),
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
    ['run_viewer_packaged.py'],
    pathex=['.', 'src'],
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
    name='E57FusionViewer',
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
    name='E57FusionViewer',
)
