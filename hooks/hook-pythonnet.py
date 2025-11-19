"""
PyInstaller Hook für pythonnet

Sammelt alle notwendigen DLLs und Daten für pythonnet/.NET Runtime.
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os
import sys

# Hidden imports
hiddenimports = collect_submodules('pythonnet')
hiddenimports += collect_submodules('clr_loader')
hiddenimports += [
    'clr',
    'clr_loader',
    'clr_loader.ffi',
    'clr_loader.util',
    'clr_loader.hostfxr',
    'clr_loader.netfx',
    'clr_loader.mono',
    'clr_loader.types',
]

# Data files
datas = collect_data_files('pythonnet')
datas += collect_data_files('clr_loader')

# Binaries
binaries = collect_dynamic_libs('pythonnet')
binaries += collect_dynamic_libs('clr_loader')

# Versuche pythonnet runtime Pfad zu finden und alle DLLs zu sammeln
try:
    import pythonnet
    pythonnet_path = os.path.dirname(pythonnet.__file__)

    # Sammle alle DLLs im pythonnet Verzeichnis
    for root, dirs, files in os.walk(pythonnet_path):
        for file in files:
            if file.endswith('.dll'):
                src = os.path.join(root, file)
                # Relativer Pfad von pythonnet_path
                rel_dir = os.path.relpath(os.path.dirname(src), pythonnet_path)
                if rel_dir == '.':
                    dest_dir = 'pythonnet'
                else:
                    dest_dir = os.path.join('pythonnet', rel_dir)
                binaries.append((src, dest_dir))

except ImportError:
    pass

# Versuche clr_loader Pfad zu finden
try:
    import clr_loader
    clr_loader_path = os.path.dirname(clr_loader.__file__)

    # Sammle alle DLLs im clr_loader Verzeichnis
    for root, dirs, files in os.walk(clr_loader_path):
        for file in files:
            if file.endswith('.dll'):
                src = os.path.join(root, file)
                rel_dir = os.path.relpath(os.path.dirname(src), clr_loader_path)
                if rel_dir == '.':
                    dest_dir = 'clr_loader'
                else:
                    dest_dir = os.path.join('clr_loader', rel_dir)
                binaries.append((src, dest_dir))

except ImportError:
    pass
