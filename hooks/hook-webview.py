"""
PyInstaller Hook für webview (pywebview)

Sammelt ALLE DLLs für alle Architekturen und stellt sicher,
dass die Verzeichnisstruktur korrekt erstellt wird.
Der Runtime Hook (pyi_rth_webview.py) wählt dann die richtige Architektur.
"""
from PyInstaller.utils.hooks import collect_data_files
import os
import sys

# Hidden imports für webview
hiddenimports = [
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'webview.platforms.edgehtml',
    'webview.util',
    'webview.window',
    'webview.menu',
    'webview.js',
    'webview.js.css',
    'clr',
    'pythonnet',
]

# Sammle data files und binaries
datas = []
binaries = []

try:
    # Finde webview-Installation
    import webview
    webview_path = os.path.dirname(webview.__file__)

    # Sammle ALLE WebView2Loader.dll für alle Architekturen
    if sys.platform == 'win32':
        architectures = ['win-x64', 'win-x86', 'win-arm64']

        for arch in architectures:
            dll_path = os.path.join(webview_path, 'lib', 'runtimes', arch, 'native', 'WebView2Loader.dll')
            if os.path.exists(dll_path):
                # Ziel-Pfad im bundle
                dest_dir = os.path.join('webview', 'lib', 'runtimes', arch, 'native')
                binaries.append((dll_path, dest_dir))

        # Andere DLLs im lib-Verzeichnis
        lib_dir = os.path.join(webview_path, 'lib')
        if os.path.exists(lib_dir):
            for root, dirs, files in os.walk(lib_dir):
                for file in files:
                    if file.endswith(('.dll', '.pyd')):
                        src = os.path.join(root, file)
                        # Relativer Pfad von webview_path
                        rel_dir = os.path.relpath(os.path.dirname(src), webview_path)
                        dest_dir = os.path.join('webview', rel_dir)
                        binaries.append((src, dest_dir))

    # Sammle andere notwendige data files
    for root, dirs, files in os.walk(webview_path):
        # Überspringe __pycache__
        if '__pycache__' in root:
            continue

        for file in files:
            # Nur non-binary data files
            if not file.endswith(('.dll', '.pyd', '.pyc', '.so')):
                src = os.path.join(root, file)
                rel_dir = os.path.relpath(os.path.dirname(src), webview_path)
                dest_dir = os.path.join('webview', rel_dir)
                datas.append((src, dest_dir))

except ImportError:
    pass
