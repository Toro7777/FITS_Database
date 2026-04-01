# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['F:\\Documentos\\Python\\FITS_Library\\fits_gui_database.py'],
    pathex=[],
    binaries=[],
    datas=[('FITS_Viewer', 'FITS_Viewer')],
    hiddenimports=['astropy', 'astropy.io.fits', 'pandas', 'matplotlib', 'numpy'],
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
    a.binaries,
    a.datas,
    [],
    name='FITS_Library',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
