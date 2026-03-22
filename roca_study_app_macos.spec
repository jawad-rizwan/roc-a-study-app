# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

_version = open('VERSION').read().strip()

ctk_datas = collect_data_files('customtkinter')

app_datas = [
    ('data/questions.json', 'data'),
    ('data/flashcards.json', 'data'),
    ('data/reference.json', 'data'),
    ('data/lessons.json', 'data'),
    ('VERSION', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=ctk_datas + app_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ROCAStudyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='ROCAStudyApp.app',
    icon=None,
    bundle_identifier='com.rocastudy.app',
    info_plist={
        'CFBundleName': 'ROC-A Study App',
        'CFBundleDisplayName': 'ROC-A Study App',
        'CFBundleShortVersionString': _version,
        'CFBundleVersion': _version,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
    },
)
