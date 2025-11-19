"""
Desktop-Anwendung für MGBFreizeitplaner mit PyWebView

Diese Datei startet die FastAPI-Anwendung in einem Desktop-Fenster
ohne dass ein externer Browser geöffnet werden muss.
"""
import sys
import os
import platform
from pathlib import Path

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


def start_server_and_redirect(window, host, port):
    """Startet den Server im Hintergrund und leitet dann zur App weiter"""
    # Server in separatem Thread starten
    server_thread = ServerThread(host, port)
    server_thread.start()

    # Warten bis Server gestartet ist
    server_thread.started.wait(timeout=5)

    # Warten bis Server verfügbar ist
    if wait_for_server(host, port, timeout=60):
        logger.info("Server bereit - leite zur Anwendung weiter...")
        window.load_url(f'http://{host}:{port}')
    else:
        logger.error("Server konnte nicht gestartet werden!")
        # Fehlermeldung im Fenster anzeigen
        window.load_html("""
            <html>
            <body style="font-family: sans-serif; padding: 50px; text-align: center; background: #fee2e2;">
                <h1 style="color: #dc2626;">Fehler beim Starten</h1>
                <p>Der Server konnte nicht gestartet werden.</p>
                <p>Bitte starten Sie die Anwendung neu.</p>
            </body>
            </html>
        """)

    return server_thread


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

    # Pfad zur Ladescreen-HTML
    loading_screen = project_root / "app" / "static" / "loading.html"

    # Desktop-Fenster sofort mit Ladescreen erstellen und anzeigen
    logger.info("Öffne Desktop-Fenster mit Ladescreen...")

    window = webview.create_window(
        title='MGBFreizeitplaner - Freizeit-Kassen-System',
        url=loading_screen.as_uri(),
        width=1400,
        height=900,
        resizable=True,
        frameless=False,
        easy_drag=True,
        min_size=(800, 600),
        text_select=True  # Ermöglicht Text-Markierung und Kopieren
    )

    # Event-Handler für Fenster-Schließen registrieren
    window.events.closing += on_closing

    # Server-Thread-Referenz für späteren Zugriff
    server_thread_holder = [None]

    def on_loaded():
        """Callback wenn das Fenster geladen ist - startet Server im Hintergrund"""
        server_thread_holder[0] = start_server_and_redirect(window, host, port)

    # WebView starten - Server wird nach Fensteröffnung gestartet
    webview.start(on_loaded, debug=False)

    # Nach dem Schließen des Fensters: Server beenden
    logger.info("Fenster geschlossen, beende Server...")
    if server_thread_holder[0]:
        server_thread_holder[0].stop()

    # Kurz warten damit Server sauber herunterfahren kann
    time.sleep(1)

    logger.info("Anwendung beendet.")


if __name__ == "__main__":
    main()
