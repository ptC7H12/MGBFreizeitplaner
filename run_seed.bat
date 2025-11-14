@echo off
echo ====================================
echo Seed-Daten Script
echo ====================================
echo.

REM Prüfen ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    echo Bitte installiere Python von https://www.python.org
    pause
    exit /b 1
)

echo [1/3] Installiere Abhängigkeiten...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo FEHLER: Installation der Abhängigkeiten fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo [2/3] Führe Seed-Script aus...
echo.
python seed_data.py
if %errorlevel% neq 0 (
    echo.
    echo FEHLER: Seed-Script ist fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo [3/3] Fertig!
echo ====================================
echo Seed-Daten wurden erfolgreich geladen!
echo ====================================
echo.
pause
