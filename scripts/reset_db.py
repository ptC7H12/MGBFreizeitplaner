#!/usr/bin/env python3
"""
Datenbank-Reset Script für Schema-Änderungen
WARNUNG: Dieses Script löscht ALLE Daten!
"""
import os
import sys
from pathlib import Path

# Pfad zum Projekt-Root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine
from app.models import *  # Alle Models importieren

def reset_database():
    """Löscht und erstellt die Datenbank neu"""
    print("=" * 60)
    print("WARNUNG: Datenbank-Reset")
    print("=" * 60)
    print()
    print("Dieses Script wird:")
    print("1. ALLE bestehenden Daten löschen")
    print("2. Alle Tabellen mit dem neuen Schema erstellen")
    print()

    response = input("Möchten Sie fortfahren? (ja/nein): ").strip().lower()

    if response not in ['ja', 'yes', 'j', 'y']:
        print("Abgebrochen.")
        sys.exit(0)

    print()
    print("Lösche alte Tabellen...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Alte Tabellen gelöscht")

    print("Erstelle neue Tabellen...")
    Base.metadata.create_all(bind=engine)
    print("✓ Neue Tabellen erstellt")

    print()
    print("=" * 60)
    print("Datenbank erfolgreich zurückgesetzt!")
    print("=" * 60)
    print()
    print("Sie können jetzt die Anwendung starten und eine neue")
    print("Freizeit erstellen.")

if __name__ == "__main__":
    reset_database()
