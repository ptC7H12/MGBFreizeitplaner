#!/usr/bin/env python3
"""
Build-Skript für Standalone Portable Versionen von MGBFreizeitplaner

Erstellt vollständig eigenständige ZIP-Archive mit embedded Python
für Windows, macOS und Linux - KEINE Python-Installation erforderlich!
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime

# Projektverzeichnis
PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
RELEASE_DIR = PROJECT_ROOT / "releases"
DOWNLOAD_CACHE = PROJECT_ROOT / ".download_cache"

# Version aus version.txt lesen
VERSION_FILE = PROJECT_ROOT / "version.txt"
try:
    VERSION = VERSION_FILE.read_text().strip()
except Exception:
    VERSION = "0.0.0"  # Fallback

# Python Versionen für embedded/standalone builds
PYTHON_VERSIONS = {
    "windows": {
        "version": "3.11.9",
        "url": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip",
        "size_mb": 10,
        "pip_url": "https://bootstrap.pypa.io/get-pip.py"
    },
    "macos": {
        "version": "3.11.9",
        # Python Standalone Builds von Gregory Szorc
        "url": "https://github.com/indygreg/python-build-standalone/releases/download/20240107/cpython-3.11.7+20240107-x86_64-apple-darwin-install_only.tar.gz",
        "size_mb": 40,
        "arch": "x86_64"
    },
    "linux": {
        "version": "3.11.9",
        "url": "https://github.com/indygreg/python-build-standalone/releases/download/20240107/cpython-3.11.7+20240107-x86_64-unknown-linux-gnu-install_only.tar.gz",
        "size_mb": 45,
        "arch": "x86_64"
    }
}

# Dateien und Ordner, die inkludiert werden sollen
INCLUDE_ITEMS = [
    "app/",
    "rulesets/",
    "seed_data.py",
    "requirements.txt",
    "version.txt",
    ".env.example",
    "README.md",
]

# Startup-Skripte
STARTUP_SCRIPTS = {
    "windows": ["start_embedded.bat"],
    "macos": ["start_embedded.sh"],
    "linux": ["start_embedded.sh"],
}


def download_file(url: str, destination: Path, description: str = "Datei"):
    """Lädt eine Datei mit Fortschrittsanzeige herunter"""
    print(f"📥 Lade {description} herunter...")
    print(f"   URL: {url}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # SSL context für Downloads
    ssl_context = ssl.create_default_context()

    # Request mit User-Agent Header (GitHub requires this)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, context=ssl_context) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0

            with open(destination, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break

                    downloaded += len(buffer)
                    f.write(buffer)

                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')

        print()  # Neue Zeile nach Download
        print(f"✅ Download abgeschlossen: {destination.name}")
        return True

    except Exception as e:
        print(f"\n❌ Fehler beim Download: {e}")
        return False


def extract_archive(archive_path: Path, destination: Path, archive_type: str = "zip"):
    """Entpackt ein Archiv"""
    print(f"📦 Entpacke {archive_path.name}...")

    destination.mkdir(parents=True, exist_ok=True)

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(destination)
        elif archive_type in ["tar.gz", "tgz"]:
            import tarfile
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(destination)

        print(f"✅ Entpackt nach: {destination}")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Entpacken: {e}")
        return False


def setup_embedded_python_windows(platform_dir: Path) -> bool:
    """Richtet embedded Python für Windows ein"""
    print("\n🐍 Richte embedded Python für Windows ein...")

    python_info = PYTHON_VERSIONS["windows"]
    python_dir = platform_dir / "python"

    # Download Python embeddable
    cache_file = DOWNLOAD_CACHE / f"python-{python_info['version']}-embed-amd64.zip"

    if not cache_file.exists():
        if not download_file(python_info["url"], cache_file, f"Python {python_info['version']} Embeddable"):
            return False
    else:
        print(f"✅ Verwende gecachte Datei: {cache_file.name}")

    # Entpacke Python
    if not extract_archive(cache_file, python_dir):
        return False

    # Download get-pip.py
    pip_installer = python_dir / "get-pip.py"
    if not download_file(python_info["pip_url"], pip_installer, "pip installer"):
        return False

    # Aktiviere site-packages (wichtig für pip)
    # Windows embedded Python hat standardmäßig site-packages deaktiviert
    pth_files = list(python_dir.glob("python*._pth"))
    if pth_files:
        pth_file = pth_files[0]
        content = pth_file.read_text()
        # Uncomment "import site" Zeile
        content = content.replace("#import site", "import site")

        # Füge notwendige Pfade hinzu (wie in build_standalone_windows.py)
        if "Lib\\site-packages" not in content:
            content += "\nLib\\site-packages\n"
        # Füge Parent-Directory hinzu (wo app/ liegt)
        if ".." not in content:
            content += "..\n"

        pth_file.write_text(content)
        print(f"✅ Site-packages aktiviert und Pfade konfiguriert in {pth_file.name}")

    print("✅ Embedded Python für Windows eingerichtet")
    return True


def setup_embedded_python_unix(platform_dir: Path, platform: str) -> bool:
    """Richtet embedded Python für macOS/Linux ein"""
    print(f"\n🐍 Richte standalone Python für {platform} ein...")

    python_info = PYTHON_VERSIONS[platform]
    python_dir = platform_dir / "python"

    # Erstelle Cache-Dateiname
    url_parts = python_info["url"].split("/")
    cache_filename = url_parts[-1]
    cache_file = DOWNLOAD_CACHE / cache_filename

    if not cache_file.exists():
        if not download_file(python_info["url"], cache_file, f"Python Standalone für {platform}"):
            return False
    else:
        print(f"✅ Verwende gecachte Datei: {cache_file.name}")

    # Entpacke Python
    if not extract_archive(cache_file, python_dir, "tar.gz"):
        return False

    # Python Standalone Builds haben die Struktur: python/install/...
    # Wir müssen das richtige Verzeichnis finden
    install_dir = python_dir / "python" / "install"
    if install_dir.exists():
        # Verschiebe Inhalte eine Ebene hoch
        temp_dir = python_dir.parent / "temp_python"
        shutil.move(str(install_dir), str(temp_dir))
        shutil.rmtree(python_dir)
        shutil.move(str(temp_dir), str(python_dir))

    print(f"✅ Standalone Python für {platform} eingerichtet")
    return True


def install_dependencies(platform_dir: Path, platform: str) -> bool:
    """Installiert Python-Dependencies in embedded Python"""
    print(f"\n📦 Installiere Dependencies für {platform}...")

    python_dir = platform_dir / "python"
    requirements = PROJECT_ROOT / "requirements.txt"

    if platform == "windows":
        python_exe = python_dir / "python.exe"
        pip_cmd = f'"{python_exe}" -m pip install -r "{requirements}" --no-warn-script-location'
    else:
        python_exe = python_dir / "bin" / "python3"
        pip_cmd = f'"{python_exe}" -m pip install -r "{requirements}"'

    # Erst pip installieren (für Windows embedded)
    if platform == "windows":
        get_pip = python_dir / "get-pip.py"
        print("  Installing pip...")
        install_pip_cmd = f'"{python_exe}" "{get_pip}" --no-warn-script-location'
        result = os.system(install_pip_cmd)
        if result != 0:
            print("❌ Pip-Installation fehlgeschlagen")
            return False

    # Dependencies installieren
    print(f"  Installing requirements from {requirements.name}...")
    result = os.system(pip_cmd)

    if result != 0:
        print("❌ Dependency-Installation fehlgeschlagen")
        return False

    print("✅ Dependencies installiert")
    return True


def create_startup_script_windows(platform_dir: Path):
    """Erstellt Startup-Skript für Windows mit embedded Python"""
    script_content = '''@echo off
REM ============================================
REM  MGBFreizeitplaner - Standalone Version
REM  KEINE Python-Installation erforderlich!
REM ============================================

echo.
echo ========================================
echo   MGBFreizeitplaner
echo   Freizeit-Kassen-System
echo ========================================
echo.

REM Wechsle ins Skript-Verzeichnis
cd /d "%~dp0"

REM Verwende embedded Python
set PYTHON_EXE=%~dp0python\\python.exe

if not exist "%PYTHON_EXE%" (
    echo [FEHLER] Embedded Python nicht gefunden!
    echo Bitte stelle sicher, dass der Ordner vollstaendig entpackt wurde.
    pause
    exit /b 1
)

echo [INFO] Verwende embedded Python

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Erstelle .env Datei aus Vorlage...
        copy .env.example .env >nul
    )
)

REM Start the application
echo.
echo ========================================
echo   Starte Anwendung...
echo ========================================
echo.
echo Druecke Ctrl+C um die Anwendung zu beenden
echo.

REM Oeffne Browser sofort mit Ladeseite
start "" "%~dp0app\\static\\loading_browser.html"

REM Starte Server
"%PYTHON_EXE%" -m app.main

REM If app exits, wait for user input
if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung wurde mit Fehler beendet!
    pause
)
'''

    script_path = platform_dir / "start_embedded.bat"
    script_path.write_text(script_content, encoding='utf-8')
    print(f"✅ Startup-Skript erstellt: {script_path.name}")


def create_startup_script_unix(platform_dir: Path, platform: str):
    """Erstellt Startup-Skript für macOS/Linux mit embedded Python"""
    script_content = '''#!/bin/bash
# ============================================
#  MGBFreizeitplaner - Standalone Version
#  KEINE Python-Installation erforderlich!
# ============================================

# Color definitions
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   MGBFreizeitplaner${NC}"
echo -e "${CYAN}   Freizeit-Kassen-System${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Wechsle ins Skript-Verzeichnis
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verwende embedded Python
PYTHON_EXE="$SCRIPT_DIR/python/bin/python3"

if [ ! -f "$PYTHON_EXE" ]; then
    echo -e "${RED}[FEHLER] Embedded Python nicht gefunden!${NC}"
    echo "Bitte stelle sicher, dass der Ordner vollständig entpackt wurde."
    read -p "Drücke Enter zum Beenden"
    exit 1
fi

echo -e "${GREEN}[INFO] Verwende embedded Python${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[INFO] Erstelle .env Datei aus Vorlage...${NC}"
        cp .env.example .env
    fi
fi

# Start the application
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Starte Anwendung...${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Drücke Ctrl+C um die Anwendung zu beenden${NC}"
echo ""

# Oeffne Browser sofort mit Ladeseite
if command -v xdg-open &> /dev/null; then
    xdg-open "$SCRIPT_DIR/app/static/loading_browser.html" &
elif command -v open &> /dev/null; then
    open "$SCRIPT_DIR/app/static/loading_browser.html" &
fi

# Starte Server
"$PYTHON_EXE" -m app.main

# If app exits with error
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[FEHLER] Anwendung wurde mit Fehler beendet!${NC}"
    read -p "Drücke Enter zum Beenden"
fi
'''

    script_path = platform_dir / "start_embedded.sh"
    script_path.write_text(script_content, encoding='utf-8')
    script_path.chmod(0o755)
    print(f"✅ Startup-Skript erstellt: {script_path.name}")


def clean_build_dirs():
    """Entfernt nur Dateien, die von diesem Skript erstellt wurden"""
    print("🧹 Räume alte Embedded-Standalone-Builds auf...")

    # Lösche nur die embedded-standalone-spezifischen Build-Ordner
    for platform in ["windows", "macos", "linux"]:
        # Dieses Skript erstellt: MGBFreizeitplaner-{platform}-standalone
        embedded_build_dir = BUILD_DIR / f"MGBFreizeitplaner-{platform}-standalone"
        if embedded_build_dir.exists():
            shutil.rmtree(embedded_build_dir)
            print(f"  ✓ Entfernt: {embedded_build_dir.name}")

    # Lösche nur embedded-standalone Release-Dateien
    # (nicht die Windows-Standalone vom anderen Skript, die hat großes W im Ordnernamen)
    if RELEASE_DIR.exists():
        for platform in ["windows", "macos", "linux"]:
            for release_file in RELEASE_DIR.glob(f"MGBFreizeitplaner-*-{platform}-standalone-*.zip"):
                release_file.unlink()
                print(f"  ✓ Entfernt: {release_file.name}")

    # Erstelle Verzeichnisse falls nicht vorhanden
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_CACHE.mkdir(parents=True, exist_ok=True)

    print("✅ Aufgeräumt!")


def copy_project_files(target_dir: Path):
    """Kopiert Projektdateien in Zielverzeichnis"""
    print(f"📋 Kopiere Projektdateien nach {target_dir.name}...")

    for item in INCLUDE_ITEMS:
        source = PROJECT_ROOT / item
        if not source.exists():
            print(f"⚠️  Warnung: {item} nicht gefunden, überspringe...")
            continue

        dest = target_dir / item

        if source.is_dir():
            shutil.copytree(source, dest, dirs_exist_ok=True)
            print(f"  ✓ {item}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"  ✓ {item}")


def create_platform_package(platform: str) -> Path:
    """Erstellt vollständiges Standalone-Paket für eine Plattform"""
    print(f"\n{'='*60}")
    print(f"📦 Erstelle Standalone-Paket für {platform.upper()}")
    print(f"{'='*60}\n")

    # Erstelle Plattform-Verzeichnis
    platform_dir = BUILD_DIR / f"MGBFreizeitplaner-{platform}-standalone"
    platform_dir.mkdir(parents=True, exist_ok=True)

    # 1. Kopiere Projektdateien
    copy_project_files(platform_dir)

    # 2. Setup embedded Python
    if platform == "windows":
        if not setup_embedded_python_windows(platform_dir):
            raise Exception("Embedded Python Setup für Windows fehlgeschlagen")
    else:
        if not setup_embedded_python_unix(platform_dir, platform):
            raise Exception(f"Embedded Python Setup für {platform} fehlgeschlagen")

    # 3. Installiere Dependencies
    if not install_dependencies(platform_dir, platform):
        raise Exception("Dependency-Installation fehlgeschlagen")

    # 4. Erstelle Startup-Skript
    if platform == "windows":
        create_startup_script_windows(platform_dir)
    else:
        create_startup_script_unix(platform_dir, platform)

    # 5. README erstellen
    readme_content = f"""# MGBFreizeitplaner - Standalone Version für {platform.upper()}

