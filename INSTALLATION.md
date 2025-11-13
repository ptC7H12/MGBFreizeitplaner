# Installationsanleitung - MGBFreizeitplaner

Detaillierte Anleitung für die Installation auf Windows, macOS und Linux.

---

## 📥 Portable Version (Empfohlen)

Die einfachste Methode für Endanwender ohne technische Vorkenntnisse.

### Windows

#### Schritt 1: Python installieren

1. **Download Python 3.11 oder höher:**
   - Gehe zu https://www.python.org/downloads/
   - Lade die neueste Version für Windows herunter

2. **Installation:**
   - Starte den Installer
   - ⚠️ **WICHTIG:** Aktiviere das Häkchen **"Add Python to PATH"**
   - Klicke auf "Install Now"
   - Warte bis Installation abgeschlossen ist

3. **Prüfe Installation:**
   - Öffne CMD oder PowerShell
   - Tippe: `python --version`
   - Es sollte "Python 3.11.x" oder höher angezeigt werden

#### Schritt 2: MGBFreizeitplaner installieren

1. **Download:**
   - Lade die Datei `MGBFreizeitplaner-windows-YYYYMMDD.zip` herunter
   - Von: [GitHub Releases](../../releases)

2. **Entpacken:**
   - Rechtsklick auf ZIP-Datei → "Alle extrahieren..."
   - Wähle einen Zielordner (z.B. `C:\Programme\MGBFreizeitplaner`)
   - Klicke "Extrahieren"

3. **Starten:**
   - Öffne den entpackten Ordner
   - **Doppelklick auf `start.bat`**
   - Beim ersten Start:
     - Virtuelle Umgebung wird erstellt (~5 Sekunden)
     - Abhängigkeiten werden installiert (~1-2 Minuten)
   - Bei weiteren Starts: Sofortiger Start!

4. **Fertig!**
   - Browser öffnet automatisch: http://localhost:8000
   - Falls nicht: Öffne Browser manuell und gehe zu dieser Adresse

#### Troubleshooting Windows

**Problem: "Python ist nicht installiert"**
- Lösung: Python von python.org installieren
- Wichtig: "Add Python to PATH" aktivieren
- Nach Installation: CMD/PowerShell neu öffnen

**Problem: PowerShell Execution Policy Fehler**
- Bei `start.ps1`: PowerShell als Administrator öffnen
- Befehl ausführen:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- Alternative: Nutze `start.bat` statt `start.ps1`

**Problem: Windows Defender Firewall Warnung**
- Klicke "Zugriff zulassen" wenn gefragt
- Dies ist normal für lokale Server

**Problem: "Port 8000 ist bereits belegt"**
- Lösung 1: Schließe andere Programme die Port 8000 nutzen
- Lösung 2: Bearbeite `.env` und ändere `PORT=8000` zu `PORT=8080`

**Problem: Installation hängt bei "Installing dependencies"**
- Antivirus könnte pip-Installation blockieren
- Temporär Antivirus deaktivieren oder Ordner ausschließen
- Oder: Warte geduldig, erste Installation kann 5+ Minuten dauern

---

### macOS

#### Schritt 1: Python installieren

**Option A: Mit Homebrew (empfohlen)**

1. **Homebrew installieren** (falls noch nicht installiert):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python installieren:**
   ```bash
   brew install python@3.11
   ```

**Option B: Direkt von Python.org**

1. Gehe zu https://www.python.org/downloads/macos/
2. Lade Python 3.11+ für macOS herunter
3. Öffne .pkg Installer und folge den Anweisungen

**Prüfe Installation:**
```bash
python3 --version
```

#### Schritt 2: MGBFreizeitplaner installieren

1. **Download:**
   - Lade `MGBFreizeitplaner-macos-YYYYMMDD.zip` herunter
   - Von: [GitHub Releases](../../releases)

2. **Entpacken:**
   - Doppelklick auf ZIP-Datei (entpackt automatisch)
   - Oder im Terminal:
     ```bash
     unzip MGBFreizeitplaner-macos-YYYYMMDD.zip
     ```

3. **Starten:**
   - **Variante A (Doppelklick):**
     - Rechtsklick auf `start.sh` → "Öffnen"
     - Bei Gatekeeper-Warnung: Klicke "Öffnen"

   - **Variante B (Terminal):**
     ```bash
     cd MGBFreizeitplaner-macos
     ./start.sh
     ```

4. **Fertig!**
   - Browser öffnet automatisch: http://localhost:8000

#### Troubleshooting macOS

**Problem: "Python 3 ist nicht installiert"**
- Lösung: Installiere Python via Homebrew oder python.org
- macOS hat oft altes Python 2.7 - installiere Python 3.11+

**Problem: "Permission denied"**
- Skript ist nicht ausführbar
- Lösung:
  ```bash
  chmod +x start.sh
  ./start.sh
  ```

**Problem: Gatekeeper blockiert Skript**
- Lösung: Rechtsklick → "Öffnen" statt Doppelklick
- Oder in Terminal:
  ```bash
  xattr -d com.apple.quarantine start.sh
  ```

**Problem: "command line tools are required"**
- Installiere Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

**Problem: Port 8000 bereits belegt**
- Finde Prozess:
  ```bash
  lsof -i :8000
  ```
- Beende Prozess:
  ```bash
  lsof -ti:8000 | xargs kill
  ```
- Oder ändere Port in `.env`: `PORT=8080`

---

