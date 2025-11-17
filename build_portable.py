#!/usr/bin/env python3
"""
Build-Skript für Portable Versionen von MGBFreizeitplaner

Erstellt ZIP-Archive für Windows, macOS und Linux mit allen
notwendigen Dateien für eine Standalone-Installation.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Projektverzeichnis
PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
RELEASE_DIR = PROJECT_ROOT / "releases"

# Version aus version.txt lesen
VERSION_FILE = PROJECT_ROOT / "version.txt"
try:
    VERSION = VERSION_FILE.read_text().strip()
except Exception:
    VERSION = "0.0.0"  # Fallback

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

# Startup-Skripte für verschiedene Plattformen
STARTUP_SCRIPTS = {
    "windows": ["start.bat", "start.ps1"],
    "macos": ["start.sh"],
    "linux": ["start.sh"],
}

# Plattform-spezifische Hinweise
PLATFORM_READMES = {
    "windows": """# MGBFreizeitplaner - Portable Version für Windows

## Schnellstart

1. **Doppelklick auf `start.bat`** (empfohlen für Anfänger)
   - Oder: Rechtsklick auf `start.ps1` → "Mit PowerShell ausführen"

2. Das Skript führt automatisch folgende Schritte aus:
   - Prüft Python-Installation
   - Erstellt virtuelle Umgebung (beim ersten Start)
   - Installiert Abhängigkeiten (beim ersten Start)
   - Startet die Anwendung

3. Browser öffnet automatisch unter: http://localhost:8000/auth

## Voraussetzungen

- **Python 3.11 oder höher** muss installiert sein
- Download: https://www.python.org/downloads/
- ⚠️ WICHTIG: Bei Installation "Add Python to PATH" aktivieren!

## Troubleshooting

### "Python ist nicht installiert"
→ Installiere Python 3.11+ von python.org
→ Achte auf "Add Python to PATH" bei der Installation

### PowerShell Execution Policy Fehler
→ Führe in PowerShell als Administrator aus:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
→ Oder verwende stattdessen start.bat

### Port 8000 bereits belegt
→ Beende andere Anwendungen auf Port 8000
→ Oder ändere PORT in .env Datei

### Firewall-Warnung
→ Klicke auf "Zugriff zulassen" wenn Windows Defender fragt

## Konfiguration

Bearbeite die `.env` Datei um Einstellungen anzupassen:
- PORT=8000           # Server-Port ändern
- DEBUG=false         # Debug-Modus aktivieren
- SECRET_KEY=...      # Sicherheitsschlüssel

## Portable Nutzung

Diese Version kann auf einem USB-Stick verwendet werden:
1. Kopiere den gesamten Ordner auf USB-Stick
2. Starte mit start.bat auf jedem Windows-PC (mit Python)
3. Datenbank (freizeit_kassen.db) wird im Ordner gespeichert

## Support

Bei Problemen: https://github.com/[YOUR_REPO]/issues
""",
    "macos": """# MGBFreizeitplaner - Portable Version für macOS

## Schnellstart

1. **Doppelklick auf `start.sh`**
   - Oder im Terminal: `./start.sh`

2. Das Skript führt automatisch folgende Schritte aus:
   - Prüft Python-Installation
   - Erstellt virtuelle Umgebung (beim ersten Start)
   - Installiert Abhängigkeiten (beim ersten Start)
   - Startet die Anwendung

3. Browser öffnet automatisch unter: http://localhost:8000/auth

## Voraussetzungen

- **Python 3.11 oder höher** muss installiert sein

### Python installieren:

**Option 1: Homebrew (empfohlen)**
```bash
brew install python@3.11
```

**Option 2: Von python.org**
https://www.python.org/downloads/macos/

## Troubleshooting

### "Python 3 ist nicht installiert"
→ Installiere Python 3.11+ mit Homebrew oder von python.org

### "Permission denied"
→ Mache das Skript ausführbar:
   chmod +x start.sh

### Xcode Command Line Tools
Falls Fehler bei Installation:
```bash
xcode-select --install
```

### Port 8000 bereits belegt
→ Beende andere Anwendungen auf Port 8000:
   lsof -ti:8000 | xargs kill
→ Oder ändere PORT in .env Datei

### Gatekeeper Warnung
→ Rechtsklick auf start.sh → "Öffnen"
→ Bestätige "Öffnen" im Dialog

## Konfiguration

Bearbeite die `.env` Datei um Einstellungen anzupassen:
- PORT=8000           # Server-Port ändern
- DEBUG=false         # Debug-Modus aktivieren
- SECRET_KEY=...      # Sicherheitsschlüssel

## Portable Nutzung

Diese Version kann auf einem USB-Stick verwendet werden:
1. Kopiere den gesamten Ordner auf USB-Stick
2. Starte mit ./start.sh auf jedem Mac (mit Python)
3. Datenbank (freizeit_kassen.db) wird im Ordner gespeichert

## Support

Bei Problemen: https://github.com/[YOUR_REPO]/issues
""",
    "linux": """# MGBFreizeitplaner - Portable Version für Linux

## Schnellstart

1. **Im Terminal ausführen: `./start.sh`**
   - Oder Doppelklick (falls File Manager Skripte ausführen kann)

2. Das Skript führt automatisch folgende Schritte aus:
   - Prüft Python-Installation
   - Erstellt virtuelle Umgebung (beim ersten Start)
   - Installiert Abhängigkeiten (beim ersten Start)
   - Startet die Anwendung

3. Browser öffnet automatisch unter: http://localhost:8000/auth

## Voraussetzungen

