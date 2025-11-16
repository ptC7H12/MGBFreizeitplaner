#!/bin/bash
# ============================================
#  MGBFreizeitplaner - macOS/Linux Startup Script
# ============================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   MGBFreizeitplaner${NC}"
echo -e "${CYAN}   Freizeit-Kassen-System${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[FEHLER] Python 3 ist nicht installiert!${NC}"
    echo ""
    echo -e "${YELLOW}Bitte installiere Python 3.11 oder höher:${NC}"
    echo ""
    echo "macOS (mit Homebrew):"
    echo "  brew install python@3.11"
    echo ""
    echo "Oder von: https://www.python.org/downloads/"
    echo ""
    read -p "Drücke Enter zum Beenden"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}[INFO] $PYTHON_VERSION${NC}"

# Check Python version (minimum 3.11)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}[FEHLER] Python 3.11 oder höher wird benötigt!${NC}"
    echo -e "${YELLOW}Aktuelle Version: Python $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
    echo ""
    read -p "Drücke Enter zum Beenden"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}[INFO] Erstelle virtuelle Python-Umgebung...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[FEHLER] Konnte virtuelle Umgebung nicht erstellen!${NC}"
        read -p "Drücke Enter zum Beenden"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtuelle Umgebung erstellt${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}[INFO] Aktiviere virtuelle Umgebung...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if [ ! -d "venv/lib/python3.*/site-packages/fastapi" ] && [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo ""
    echo -e "${YELLOW}[INFO] Installiere Abhängigkeiten (dies kann einige Minuten dauern)...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[FEHLER] Installation der Abhängigkeiten fehlgeschlagen!${NC}"
        read -p "Drücke Enter zum Beenden"
        exit 1
    fi
    echo -e "${GREEN}[OK] Abhängigkeiten installiert${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo ""
        echo -e "${YELLOW}[INFO] Erstelle .env Datei aus Vorlage...${NC}"
        cp .env.example .env
        echo -e "${GREEN}[OK] .env Datei erstellt${NC}"
    fi
fi

# Start the application
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Starte Anwendung...${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}Die Anwendung ist verfügbar unter:${NC}"
echo -e "${CYAN}  http://localhost:8000/auth${NC}"
echo ""
echo -e "${YELLOW}Drücke Ctrl+C um die Anwendung zu beenden${NC}"
echo -e "${YELLOW}[INFO] Browser wird automatisch geöffnet...${NC}"
echo ""

# Open browser in background after 3 seconds
(sleep 3 && {
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8000/auth
    elif command -v open &> /dev/null; then
        open http://localhost:8000/auth
    fi
}) &

python -m app.main

# If app exits with error
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[FEHLER] Anwendung wurde mit Fehler beendet!${NC}"
    read -p "Drücke Enter zum Beenden"
fi
