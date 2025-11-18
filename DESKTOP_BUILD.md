# MGBFreizeitplaner - Desktop-Version

## Übersicht

Die Desktop-Version von MGBFreizeitplaner ist eine eigenständige Windows-Anwendung (.exe), die **ohne Browser** läuft. Sie verwendet PyWebView, um die FastAPI-Anwendung in einem nativen Desktop-Fenster anzuzeigen.

### Vorteile der Desktop-Version

✅ **Kein Browser erforderlich** - Läuft in eigenem Fenster
✅ **Einfache Installation** - Nur .exe starten, keine Python-Installation nötig
✅ **Portable** - Kompletter Ordner kopierbar
✅ **Offline-fähig** - Keine Internet-Verbindung erforderlich (außer für Ruleset-Downloads)
✅ **Besseres Desktop-Gefühl** - Native Fenster-Integration

## Technische Details

- **Framework**: PyWebView 5.3.1
- **Backend**: FastAPI (unverändert)
- **Build-Tool**: PyInstaller 6.11.1
- **Zielplattform**: Windows 10/11 (x64)
- **Größe**: Ca. 80-120 MB (inkl. Python-Runtime)

## Build-Anleitung

### Voraussetzungen

- Python 3.11 oder 3.12 (auf dem Build-System)
- Git (optional, für Clone)
- Windows 10 oder höher (für .exe Build)

### Schritt 1: Repository klonen (falls noch nicht vorhanden)

```bash
git clone https://github.com/ptC7H12/MGBFreizeitplaner.git
cd MGBFreizeitplaner
```

### Schritt 2: Build ausführen

**Option A - Windows Batch-Skript (empfohlen für Windows):**

```cmd
build_desktop_windows.bat
```

**Option B - Python-Skript (plattformübergreifend):**

```cmd
python build_desktop.py
```

Beide Skripte führen folgende Schritte aus:

1. Erstellen einer virtuellen Umgebung (falls nicht vorhanden)
2. Installation aller Dependencies (inkl. PyWebView + PyInstaller)
3. Bereinigung vorheriger Builds
4. PyInstaller-Build mit `desktop_app.spec`
5. Kopieren zusätzlicher Dateien (README, .env)
6. Verifizierung des Builds

### Schritt 3: Build testen

Nach erfolgreichem Build:

```cmd
cd dist\MGBFreizeitplaner
MGBFreizeitplaner.exe
```

Die Anwendung sollte sich in einem Desktop-Fenster öffnen.

## Build-Ausgabe

Nach dem Build befindet sich die fertige Anwendung in:

```
dist/
└── MGBFreizeitplaner/
    ├── MGBFreizeitplaner.exe    # Hauptanwendung
    ├── _internal/                # Abhängigkeiten, Templates, etc.
    ├── .env                      # Konfiguration
    ├── README.txt                # Benutzer-Dokumentation
    └── alembic.ini               # Datenbank-Migrationen
```

**Hinweis:** Der komplette Ordner `dist/MGBFreizeitplaner/` kann auf andere Windows-PCs kopiert werden.

## Verteilung

### Variante 1: ZIP-Archiv

Empfohlen für einfache Verteilung:

```cmd
cd dist
powershell Compress-Archive -Path MGBFreizeitplaner -DestinationPath MGBFreizeitplaner-Desktop-v1.0.zip
```

Nutzer müssen nur:
1. ZIP entpacken
2. `MGBFreizeitplaner.exe` starten

### Variante 2: Installer (fortgeschritten)

Für professionelle Verteilung kann ein Installer erstellt werden mit:

- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup**
- **WiX Toolset**

Beispiel mit NSIS (nicht im Scope dieses Projekts):

```nsis
; MGBFreizeitplaner.nsi
!define APP_NAME "MGBFreizeitplaner"
!define APP_VERSION "1.0.0"
OutFile "MGBFreizeitplaner-Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
...
```

## Entwicklung & Testing

### Entwicklungsmodus (ohne Build)

Für schnellere Iteration während der Entwicklung:

```bash
# Dependencies installieren
pip install -r requirements.txt

# Desktop-App direkt starten (ohne PyInstaller)
python desktop_app.py
```

Dies startet die Anwendung direkt aus dem Source-Code.

### Debugging

Bei Problemen mit der .exe:

1. **Console-Modus aktivieren** (in `desktop_app.spec`):
   ```python
   exe = EXE(
       ...
       console=True,  # Ändere False zu True
       ...
   )
   ```

2. **Neu bauen:**
   ```cmd
   pyinstaller desktop_app.spec
   ```

3. **Log-Ausgabe prüfen:**
   Die .exe gibt dann Debug-Informationen im Terminal aus.

## Architektur

### desktop_app.py

