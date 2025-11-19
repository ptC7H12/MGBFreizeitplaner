# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec-Datei für MGBFreizeitplaner Desktop-App

Erstellt eine standalone Windows .exe mit allen Abhängigkeiten.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os

# Arbeitsverzeichnis
block_cipher = None
project_root = os.path.abspath(SPECPATH)

# Sammle alle Hidden Imports für FastAPI und Dependencies
hiddenimports = [
    # PyWebView
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'clr',
    'pythonnet',
    'clr_loader',
    'clr_loader.ffi',
    'clr_loader.util',
    # Uvicorn
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    # App modules
    'app.main',
    'app.config',
    'app.database',
    'app.models',
    'app.routers',
    'app.services',
    'app.utils',
    # Database
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'alembic',
    # Other
    'jinja2',
    'email_validator',
    'reportlab',
    'qrcode',
    'openpyxl',
    'yaml',
    'pydantic',
]

# Sammle alle Submodule
hiddenimports += collect_submodules('webview')
hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('alembic')
hiddenimports += collect_submodules('reportlab')
hiddenimports += collect_submodules('pythonnet')
hiddenimports += collect_submodules('clr_loader')

# Data Files - Templates, Static Files, Migrations, etc.
datas = []

# Pythonnet und clr_loader Data Files (wichtig für .NET Runtime)
datas += collect_data_files('pythonnet')
datas += collect_data_files('clr_loader')

# Templates hinzufügen
datas += [(os.path.join(project_root, 'app/templates'), 'app/templates')]

# Static Files hinzufügen
datas += [(os.path.join(project_root, 'app/static'), 'app/static')]

# Alembic Migrations hinzufügen (falls vorhanden)
if os.path.exists(os.path.join(project_root, 'alembic')):
    datas += [(os.path.join(project_root, 'alembic'), 'alembic')]
if os.path.exists(os.path.join(project_root, 'alembic.ini')):
    datas += [(os.path.join(project_root, 'alembic.ini'), '.')]

# .env.example hinzufügen (falls vorhanden)
if os.path.exists(os.path.join(project_root, '.env.example')):
    datas += [(os.path.join(project_root, '.env.example'), '.')]

# Ruleset-Vorlagen (falls vorhanden)
if os.path.exists(os.path.join(project_root, 'rulesets')):
    datas += [(os.path.join(project_root, 'rulesets'), 'rulesets')]

# VERSION.txt hinzufügen
if os.path.exists(os.path.join(project_root, 'VERSION.txt')):
    datas += [(os.path.join(project_root, 'VERSION.txt'), '.')]

# Binaries für pythonnet und clr_loader
binaries = []
binaries += collect_dynamic_libs('pythonnet')
binaries += collect_dynamic_libs('clr_loader')

a = Analysis(
    ['desktop_app.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[os.path.join(project_root, 'hooks')],
    hooksconfig={},
    runtime_hooks=[
        os.path.join(project_root, 'hooks', 'pyi_rth_pythonnet.py'),
        os.path.join(project_root, 'hooks', 'pyi_rth_webview.py'),
    ],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'IPython',
        'jupyter',
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
    [],
    exclude_binaries=True,
    name='MGBFreizeitplaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Kein Konsolen-Fenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Windows .ico Icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MGBFreizeitplaner',
)
