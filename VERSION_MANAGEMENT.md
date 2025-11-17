# Versionsverwaltung für MGBFreizeitplaner

## 📌 Übersicht

Die Versionsnummer wird **zentral** in der Datei `version.txt` im Root-Verzeichnis gepflegt.
Alle anderen Teile der Anwendung lesen die Version aus dieser Datei.

## 🎯 Wie es funktioniert

### Zentrale Version
```
version.txt              ← Einzige Stelle, wo die Version steht
     ↓
app/version.py          ← Liest version.txt
     ↓
     ├── app/__init__.py         ← Importiert __version__
     ├── app/config.py           ← Nutzt Version in Settings
     ├── app/templates/*.html    ← Zeigt Version im Footer ({{ app_version }})
     └── build_*.py             ← Build-Skripte nutzen Version
```

### Automatische Integration

- **Templates**: Die Variable `{{ app_version }}` ist automatisch in allen Templates verfügbar
- **API**: Der `/health` Endpunkt gibt die Version zurück
- **Build-Skripte**: Alle Build-Skripte lesen die Version aus `version.txt`

## 🚀 Version aktualisieren

### Methode 1: Manuell (Einfach)

Bearbeite einfach die `version.txt` Datei:

```bash
echo "1.2.3" > version.txt
git add version.txt
git commit -m "Bump version to 1.2.3"
git tag -a v1.2.3 -m "Release 1.2.3"
git push && git push --tags
```

### Methode 2: Mit Skript (Automatisiert) ⭐ Empfohlen

Verwende das `update_version.py` Skript:

```bash
# Aktuelle Version anzeigen
python update_version.py

# Neue Version setzen (erstellt auch Git-Tag)
python update_version.py 1.2.3

# Nur Version setzen, kein Git-Tag
python update_version.py 1.2.3 --no-tag

# Version aus bestehendem Git-Tag übernehmen
python update_version.py from-git
```

## 📝 Versionsformat (Semantic Versioning)

Wir verwenden [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH[-SUFFIX]

Beispiele:
  1.0.0         ← Release-Version
  1.2.3         ← Mit neuen Features
  1.2.4-beta.1  ← Beta-Version
  2.0.0-rc.1    ← Release Candidate
```

### Wann welche Version erhöhen?

- **MAJOR** (1.x.x → 2.x.x): Breaking Changes, nicht rückwärtskompatibel
- **MINOR** (x.1.x → x.2.x): Neue Features, rückwärtskompatibel
- **PATCH** (x.x.1 → x.x.2): Bugfixes, keine neuen Features

## 🔄 Workflow für neue Releases

### Standard-Release

```bash
# 1. Änderungen machen und committen
git add .
git commit -m "Add new feature XYZ"

# 2. Version aktualisieren (z.B. von 1.0.0 → 1.1.0)
python update_version.py 1.1.0

# 3. Version committen
git add version.txt
git commit -m "Bump version to 1.1.0"

# 4. Pushen (inkl. Tags)
git push && git push origin v1.1.0
```

### Hotfix-Release

```bash
# 1. Bugfix committen
git add .
git commit -m "Fix critical bug in payment calculation"

# 2. Patch-Version erhöhen (1.1.0 → 1.1.1)
python update_version.py 1.1.1

# 3. Version committen und pushen
git add version.txt
git commit -m "Bump version to 1.1.1"
git push && git push origin v1.1.1
```

## 📦 Build-Prozess

Die Build-Skripte nutzen automatisch die Version aus `version.txt`:

```bash
# Portable Version bauen
python build_portable.py

# Windows Standalone bauen
python build_standalone_windows.py

# Multi-Platform Standalone bauen
python build_portable_embedded.py
```

Die erstellten ZIP-Dateien enthalten die Version im Dateinamen:
```
MGBFreizeitplaner-1.2.3-windows-portable-20240115-143022.zip
```

## ✅ Vorteile dieses Systems

1. **Eine zentrale Stelle** für die Versionsnummer
2. **Automatische Synchronisation** zwischen App, Templates und Build-Skripten
3. **Git-Tag Integration** für saubere Release-Historie
4. **Einfache Automatisierung** über Skript
5. **Keine Inkonsistenzen** mehr zwischen verschiedenen Dateien

## 🔍 Wo wird die Version überall verwendet?

- `version.txt` - Zentrale Quelle
- `app/version.py` - Liest die Version ein
- `app/__init__.py` - Exportiert `__version__`
- `app/config.py` - Settings.app_version
- `app/templates_config.py` - Registriert für Templates
- `app/templates/base.html` - Footer
- `app/templates/auth/landing.html` - Footer
- `app/main.py` - FastAPI App und Health-Check
- `build_portable.py` - Portable Builds
- `build_standalone_windows.py` - Windows Standalone
- `build_portable_embedded.py` - Multi-Platform Standalone

## 🛠️ Fehlerbehebung

### Version wird nicht aktualisiert?

1. Prüfe, ob `version.txt` existiert und lesbar ist
2. Starte die Anwendung neu (bei Entwicklung mit `reload=True` automatisch)
3. Prüfe die Logs auf Fehler

### Build-Skripte zeigen alte Version?

Die Version wird beim Start des Build-Skripts eingelesen. Stelle sicher, dass `version.txt` vor dem Build aktualisiert wurde.

## 📚 Weitere Informationen

- [Semantic Versioning](https://semver.org/)
- [Git Tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
