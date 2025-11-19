"""
Build-Skript für MGBFreizeitplaner Desktop-Anwendung

Erstellt eine standalone .exe für Windows mit PyInstaller.
"""
import warnings
# Unterdrücke pkg_resources Deprecation-Warnung von altgraph/PyInstaller
warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)

import subprocess
import sys
import shutil
from pathlib import Path
import platform


def check_python_version():
    """Prüft ob Python-Version kompatibel ist"""
    version = sys.version_info
    if version.major != 3 or version.minor < 11:
        print(f"[FEHLER] Python 3.11+ erforderlich, aber {version.major}.{version.minor} gefunden!")
        return False

    if version.minor == 13:
        print(f"\n[WARNUNG] Python 3.13 wird noch nicht vollständig unterstützt!")
        print(f"[WARNUNG] Einige Pakete können Probleme verursachen.")
        print(f"[WARNUNG] Empfohlen: Python 3.11 oder 3.12")
        print(f"[INFO] Build wird trotzdem versucht...\n")

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_platform():
    """Prüft ob Windows für .exe Build"""
    system = platform.system()
    if system != "Windows":
        print(f"[WARNUNG] Dieses Skript ist für Windows optimiert, läuft aber auf: {system}")
        print(f"[INFO] Für {system} wird trotzdem versucht zu bauen...")
    return system


def install_requirements():
    """Installiert alle Requirements inklusive PyInstaller und PyWebView"""
    print("\n[INFO] Installiere Build-Abhängigkeiten...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("[OK] Abhängigkeiten installiert")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FEHLER] Installation fehlgeschlagen: {e}")
        return False


def clean_build():
    """Löscht alte Build-Artefakte"""
    print("\n[INFO] Bereinige vorherige Builds...")
    dirs_to_clean = ["dist", "build"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"[OK] {dir_name}/ gelöscht")
    return True


def create_icon_if_missing():
    """Erstellt Icon falls nicht vorhanden"""
    icon_path = Path("app_icon.ico")
    if not icon_path.exists():
        print("\n[INFO] Icon nicht gefunden, erstelle Icon...")
        try:
            subprocess.run(
                [sys.executable, "create_icon.py"],
                check=True
            )
            if icon_path.exists():
                print("[OK] Icon erstellt")
                return True
            else:
                print("[WARNUNG] Icon konnte nicht erstellt werden")
                return False
        except subprocess.CalledProcessError as e:
            print(f"[WARNUNG] Icon-Erstellung fehlgeschlagen: {e}")
            return False
    else:
        print("\n[OK] Icon gefunden: app_icon.ico")
        return True


def run_pyinstaller():
    """Führt PyInstaller mit der Spec-Datei aus"""
    print("\n[INFO] Starte PyInstaller Build...")
    print("[INFO] Dies kann 5-10 Minuten dauern...\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "desktop_app.spec"],
            check=True
        )
        print("\n[OK] PyInstaller Build abgeschlossen")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FEHLER] PyInstaller Build fehlgeschlagen: {e}")
        return False


def verify_build():
    """Prüft ob die .exe erstellt wurde"""
    exe_path = Path("dist/MGBFreizeitplaner/MGBFreizeitplaner.exe")
    if not exe_path.exists():
        print(f"[FEHLER] .exe wurde nicht erstellt: {exe_path}")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] .exe erstellt: {exe_path}")
    print(f"[INFO] Größe: {size_mb:.1f} MB")
    return True


def copy_additional_files():
    """Kopiert zusätzliche Dateien ins Dist-Verzeichnis"""
    print("\n[INFO] Kopiere zusätzliche Dateien...")

    dist_dir = Path("dist/MGBFreizeitplaner")

    # .env erstellen wenn nicht vorhanden
    env_file = dist_dir / ".env"
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("[OK] .env erstellt")

    # README erstellen
    readme_content = """MGBFreizeitplaner - Desktop-Version
=====================================

STARTEN:
--------
Doppelklick auf: MGBFreizeitplaner.exe

Die Anwendung öffnet sich in einem eigenen Fenster.
Es wird KEIN Browser benötigt!

DATENBANK:
----------
Die SQLite-Datenbank (freizeit_kassen.db) wird automatisch
im gleichen Verzeichnis erstellt.

BACKUP:
-------
Sichern Sie regelmäßig das komplette Verzeichnis oder nutzen
Sie die Backup-Funktion in der Anwendung.

VERTEILUNG:
-----------
Der komplette Ordner "MGBFreizeitplaner" kann auf andere
Windows-PCs kopiert werden (keine Installation nötig).

SUPPORT:
--------
Bei Problemen erstellen Sie ein Issue auf GitHub:
https://github.com/ptC7H12/MGBFreizeitplaner
"""

    readme_file = dist_dir / "README.txt"
    readme_file.write_text(readme_content, encoding="utf-8")
    print("[OK] README.txt erstellt")
    return True


def main():
    """Hauptfunktion - orchestriert den Build-Prozess"""
    print("=" * 60)
    print("  MGBFreizeitplaner - Desktop Build")
    print("  Windows .exe erstellen mit PyInstaller")
    print("=" * 60)

    # Arbeitsverzeichnis ins Projektroot wechseln
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)

    # Checks
    if not check_python_version():
        sys.exit(1)

    system = check_platform()

    # Build-Prozess
    steps = [
        ("Requirements installieren", install_requirements),
        ("Build bereinigen", clean_build),
        ("Icon erstellen/prüfen", create_icon_if_missing),
        ("PyInstaller ausführen", run_pyinstaller),
        ("Build verifizieren", verify_build),
        ("Zusätzliche Dateien kopieren", copy_additional_files),
    ]

    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"  {step_name}...")
        print(f"{'='*60}")

        if not step_func():
            print(f"\n[FEHLER] Schritt fehlgeschlagen: {step_name}")
            sys.exit(1)

    # Erfolgsmeldung
    print("\n" + "=" * 60)
    print("  BUILD ERFOLGREICH!")
    print("=" * 60)
    print("\n[OK] Desktop-Anwendung wurde erstellt:")
    print("     dist/MGBFreizeitplaner/MGBFreizeitplaner.exe")
    print("\n[INFO] Der komplette Ordner 'dist/MGBFreizeitplaner/' kann")
    print("       auf andere Windows-PCs kopiert werden.")
    print("\n[INFO] Zum Testen:")
    print("       cd dist/MGBFreizeitplaner")
    print("       ./MGBFreizeitplaner.exe")
    print()


if __name__ == "__main__":
    main()
