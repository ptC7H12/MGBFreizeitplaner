"""
Build-Skript für MGBFreizeitplaner Desktop-Anwendung mit Nuitka

Erstellt eine standalone .exe für Windows durch Kompilierung zu C.
Nuitka bietet bessere Performance und Code-Schutz als PyInstaller.
"""
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


def check_nuitka():
    """Prüft ob Nuitka installiert ist"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"[OK] Nuitka gefunden: {version}")
            return True
        else:
            print("[FEHLER] Nuitka nicht gefunden!")
            return False
    except Exception as e:
        print(f"[FEHLER] Nuitka nicht gefunden: {e}")
        return False


def check_compiler():
    """Prüft ob ein C-Compiler verfügbar ist (nur Windows)"""
    if platform.system() != "Windows":
        return True

    # Nuitka sucht automatisch nach MSVC oder MinGW
    print("[INFO] C-Compiler wird beim Build automatisch erkannt...")
    print("[INFO] Falls kein Compiler gefunden wird:")
    print("       - Visual Studio Build Tools installieren")
    print("       - Oder: MinGW-w64 installieren")
    return True


def install_requirements():
    """Installiert alle Requirements inklusive Nuitka"""
    print("\n[INFO] Installiere Build-Abhängigkeiten...")
    try:
        # Installiere requirements.txt
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )

        # Installiere Nuitka falls nicht vorhanden
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "nuitka", "ordered-set", "zstandard"],
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
    dirs_to_clean = ["dist", "build", "MGBFreizeitplaner.build", "MGBFreizeitplaner.dist", "MGBFreizeitplaner.onefile-build"]
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


def run_nuitka():
    """Führt Nuitka Build aus"""
    print("\n[INFO] Starte Nuitka Build...")
    print("[INFO] Dies kann 10-30 Minuten dauern (Kompilierung zu C)...\n")

    # Nuitka Kommando zusammenstellen
    cmd = [
        sys.executable, "-m", "nuitka",

        # Standalone Mode
        "--standalone",

        # Windows-spezifisch
        "--windows-console-mode=disable",  # Kein Konsolen-Fenster

        # Icon
        "--windows-icon-from-ico=app_icon.ico",

        # Output
        "--output-dir=dist",
        "--output-filename=MGBFreizeitplaner.exe",

        # Includes - Pakete die eingebunden werden müssen
        "--include-package=app",
        "--include-package=webview",
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=sqlalchemy",
        "--include-package=alembic",
        "--include-package=jinja2",
        "--include-package=pydantic",
        "--include-package=reportlab",
        "--include-package=qrcode",
        "--include-package=openpyxl",
        "--include-package=yaml",
        "--include-package=email_validator",
        "--include-package=pythonnet",
        "--include-package=clr_loader",

        # Data Files
        "--include-data-dir=app/templates=app/templates",
        "--include-data-dir=app/static=app/static",
        "--include-data-dir=rulesets=rulesets",

        # Alembic falls vorhanden
        "--include-data-dir=alembic=alembic" if Path("alembic").exists() else "",

        # Entferne nicht benötigte Module (nicht-Windows Plattformen)
        "--nofollow-import-to=webview.platforms.android",
        "--nofollow-import-to=webview.platforms.gtk",
        "--nofollow-import-to=webview.platforms.cocoa",
        "--nofollow-import-to=webview.platforms.qt",
        "--nofollow-import-to=matplotlib",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=pandas",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=IPython",
        "--nofollow-import-to=jupyter",

        # Hauptdatei
        "desktop_app.py",
    ]

    # Leere Strings entfernen
    cmd = [c for c in cmd if c]

    try:
        subprocess.run(cmd, check=True)
        print("\n[OK] Nuitka Build abgeschlossen")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FEHLER] Nuitka Build fehlgeschlagen: {e}")
        return False


def verify_build():
    """Prüft ob die .exe erstellt wurde"""
    # Nuitka erstellt dist/desktop_app.dist/
    exe_path = Path("dist/desktop_app.dist/MGBFreizeitplaner.exe")

    # Alternative Pfade prüfen
    alt_paths = [
        Path("dist/MGBFreizeitplaner.exe"),
        Path("dist/desktop_app.dist/desktop_app.exe"),
    ]

    for path in [exe_path] + alt_paths:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"[OK] .exe erstellt: {path}")
            print(f"[INFO] Größe: {size_mb:.1f} MB")
            return True

    print(f"[FEHLER] .exe wurde nicht erstellt")
    print("[INFO] Prüfe dist/ Verzeichnis manuell")
    return False


def copy_additional_files():
    """Kopiert zusätzliche Dateien ins Dist-Verzeichnis"""
    print("\n[INFO] Kopiere zusätzliche Dateien...")

    # Finde das dist-Verzeichnis
    dist_dir = None
    for path in [Path("dist/desktop_app.dist"), Path("dist")]:
        if path.exists() and (path / "MGBFreizeitplaner.exe").exists():
            dist_dir = path
            break
        if path.exists() and (path / "desktop_app.exe").exists():
            dist_dir = path
            break

    if not dist_dir:
        dist_dir = Path("dist/desktop_app.dist")
        if not dist_dir.exists():
            dist_dir = Path("dist")

    # .env erstellen wenn nicht vorhanden
    env_file = dist_dir / ".env"
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("[OK] .env erstellt")

    # alembic.ini kopieren
    alembic_ini = Path("alembic.ini")
    if alembic_ini.exists():
        shutil.copy(alembic_ini, dist_dir / "alembic.ini")
        print("[OK] alembic.ini kopiert")

    # README erstellen
    readme_content = """MGBFreizeitplaner - Desktop-Version (Nuitka Build)
=================================================

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
Der komplette Ordner kann auf andere Windows-PCs kopiert
werden (keine Installation nötig).

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
    print("  MGBFreizeitplaner - Desktop Build mit Nuitka")
    print("  Kompiliert Python zu nativen C-Code")
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
        ("Nuitka prüfen", check_nuitka),
        ("Compiler prüfen", check_compiler),
        ("Build bereinigen", clean_build),
        ("Icon erstellen/prüfen", create_icon_if_missing),
        ("Nuitka ausführen", run_nuitka),
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
    print("     dist/desktop_app.dist/")
    print("\n[INFO] Der komplette Ordner 'dist/desktop_app.dist/' kann")
    print("       auf andere Windows-PCs kopiert werden.")
    print("\n[INFO] Zum Testen:")
    print("       cd dist/desktop_app.dist")
    print("       ./MGBFreizeitplaner.exe")
    print()


if __name__ == "__main__":
    main()
