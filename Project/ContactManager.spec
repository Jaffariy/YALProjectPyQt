# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('about-icon.png', '.'), ('add-contact.ico.png', '.'), ('add-tag.ico.png', '.'), ('app-icon.png', '.'), ('contacts.ico.png', '.'), ('delete-contact.ico.png', '.'), ('edit-contact.ico.png', '.'), ('export-icon.png', '.'), ('import-icon.png', '.'), ('open-tags.ico.png', '.'), ('search-contact.ico.png', '.'), ('your-logo.png', '.'), ('music1.mp3', '.'), ('music2.mp3', '.'), ('music3.mp3', '.'), ('music4.mp3', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ContactManager',
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
