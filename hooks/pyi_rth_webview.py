"""
PyInstaller Runtime Hook für PyWebView

Dieser Hook wird VOR dem Import von webview ausgeführt und
stellt sicher, dass die korrekte Plattform erkannt wird.
"""
import sys
import os
import platform

# Setze die Plattform basierend auf der tatsächlichen Architektur
if sys.platform == 'win32':
    # Erkenne Architektur mit verbesserter Logik
    machine = platform.machine().lower()
    if machine in ('amd64', 'x86_64'):
        arch = 'win-x64'
    elif machine in ('x86', 'i386', 'i686'):
        arch = 'win-x86'
    elif machine in ('arm64', 'aarch64'):
        arch = 'win-arm64'
    else:
        # Fallback basierend auf sys.maxsize
        arch = 'win-x64' if sys.maxsize > 2**32 else 'win-x86'

    # Setze WEBVIEW_PLATFORM Umgebungsvariable
    os.environ['WEBVIEW_PLATFORM'] = arch

    # Finde PyInstaller's _MEIPASS (temp directory wo files entpackt werden)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    # Stelle sicher dass webview lib Pfad im PATH ist
    webview_lib = os.path.join(base_path, 'webview', 'lib')
    if os.path.exists(webview_lib):
        # Füge zum PATH hinzu
        if 'Path' in os.environ:
            os.environ['Path'] += ';' + webview_lib
        else:
            os.environ['Path'] = webview_lib

    # Füge auch den architektur-spezifischen Pfad hinzu
    arch_lib = os.path.join(base_path, 'webview', 'lib', 'runtimes', arch, 'native')
    if os.path.exists(arch_lib):
        if 'Path' in os.environ:
            os.environ['Path'] += ';' + arch_lib
        else:
            os.environ['Path'] = arch_lib
