# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import sys

# Get the project root directory
project_root = os.path.abspath(SPECPATH)
src_path = os.path.join(project_root, 'src')

# Add all necessary data files
datas = [
    (os.path.join(src_path, 'plaza', 'util', 'item_db.json'), 'plaza/util'),
    (os.path.join(src_path, 'plaza', 'util', 'item_db_cn.json'), 'plaza/util'),
    (os.path.join(project_root, 'assets', 'presets'), 'assets/presets'),
]

a = Analysis(
    ['run.py'],
    pathex=[project_root, src_path],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'plaza.crypto',
        'plaza.crypto.fnvhash',
        'plaza.crypto.hashdb',
        'plaza.crypto.scblock',
        'plaza.crypto.sctypecode',
        'plaza.crypto.scxorshift',
        'plaza.crypto.swishcrypto',
        'plaza.types',
        'plaza.types.accessors',
        'plaza.types.bagsave',
        'plaza.types.coredata',
        'plaza.types.pokedex',
        'plaza.util.items',
        'pokemon_legends_za_editor.main',
        'pokemon_legends_za_editor.plza_config',
        'pokemon_legends_za_editor.plza_utils',
        'pokemon_legends_za_editor.preset_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Pokemon_Legends_ZA_Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'za.ico'),  # Application icon
)
