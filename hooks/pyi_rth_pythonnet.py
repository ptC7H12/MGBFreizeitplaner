"""
PyInstaller Runtime Hook für pythonnet

Wird VOR dem Import von pythonnet/clr ausgeführt und stellt sicher,
dass die Runtime-Pfade korrekt gesetzt sind.
"""
import sys
import os

# Finde PyInstaller's _MEIPASS
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Setze Umgebungsvariablen für pythonnet
pythonnet_runtime = os.path.join(base_path, 'pythonnet', 'runtime')
if os.path.exists(pythonnet_runtime):
    # Füge zum PATH hinzu damit DLLs gefunden werden
    if 'PATH' in os.environ:
        os.environ['PATH'] = pythonnet_runtime + os.pathsep + os.environ['PATH']
    else:
        os.environ['PATH'] = pythonnet_runtime

# Auch das pythonnet Hauptverzeichnis
pythonnet_dir = os.path.join(base_path, 'pythonnet')
if os.path.exists(pythonnet_dir):
    if 'PATH' in os.environ:
        os.environ['PATH'] = pythonnet_dir + os.pathsep + os.environ['PATH']
    else:
        os.environ['PATH'] = pythonnet_dir

# clr_loader Verzeichnis
clr_loader_dir = os.path.join(base_path, 'clr_loader')
if os.path.exists(clr_loader_dir):
    if 'PATH' in os.environ:
        os.environ['PATH'] = clr_loader_dir + os.pathsep + os.environ['PATH']
    else:
        os.environ['PATH'] = clr_loader_dir
