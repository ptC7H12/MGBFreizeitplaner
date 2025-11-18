"""
PyInstaller Hook für webview (pywebview)

Sammelt nur die benötigten DLLs für die Zielarchitektur (x64)
und vermeidet Probleme mit mehrfachen Architektur-Varianten.
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
    'clr',
    'pythonnet',
]

# Sammle data files, aber nur für die richtige Architektur
datas = []
binaries = []

try:
    # Finde webview-Installation
    import webview
    webview_path = os.path.dirname(webview.__file__)

    # Sammle nur x64 DLLs für Windows 64-bit
    if sys.platform == 'win32':
        # WebView2Loader.dll für x64
        dll_x64 = os.path.join(webview_path, 'lib', 'runtimes', 'win-x64', 'native', 'WebView2Loader.dll')
        if os.path.exists(dll_x64):
            binaries.append((dll_x64, 'webview/lib/runtimes/win-x64/native'))

        # WebView2Loader.dll für x86 (falls benötigt)
        dll_x86 = os.path.join(webview_path, 'lib', 'runtimes', 'win-x86', 'native', 'WebView2Loader.dll')
        if os.path.exists(dll_x86):
            binaries.append((dll_x86, 'webview/lib/runtimes/win-x86/native'))

        # Andere webview DLLs im lib-Verzeichnis
        lib_dir = os.path.join(webview_path, 'lib')
        if os.path.exists(lib_dir):
            for root, dirs, files in os.walk(lib_dir):
                # Überspringe ARM64-Verzeichnisse
                if 'arm64' in root.lower():
                    continue

                for file in files:
                    if file.endswith(('.dll', '.pyd')):
                        src = os.path.join(root, file)
                        # Relativer Pfad von webview_path
                        rel_path = os.path.relpath(os.path.dirname(src), webview_path)
                        binaries.append((src, os.path.join('webview', rel_path)))

    # Sammle andere notwendige data files (aber keine DLLs)
    for root, dirs, files in os.walk(webview_path):
        # Überspringe ARM64 und unnötige Verzeichnisse
        if 'arm64' in root.lower() or '__pycache__' in root:
            continue

        for file in files:
            # Nur non-binary data files
            if not file.endswith(('.dll', '.pyd', '.pyc')):
                src = os.path.join(root, file)
                rel_path = os.path.relpath(os.path.dirname(src), webview_path)
                datas.append((src, os.path.join('webview', rel_path)))

except ImportError:
    pass
