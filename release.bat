@echo off
REM Release-Skript für MGBFreizeitplaner (Windows)
REM Automatisiert: Version setzen, Tag erstellen, committen und pushen
REM
REM Verwendung:
REM   release.bat 0.3.0
REM   release.bat 0.3.0 --no-push

setlocal enabledelayedexpansion

REM Prüfe ob Version angegeben wurde
if "%1"=="" (
    echo.
    echo FEHLER: Keine Version angegeben
    echo.
    echo Verwendung:
    echo   release.bat 0.3.0           ^(Erstellt Version 0.3.0 und pusht alles^)
    echo   release.bat 0.3.0 --no-push ^(Nur lokal, kein Push^)
    echo.
    echo Aktuelle Version:
    type version.txt 2>nul || echo 0.0.0
    exit /b 1
)

set VERSION=%1
set NO_PUSH=false

if "%2"=="--no-push" set NO_PUSH=true

echo ============================================
echo   MGBFreizeitplaner Release %VERSION%
echo ============================================
echo.

REM Schritt 1: Version setzen und Tag erstellen
echo [1/5] Version setzen und Git-Tag erstellen...
python update_version.py %VERSION%
if errorlevel 1 (
    echo FEHLER: Version konnte nicht gesetzt werden
    exit /b 1
)
echo.

REM Schritt 2: version.txt zum Staging-Bereich hinzufügen
echo [2/5] version.txt zum Staging-Bereich hinzufuegen...
git add version.txt
echo OK: version.txt hinzugefuegt
echo.

REM Schritt 3: Committen
echo [3/5] Version-Bump committen...
git commit -m "Bump version to %VERSION%"
if errorlevel 1 (
    echo FEHLER: Commit fehlgeschlagen
    exit /b 1
)
echo OK: Commit erstellt
echo.

if "%NO_PUSH%"=="true" (
    echo HINWEIS: --no-push Flag gesetzt, ueberspringe Push-Schritte
    echo.
    echo ============================================
    echo   Version %VERSION% erfolgreich erstellt!
    echo ============================================
    echo.
    echo Naechste Schritte ^(manuell^):
    echo   git push
    echo   git push origin v%VERSION%
    exit /b 0
)

REM Schritt 4: Branch pushen
echo [4/5] Branch pushen...
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
git push -u origin %CURRENT_BRANCH%
if errorlevel 1 (
    echo FEHLER: Branch-Push fehlgeschlagen
    echo Versuchen Sie manuell: git push
    exit /b 1
)
echo OK: Branch gepusht: %CURRENT_BRANCH%
echo.

REM Schritt 5: Tag pushen
echo [5/5] Git-Tag pushen...
git push origin v%VERSION% 2>&1 | findstr /C:"403" /C:"error" /C:"fatal" >nul
if errorlevel 1 (
    echo OK: Tag gepusht: v%VERSION%
) else (
    echo WARNUNG: Tag-Push hat moeglicherweise nicht funktioniert
    echo Bitte pushen Sie den Tag manuell:
    echo   git push origin v%VERSION%
)
echo.

REM Erfolg!
echo ============================================
echo   Release %VERSION% erfolgreich erstellt!
echo ============================================
echo.
echo Zusammenfassung:
echo   - Version in version.txt: %VERSION%
echo   - Git-Tag erstellt: v%VERSION%
echo   - Branch gepusht: %CURRENT_BRANCH%
echo.
echo Alle Tags anzeigen:
echo   git tag -l
echo.

endlocal
