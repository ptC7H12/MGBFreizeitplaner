"""
Desktop-Anwendung für MGBFreizeitplaner mit PyWebView

Diese Datei startet die FastAPI-Anwendung in einem Desktop-Fenster
ohne dass ein externer Browser geöffnet werden muss.
"""
import sys
import os
import platform
from pathlib import Path

# PyInstaller Fix für WebView2 DLLs
# Muss VOR dem Import von webview ausgeführt werden
if getattr(sys, 'frozen', False):
    # Wir laufen als PyInstaller Bundle
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

    # Erkenne Architektur
    machine = platform.machine().lower()
    if machine in ('amd64', 'x86_64'):
        arch = 'win-x64'
    elif machine in ('x86', 'i386', 'i686'):
        arch = 'win-x86'
    elif machine in ('arm64', 'aarch64'):
        arch = 'win-arm64'
    else:
        arch = 'win-x64'  # Fallback

    # Setze Umgebungsvariablen für webview
    os.environ['WEBVIEW_PLATFORM'] = arch

    # Patch webview.util.interop_dll_path bevor webview importiert wird
    import importlib.util

    # Finde webview Modul
    spec = importlib.util.find_spec('webview.util')
    if spec and spec.origin:
        # Lade webview.util
        import webview.util

        # Original-Funktion speichern
        original_interop_dll_path = webview.util.interop_dll_path

        # Neue Funktion definieren
        def patched_interop_dll_path(platform_name):
            """Patched version die mit PyInstaller Bundle funktioniert"""
            dll_name = f'{platform_name}'

            # Versuche DLL im PyInstaller Bundle zu finden
            possible_paths = [
                os.path.join(base_path, 'webview', 'lib', 'runtimes', dll_name, 'native'),
                os.path.join(base_path, 'webview', 'lib', dll_name),
                os.path.join(base_path, dll_name),
            ]

            for path in possible_paths:
                dll_file = os.path.join(path, 'WebView2Loader.dll')
                if os.path.exists(dll_file):
                    return path

            # Fallback zur Original-Funktion
            try:
                return original_interop_dll_path(platform_name)
            except:
                # Wenn alles fehlschlägt, verwende arch-Variable
                fallback_path = os.path.join(base_path, 'webview', 'lib', 'runtimes', arch, 'native')
                if os.path.exists(fallback_path):
                    return fallback_path
                raise FileNotFoundError(f'Cannot find WebView2Loader.dll for {platform_name}')

        # Ersetze die Funktion
        webview.util.interop_dll_path = patched_interop_dll_path

import webview
import threading
import uvicorn
import time
import socket
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_free_port(start_port=8000, max_attempts=10):
    """Findet einen freien Port, falls der Standard-Port belegt ist"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Konnte keinen freien Port zwischen {start_port} und {start_port + max_attempts} finden")


class ServerThread(threading.Thread):
    """Thread für den FastAPI-Server"""

    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.server = None
        self.started = threading.Event()

    def run(self):
        """Startet den Uvicorn-Server"""
        try:
            logger.info(f"Starte FastAPI-Server auf {self.host}:{self.port}")

            # Konfiguration für Uvicorn
            config = uvicorn.Config(
                "app.main:app",
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True
            )
            self.server = uvicorn.Server(config)

            # Signal dass Server bereit ist
            self.started.set()

            # Server starten (blockiert bis shutdown)
            self.server.run()

        except Exception as e:
            logger.error(f"Fehler beim Starten des Servers: {e}", exc_info=True)
            self.started.set()  # Auch bei Fehler signalisieren

    def stop(self):
        """Stoppt den Server gracefully"""
        if self.server:
            logger.info("Beende FastAPI-Server...")
            self.server.should_exit = True


def wait_for_server(host, port, timeout=30):
    """Wartet bis der Server verfügbar ist"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                logger.info(f"Server ist verfügbar auf {host}:{port}")
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def on_closing():
    """Callback wenn das Fenster geschlossen wird"""
    logger.info("Anwendung wird beendet...")
    return True


def main():
    """Hauptfunktion - startet Server und Desktop-Fenster"""

    # Arbeitsverzeichnis auf Projektroot setzen
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)

    # Freien Port finden
    try:
        port = find_free_port()
        host = "127.0.0.1"
        logger.info(f"Verwende Port {port}")
    except RuntimeError as e:
        logger.error(f"Fehler: {e}")
        sys.exit(1)

    # Server in separatem Thread starten
    server_thread = ServerThread(host, port)
    server_thread.start()

    # Warten bis Server gestartet ist
    server_thread.started.wait(timeout=5)

    # Warten bis Server verfügbar ist
    if not wait_for_server(host, port):
        logger.error("Server konnte nicht gestartet werden!")
        sys.exit(1)

    # Desktop-Fenster erstellen und anzeigen
    logger.info("Öffne Desktop-Fenster...")

    window = webview.create_window(
        title='MGBFreizeitplaner - Freizeit-Kassen-System',
        url=f'http://{host}:{port}',
        width=1400,
        height=900,
        resizable=True,
        frameless=False,
        easy_drag=True,
        min_size=(800, 600)
    )

    # Event-Handler für Fenster-Schließen registrieren
    window.events.closing += on_closing

    # WebView starten (blockiert bis Fenster geschlossen wird)
    webview.start(debug=False)

    # Nach dem Schließen des Fensters: Server beenden
    logger.info("Fenster geschlossen, beende Server...")
    server_thread.stop()

    # Kurz warten damit Server sauber herunterfahren kann
    time.sleep(1)

    logger.info("Anwendung beendet.")


if __name__ == "__main__":
    main()
