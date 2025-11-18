@echo off
REM ============================================
REM  MGBFreizeitplaner - Desktop Build Script
REM  Erstellt eine standalone .exe für Windows
REM ============================================

echo.
echo ========================================
echo   MGBFreizeitplaner Desktop Build
echo   Windows .exe erstellen
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo.
    echo Bitte installiere Python 3.11 oder hoeher von:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Erstelle virtuelle Umgebung...
    python -m venv venv
    if errorlevel 1 (
        echo [FEHLER] Konnte virtuelle Umgebung nicht erstellen!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Install/Update requirements including PyInstaller and PyWebView
echo.
echo [INFO] Installiere Build-Abhängigkeiten...
pip install -r requirements.txt
if errorlevel 1 (
    echo [FEHLER] Installation fehlgeschlagen!
    pause
    exit /b 1
)

REM Clean previous build
echo.
echo [INFO] Bereinige vorherige Builds...
if exist "dist\" rmdir /s /q dist
if exist "build\" rmdir /s /q build

REM Build with PyInstaller
echo.
echo [INFO] Starte PyInstaller Build...
echo [INFO] Dies kann einige Minuten dauern...
echo.
pyinstaller desktop_app.spec

if errorlevel 1 (
    echo.
    echo [FEHLER] Build fehlgeschlagen!
    pause
    exit /b 1
)

REM Check if build was successful
if not exist "dist\MGBFreizeitplaner\MGBFreizeitplaner.exe" (
    echo.
    echo [FEHLER] .exe Datei wurde nicht erstellt!
    pause
    exit /b 1
)

REM Copy additional files to dist
echo.
echo [INFO] Kopiere zusätzliche Dateien...

REM Create .env if it doesn't exist in dist
if not exist "dist\MGBFreizeitplaner\.env" (
    if exist ".env.example" (
        copy .env.example "dist\MGBFreizeitplaner\.env" >nul
    )
)

REM Create README for distribution
echo MGBFreizeitplaner - Desktop-Version > "dist\MGBFreizeitplaner\README.txt"
echo. >> "dist\MGBFreizeitplaner\README.txt"
echo Starten: MGBFreizeitplaner.exe doppelklicken >> "dist\MGBFreizeitplaner\README.txt"
echo. >> "dist\MGBFreizeitplaner\README.txt"
echo Die Anwendung öffnet sich in einem eigenen Fenster. >> "dist\MGBFreizeitplaner\README.txt"
echo Es wird KEIN Browser benötigt! >> "dist\MGBFreizeitplaner\README.txt"
echo. >> "dist\MGBFreizeitplaner\README.txt"
echo Datenbank: Die SQLite-Datenbank wird im gleichen Verzeichnis erstellt. >> "dist\MGBFreizeitplaner\README.txt"

REM Get file size
for %%A in ("dist\MGBFreizeitplaner\MGBFreizeitplaner.exe") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576

echo.
echo ========================================
echo   BUILD ERFOLGREICH!
echo ========================================
echo.
echo [OK] Desktop-Anwendung wurde erstellt:
echo      dist\MGBFreizeitplaner\MGBFreizeitplaner.exe
echo.
echo [INFO] Größe: ~%SIZE_MB% MB
echo.
echo [INFO] Der komplette Ordner "dist\MGBFreizeitplaner\" kann
echo        auf andere Windows-PCs kopiert werden.
echo.
echo [INFO] Zum Testen:
echo        cd dist\MGBFreizeitplaner
echo        MGBFreizeitplaner.exe
echo.
pause