- **Python 3.11 oder höher** muss installiert sein

### Python installieren:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Fedora:**
```bash
sudo dnf install python3.11
```

**Arch Linux:**
```bash
sudo pacman -S python
```

## Troubleshooting

### "Python 3 ist nicht installiert"
→ Installiere Python 3.11+ mit deinem Paketmanager

### "Permission denied"
→ Mache das Skript ausführbar:
   chmod +x start.sh

### Fehlende venv-Module
→ Installiere python3-venv:
   sudo apt install python3.11-venv  # Ubuntu/Debian

### Port 8000 bereits belegt
→ Beende andere Anwendungen auf Port 8000:
   lsof -ti:8000 | xargs kill -9
→ Oder ändere PORT in .env Datei

### Build-Tools fehlen (für native Extensions)
→ Installiere Build-Essentials:
   sudo apt install build-essential python3-dev  # Ubuntu/Debian

## Konfiguration

Bearbeite die `.env` Datei um Einstellungen anzupassen:
- PORT=8000           # Server-Port ändern
- DEBUG=false         # Debug-Modus aktivieren
- SECRET_KEY=...      # Sicherheitsschlüssel

## Portable Nutzung

Diese Version kann auf einem USB-Stick verwendet werden:
1. Kopiere den gesamten Ordner auf USB-Stick
2. Starte mit ./start.sh auf jedem Linux-System (mit Python)
3. Datenbank (freizeit_kassen.db) wird im Ordner gespeichert

## Support

Bei Problemen: https://github.com/[YOUR_REPO]/issues
"""
}


def clean_build_dirs():
    """Entfernt alte Build-Verzeichnisse"""
    print("🧹 Räume alte Build-Verzeichnisse auf...")
    for dir_path in [BUILD_DIR, RELEASE_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    BUILD_DIR.mkdir(parents=True)
    RELEASE_DIR.mkdir(parents=True)
    print("✅ Aufgeräumt!")


def copy_project_files(target_dir: Path):
    """Kopiert Projektdateien in Zielverzeichnis"""
    print(f"📋 Kopiere Projektdateien nach {target_dir.name}...")

    for item in INCLUDE_ITEMS:
        source = PROJECT_ROOT / item
        if not source.exists():
            print(f"⚠️  Warnung: {item} nicht gefunden, überspringe...")
            continue

        # Berechne Zielpfad
        dest = target_dir / item

        if source.is_dir():
            # Kopiere Verzeichnis
            shutil.copytree(source, dest, dirs_exist_ok=True)
            print(f"  ✓ {item}")
        else:
            # Kopiere Datei
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"  ✓ {item}")


def create_platform_package(platform: str):
    """Erstellt Paket für spezifische Plattform"""
    print(f"\n📦 Erstelle Paket für {platform.upper()}...")

    # Erstelle Plattform-spezifisches Verzeichnis
    platform_dir = BUILD_DIR / f"MGBFreizeitplaner-{platform}"
    platform_dir.mkdir(parents=True, exist_ok=True)

    # Kopiere Projektdateien
    copy_project_files(platform_dir)

    # Kopiere Startup-Skripte für diese Plattform
    print(f"📝 Füge Startup-Skripte hinzu...")
    for script in STARTUP_SCRIPTS.get(platform, []):
        source = PROJECT_ROOT / script
        if source.exists():
            dest = platform_dir / script
            shutil.copy2(source, dest)
            # Mache ausführbar (für Unix-Systeme)
            if script.endswith('.sh'):
                dest.chmod(0o755)
            print(f"  ✓ {script}")

    # Erstelle plattform-spezifische README
    readme_content = PLATFORM_READMES.get(platform, "")
    if readme_content:
        readme_path = platform_dir / "QUICKSTART.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"  ✓ QUICKSTART.md")

    # Erstelle ZIP-Archiv
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"MGBFreizeitplaner-{VERSION}-{platform}-portable-{timestamp}.zip"
    zip_path = RELEASE_DIR / zip_name

    print(f"🗜️  Erstelle ZIP-Archiv: {zip_name}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(platform_dir):
            # Überspringe __pycache__ und andere Python-Cache-Dateien
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache']]

            for file in files:
                if file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname)

    # Dateigröße anzeigen
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ {zip_name} erstellt ({size_mb:.2f} MB)")

    return zip_path


def create_all_packages():
    """Erstellt Pakete für alle Plattformen"""
    print("\n" + "="*60)
    print("🚀 MGBFreizeitplaner - Portable Build")
    print(f"📌 Version: {VERSION}")
    print("="*60 + "\n")

    # Aufräumen
    clean_build_dirs()

    # Erstelle Pakete für jede Plattform
    created_packages = []
    for platform in ["windows", "macos", "linux"]:
        try:
            zip_path = create_platform_package(platform)
            created_packages.append((platform, zip_path))
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des {platform}-Pakets: {e}")

    # Zusammenfassung
    print("\n" + "="*60)
    print("✨ Build abgeschlossen!")
    print("="*60)
    print(f"\n📁 Release-Verzeichnis: {RELEASE_DIR.absolute()}\n")

    for platform, zip_path in created_packages:
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {platform.upper()}: {zip_path.name} ({size_mb:.2f} MB)")

    print("\n💡 Nächste Schritte:")
    print("  1. Teste die ZIP-Archive auf den jeweiligen Plattformen")
    print("  2. Lade sie auf GitHub Releases hoch")
    print("  3. Aktualisiere die README mit Download-Links")
    print()


if __name__ == "__main__":
    create_all_packages()
