"""
Desktop-Anwendung für MGBFreizeitplaner mit PyWebView

Diese Datei startet die FastAPI-Anwendung in einem Desktop-Fenster
ohne dass ein externer Browser geöffnet werden muss.
"""
import webview
import threading
import uvicorn
import time
import socket
import sys
import logging
from pathlib import Path

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
