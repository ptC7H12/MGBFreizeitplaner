@echo off
REM ============================================
REM  MGBFreizeitplaner - Windows Startup Script
REM ============================================

echo.
echo ========================================
echo   MGBFreizeitplaner
echo   Freizeit-Kassen-System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo.
    echo Bitte installiere Python 3.11 oder hoeher von:
    echo https://www.python.org/downloads/
    echo.
    echo WICHTIG: Waehle bei der Installation "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python Version: %PYTHON_VERSION%

REM Check if Python version is supported (3.11 or 3.12)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if "%PYTHON_MAJOR%.%PYTHON_MINOR%" == "3.13" (
    echo.
    echo [WARNUNG] Python 3.13 wird noch nicht vollstaendig unterstuetzt!
    echo.
    echo Einige Pakete haben keine vorgefertigten Versionen fuer Python 3.13
    echo und benoetigen Rust zum Kompilieren.
    echo.
    echo Bitte installiere Python 3.11 oder 3.12 stattdessen:
    echo https://www.python.org/downloads/
    echo.
    echo Empfohlene Versionen:
    echo - Python 3.11.x (stabil)
    echo - Python 3.12.x (aktuell)
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo [INFO] Erstelle virtuelle Python-Umgebung...
    python -m venv venv
    if errorlevel 1 (
        echo [FEHLER] Konnte virtuelle Umgebung nicht erstellen!
        pause
        exit /b 1
    )
    echo [OK] Virtuelle Umgebung erstellt
)

REM Activate virtual environment
echo [INFO] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\Lib\site-packages\fastapi\" (
    echo.
    echo [INFO] Installiere Abhaengigkeiten (dies kann einige Minuten dauern)
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [FEHLER] Installation der Abhaengigkeiten fehlgeschlagen!
        pause
        exit /b 1
    )
    echo [OK] Abhaengigkeiten installiert
)

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo.
        echo [INFO] Erstelle .env Datei aus Vorlage...
        copy .env.example .env >nul
        echo [OK] .env Datei erstellt
    )
)

REM Start the application
echo.
echo ========================================
echo   Starte Anwendung
echo ========================================
echo.
echo Die Anwendung ist verfuegbar unter:
echo   http://localhost:8000
echo.
echo Druecke Ctrl+C um die Anwendung zu beenden
echo.
echo [INFO] Browser wird automatisch geoeffnet...
echo.

REM Start browser in background after 3 seconds using PowerShell
start /b powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:8000'"

python -m app.main

REM If app exits, wait for user input
if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung wurde mit Fehler beendet!
    pause
)
