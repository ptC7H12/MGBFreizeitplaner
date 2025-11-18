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
    # Erkenne ob x64 oder x86
    is_64bit = platform.machine().endswith('64')

    # Setze WEBVIEW_PLATFORM Umgebungsvariable
    if is_64bit:
        os.environ['WEBVIEW_PLATFORM'] = 'win-x64'
    else:
        os.environ['WEBVIEW_PLATFORM'] = 'win-x86'

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
