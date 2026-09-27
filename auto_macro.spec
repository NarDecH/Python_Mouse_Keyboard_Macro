# -*- mode: python ; coding: utf-8 -*-
# ไฟล์ spec สำหรับ PyInstaller — build Auto Mouse & Keyboard Macro เป็น .exe ไฟล์เดียว
# ใช้:  py -m PyInstaller auto_macro.spec --noconfirm

a = Analysis(
    ['auto_macro.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy.distutils', 'scipy', 'pandas', 'PyQt5', 'PyQt6',
              'PySide2', 'PySide6', 'IPython', 'notebook', 'pytest'],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoMouseMacro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # โปรแกรม GUI ไม่ต้องมีหน้าต่าง console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