### Linux

#### Schritt 1: Python installieren

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Fedora:**
```bash
sudo dnf install python3.11 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

**openSUSE:**
```bash
sudo zypper install python311 python311-pip
```

**Prüfe Installation:**
```bash
python3 --version
```

#### Schritt 2: MGBFreizeitplaner installieren

1. **Download:**
   ```bash
   wget https://github.com/[YOUR_REPO]/releases/download/v1.0.0/MGBFreizeitplaner-linux-YYYYMMDD.zip
   ```

2. **Entpacken:**
   ```bash
   unzip MGBFreizeitplaner-linux-YYYYMMDD.zip
   cd MGBFreizeitplaner-linux
   ```

3. **Starten:**
   ```bash
   ./start.sh
   ```

4. **Fertig!**
   - Browser öffnet automatisch: http://localhost:8000

#### Troubleshooting Linux

**Problem: "Python 3 ist nicht installiert"**
- Lösung: Installiere mit Paketmanager (siehe oben)

**Problem: "Permission denied"**
- Mache Skript ausführbar:
  ```bash
  chmod +x start.sh
  ./start.sh
  ```

**Problem: "ensurepip is not available"**
- Python venv-Modul fehlt
- Ubuntu/Debian:
  ```bash
  sudo apt install python3.11-venv
  ```

**Problem: Compiler-Fehler bei Installation**
- Build-Tools fehlen
- Ubuntu/Debian:
  ```bash
  sudo apt install build-essential python3-dev
  ```
- Fedora:
  ```bash
  sudo dnf install gcc python3-devel
  ```

**Problem: Port 8000 bereits belegt**
- Finde Prozess:
  ```bash
  sudo lsof -i :8000
  # oder
  sudo netstat -tulpn | grep 8000
  ```
- Beende Prozess:
  ```bash
  sudo kill -9 <PID>
  ```
- Oder ändere Port in `.env`: `PORT=8080`

---

## 🐳 Docker Installation

### Voraussetzungen

- Docker Desktop (Windows/macOS)
- Docker Engine (Linux)

### Installation

**Windows/macOS:**
1. Installiere Docker Desktop von https://www.docker.com/products/docker-desktop/
2. Starte Docker Desktop
3. Klone Repository:
   ```bash
   git clone <repository-url>
   cd MGBFreizeitplaner
   ```
4. Starte mit:
   ```bash
   docker-compose up -d
   ```

**Linux:**
1. Installiere Docker:
   ```bash
   # Ubuntu/Debian
   sudo apt install docker.io docker-compose

   # Fedora
   sudo dnf install docker docker-compose
   ```
2. Starte Docker-Service:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
3. Klone Repository und starte:
   ```bash
   git clone <repository-url>
   cd MGBFreizeitplaner
   sudo docker-compose up -d
   ```

### Docker Troubleshooting

**Problem: "Cannot connect to Docker daemon"**
- Docker Desktop nicht gestartet (Windows/macOS)
- Docker Service nicht gestartet (Linux):
  ```bash
  sudo systemctl start docker
  ```

**Problem: Port 8000 bereits belegt**
- Ändere Port in `docker-compose.yml`:
  ```yaml
  ports:
    - "8080:8000"  # Ändere ersten Port
  ```

---

## 💻 Manuelle Installation (Entwickler)

Für Entwickler die am Code arbeiten möchten.

### Alle Plattformen

1. **Repository klonen:**
   ```bash
   git clone <repository-url>
   cd MGBFreizeitplaner
   ```

2. **Virtual Environment erstellen:**
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (CMD)
   python -m venv venv
   venv\Scripts\activate.bat

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfiguration:**
   ```bash
   cp .env.example .env
   # Bearbeite .env nach Bedarf
   ```

5. **Starten:**
   ```bash
   # Produktionsmodus
   python -m app.main

   # Entwicklungsmodus (Auto-Reload)
   uvicorn app.main:app --reload
   ```

---

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

```bash
# Server-Konfiguration
PORT=8000                    # Port für Webserver
HOST=0.0.0.0                # Listen auf allen Interfaces

# Datenbank
DATABASE_URL=sqlite:///./freizeit_kassen.db

# Security
SECRET_KEY=dein-geheimer-schlüssel-hier
DEBUG=false                 # true nur für Entwicklung!

# Optional: Logging
LOG_LEVEL=INFO
```

### Datenbank zurücksetzen

```bash
# Stoppe die Anwendung (Ctrl+C)

# Lösche Datenbank
rm freizeit_kassen.db  # Linux/macOS
del freizeit_kassen.db  # Windows

# Starte neu - neue DB wird erstellt
python -m app.main
```

---

## 📞 Support

Bei Problemen:

1. Prüfe [Troubleshooting](#troubleshooting-windows) für deine Plattform
2. Erstelle ein [Issue auf GitHub](../../issues)
3. Beschreibe:
   - Betriebssystem & Version
   - Python-Version (`python --version`)
   - Fehlermeldung (vollständiger Text)
   - Was hast du bereits versucht?

---

## 🔄 Updates

### Portable Version
1. Lade neue Version herunter
2. Entpacke in neuen Ordner
3. Kopiere alte `freizeit_kassen.db` in neuen Ordner (um Daten zu behalten)
4. Starte neu

### Docker
```bash
docker-compose pull
docker-compose up -d
```

### Manuelle Installation
```bash
git pull
pip install -r requirements.txt --upgrade
```
