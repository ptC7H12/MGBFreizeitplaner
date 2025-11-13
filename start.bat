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

python -m app.main

REM If app exits, wait for user input
if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung wurde mit Fehler beendet!
    pause
)
