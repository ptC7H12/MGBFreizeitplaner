#!/bin/bash

echo "===================================="
echo "Seed-Daten Script"
echo "===================================="
echo ""

# Prüfen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python ist nicht installiert!"
    echo "Bitte installiere Python 3"
    read -p "Drücke Enter zum Beenden..."
    exit 1
fi

echo "[1/3] Installiere Abhängigkeiten..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER: Installation der Abhängigkeiten fehlgeschlagen!"
    read -p "Drücke Enter zum Beenden..."
    exit 1
fi

echo ""
echo "[2/3] Führe Seed-Script aus..."
echo ""
python3 seed_data.py
if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER: Seed-Script ist fehlgeschlagen!"
    read -p "Drücke Enter zum Beenden..."
    exit 1
fi

echo ""
echo "[3/3] Fertig!"
echo "===================================="
echo "Seed-Daten wurden erfolgreich geladen!"
echo "===================================="
echo ""
read -p "Drücke Enter zum Beenden..."