## ✨ Keine Installation erforderlich!

Diese Version enthält alles, was Sie brauchen - einschließlich Python!

## Schnellstart

{'1. Doppelklick auf `start_embedded.bat`' if platform == 'windows' else '1. Doppelklick auf `start_embedded.sh` (oder im Terminal: `./start_embedded.sh`)'}
2. Fertig! Browser öffnet sich automatisch unter http://localhost:8000/auth

## Das wars!

Keine Python-Installation, keine Konfiguration, keine Kommandozeile erforderlich.
Einfach entpacken und starten!

## Technische Details

- Enthält: Python {PYTHON_VERSIONS[platform]['version']} (embedded)
- Größe: ~{PYTHON_VERSIONS[platform]['size_mb'] + 20} MB
- Portable: Kann auf USB-Stick verwendet werden
- Datenbank: Wird lokal im Ordner gespeichert

## Support

Bei Problemen: https://github.com/[YOUR_REPO]/issues
"""

    readme_path = platform_dir / "README_STANDALONE.md"
    readme_path.write_text(readme_content, encoding='utf-8')

    # 6. Erstelle ZIP-Archiv
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"MGBFreizeitplaner-{VERSION}-{platform}-standalone-{timestamp}.zip"
    zip_path = RELEASE_DIR / zip_name

    print(f"\n🗜️  Erstelle ZIP-Archiv: {zip_name}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(platform_dir):
            # Überspringe Cache-Dateien
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', '__pycache__']]

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname)

    # Dateigröße anzeigen
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ {zip_name} erstellt ({size_mb:.1f} MB)")

    return zip_path


def create_all_packages():
    """Erstellt Standalone-Pakete für alle Plattformen"""
    print("\n" + "="*60)
    print("🚀 MGBFreizeitplaner - Standalone Build (mit embedded Python)")
    print(f"📌 Version: {VERSION}")
    print("="*60 + "\n")

    print("⚠️  HINWEIS: Dieser Build lädt Python-Distributionen herunter")
    print("    Gesamtgröße: ~100-150 MB Downloads")
    print("    Dies kann einige Minuten dauern...\n")

    # Aufräumen
    clean_build_dirs()

    # Wähle Plattformen
    print("Wähle Plattformen:")
    print("  1 - Nur Windows")
    print("  2 - Nur macOS")
    print("  3 - Nur Linux")
    print("  4 - Alle Plattformen")

    choice = input("\nAuswahl (1-4) [Standard: 1]: ").strip() or "1"

    platform_map = {
        "1": ["windows"],
        "2": ["macos"],
        "3": ["linux"],
        "4": ["windows", "macos", "linux"]
    }

    selected_platforms = platform_map.get(choice, ["windows"])

    print(f"\n✅ Erstelle Pakete für: {', '.join(selected_platforms)}\n")

    # Erstelle Pakete
    created_packages = []
    for platform in selected_platforms:
        try:
            zip_path = create_platform_package(platform)
            created_packages.append((platform, zip_path))
        except Exception as e:
            print(f"\n❌ Fehler beim Erstellen des {platform}-Pakets: {e}")
            import traceback
            traceback.print_exc()

    # Zusammenfassung
    print("\n" + "="*60)
    print("✨ Build abgeschlossen!")
    print("="*60)
    print(f"\n📁 Release-Verzeichnis: {RELEASE_DIR.absolute()}\n")

    for platform, zip_path in created_packages:
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {platform.upper()}: {zip_path.name} ({size_mb:.1f} MB)")

    print("\n💡 Nächste Schritte:")
    print("  1. Teste die ZIP-Archive auf den jeweiligen Plattformen")
    print("  2. WICHTIG: Einfach entpacken und start_embedded Skript ausführen!")
    print("  3. Lade sie auf GitHub Releases hoch")
    print("  4. Aktualisiere die README mit Download-Links")
    print()


if __name__ == "__main__":
    try:
        create_all_packages()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
