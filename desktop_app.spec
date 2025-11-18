# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec-Datei für MGBFreizeitplaner Desktop-App

Erstellt eine standalone Windows .exe mit allen Abhängigkeiten.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# Arbeitsverzeichnis
block_cipher = None
project_root = os.path.abspath(SPECPATH)

# Sammle alle Hidden Imports für FastAPI und Dependencies
hiddenimports = [
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
    'app.main',
    'app.config',
    'app.database',
    'app.models',
    'app.routers',
    'app.services',
    'app.utils',
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'alembic',
    'jinja2',
    'email_validator',
    'reportlab',
    'qrcode',
    'openpyxl',
    'yaml',
    'pydantic',
]

# Sammle alle Submodule
hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('alembic')
hiddenimports += collect_submodules('reportlab')

# Data Files - Templates, Static Files, Migrations, etc.
datas = []

# Templates hinzufügen
datas += [(os.path.join(project_root, 'app/templates'), 'app/templates')]

# Static Files hinzufügen
datas += [(os.path.join(project_root, 'app/static'), 'app/static')]

# Alembic Migrations hinzufügen
datas += [(os.path.join(project_root, 'alembic'), 'alembic')]
datas += [(os.path.join(project_root, 'alembic.ini'), '.')]

# .env.example hinzufügen
datas += [(os.path.join(project_root, '.env.example'), '.')]

# Ruleset-Vorlagen (falls vorhanden)
if os.path.exists(os.path.join(project_root, 'rulesets')):
    datas += [(os.path.join(project_root, 'rulesets'), 'rulesets')]

# VERSION.txt hinzufügen
if os.path.exists(os.path.join(project_root, 'VERSION.txt')):
    datas += [(os.path.join(project_root, 'VERSION.txt'), '.')]

a = Analysis(
    ['desktop_app.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    icon=None,  # TODO: Icon hinzufügen falls vorhanden
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