Hauptskript für die Desktop-Integration:

```
┌─────────────────────────────────────┐
│     desktop_app.py                  │
├─────────────────────────────────────┤
│  ┌────────────┐   ┌──────────────┐ │
│  │  Thread 1  │   │   Thread 2   │ │
│  │            │   │              │ │
│  │  Uvicorn   │   │  PyWebView   │ │
│  │  Server    │   │  Window      │ │
│  │            │   │              │ │
│  │ FastAPI    │◄──┤ http://      │ │
│  │ App        │   │ localhost    │ │
│  │ Port 8000  │   │ :8000        │ │
│  └────────────┘   └──────────────┘ │
└─────────────────────────────────────┘
```

**Features:**

- Automatische Port-Findung (falls 8000 belegt)
- Graceful Shutdown beim Fenster-Schließen
- Server-Verfügbarkeits-Check vor Fenster-Öffnung

### desktop_app.spec

PyInstaller-Konfiguration:

- **Hidden Imports**: Alle FastAPI, Uvicorn, SQLAlchemy Module
- **Data Files**: Templates, Static Files, Migrations
- **Excludes**: Unnötige Pakete (matplotlib, numpy, etc.)
- **UPX Compression**: Kleinere .exe-Größe
- **Console**: False (kein schwarzes Terminal-Fenster)

## Bekannte Probleme & Lösungen

### Problem: "Port 8000 already in use"

**Lösung**: Die App findet automatisch einen freien Port (8000-8010).

### Problem: ".exe ist zu groß (>200 MB)"

**Lösungen**:

1. **UPX aktivieren** (bereits in spec): `upx=True`
2. **Excludes erweitern** in `desktop_app.spec`:
   ```python
   excludes=[
       'matplotlib', 'numpy', 'pandas', 'scipy',
       'pytest', 'IPython', 'jupyter', 'tkinter'
   ]
   ```
3. **One-File-Build vermeiden** (langsamer Start)

### Problem: "Antivirus blockiert .exe"

**Ursache**: PyInstaller-gepackte .exe werden manchmal als verdächtig eingestuft.

**Lösungen**:

1. **Code-Signing**: Signieren Sie die .exe mit einem gültigen Zertifikat
2. **Whitelist**: Fügen Sie die .exe zur Antivirus-Whitelist hinzu
3. **VirusTotal-Scan**: Scannen und teilen Sie den Bericht

### Problem: "Templates nicht gefunden"

**Ursache**: Templates wurden nicht korrekt gepackt.

**Lösung**: Prüfen Sie in `desktop_app.spec`:

```python
datas += [(os.path.join(project_root, 'app/templates'), 'app/templates')]
```

Debugging mit `console=True` aktivieren und Logs prüfen.

## FAQ

**Q: Muss Python auf dem Ziel-PC installiert sein?**
A: Nein! Die .exe enthält eine embedded Python-Runtime.

**Q: Funktioniert das auch auf macOS/Linux?**
A: PyWebView ist plattformübergreifend, aber die .exe nur für Windows. Für macOS/Linux:
- macOS: `.app` Bundle erstellen
- Linux: AppImage oder .deb Package

**Q: Kann ich die .exe umbenennen?**
A: Ja, die .exe kann beliebig umbenannt werden.

**Q: Wo wird die Datenbank gespeichert?**
A: Im gleichen Verzeichnis wie die .exe: `freizeit_kassen.db`

**Q: Wie aktualisiere ich die Desktop-App?**
A: Kompletten Ordner durch neue Version ersetzen (Datenbank vorher sichern!).

**Q: Ist die Desktop-Version sicherer?**
A: Gleiche Sicherheit wie Web-Version (localhost-basiert). Für zusätzliche Sicherheit:
- Passwortschutz beim App-Start implementieren
- Datenbank-Verschlüsselung (SQLCipher)

## Roadmap

Mögliche zukünftige Verbesserungen:

- [ ] **Auto-Update-Funktion** (ähnlich wie Electron)
- [ ] **Installer-Paket** mit NSIS oder Inno Setup
- [ ] **System-Tray-Icon** mit Minimize-to-Tray
- [ ] **Passwortschutz** beim App-Start
- [ ] **Datenbank-Verschlüsselung**
- [ ] **macOS `.app` Bundle**
- [ ] **Linux AppImage**
- [ ] **Code-Signing** für Windows

## Support

Bei Problemen:

1. **GitHub Issues**: https://github.com/ptC7H12/MGBFreizeitplaner/issues
2. **Logs prüfen**: `console=True` in spec aktivieren
3. **Community**: Diskussionen im GitHub-Repo

## Lizenz

Siehe [LICENSE](LICENSE) im Hauptverzeichnis.
