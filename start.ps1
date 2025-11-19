# ============================================
#  MGBFreizeitplaner - PowerShell Startup Script
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MGBFreizeitplaner" -ForegroundColor Cyan
Write-Host "   Freizeit-Kassen-System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python Version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[FEHLER] Python ist nicht installiert!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bitte installiere Python 3.11 oder höher von:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WICHTIG: Wähle bei der Installation 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "[INFO] Erstelle virtuelle Python-Umgebung..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FEHLER] Konnte virtuelle Umgebung nicht erstellen!" -ForegroundColor Red
        Read-Host "Drücke Enter zum Beenden"
        exit 1
    }
    Write-Host "[OK] Virtuelle Umgebung erstellt" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[INFO] Aktiviere virtuelle Umgebung..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check for execution policy issues
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNUNG] Execution Policy verhindert Skript-Ausführung!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Führe folgenden Befehl aus (als Administrator):" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Oder verwende stattdessen start.bat" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Check if dependencies are installed
if (-not (Test-Path "venv\Lib\site-packages\fastapi")) {
    Write-Host ""
    Write-Host "[INFO] Installiere Abhängigkeiten (dies kann einige Minuten dauern)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FEHLER] Installation der Abhängigkeiten fehlgeschlagen!" -ForegroundColor Red
        Read-Host "Drücke Enter zum Beenden"
        exit 1
    }
    Write-Host "[OK] Abhängigkeiten installiert" -ForegroundColor Green
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host ""
        Write-Host "[INFO] Erstelle .env Datei aus Vorlage..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] .env Datei erstellt" -ForegroundColor Green
    }
}

# Start the application
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starte Anwendung..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Drücke Ctrl+C um die Anwendung zu beenden" -ForegroundColor Yellow
Write-Host ""

# Oeffne Browser sofort mit Ladeseite
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process "$scriptDir\app\static\loading_browser.html"

# Starte Server
python -m app.main

# If app exits with error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[FEHLER] Anwendung wurde mit Fehler beendet!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
}
