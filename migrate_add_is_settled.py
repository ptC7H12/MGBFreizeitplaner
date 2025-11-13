#!/usr/bin/env python3
"""
Migration: Fügt das is_settled Feld zur expenses Tabelle hinzu
"""
import sys
from pathlib import Path

# Pfad zum Projekt-Root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Fügt die is_settled Spalte zur expenses Tabelle hinzu"""
    print("=" * 60)
    print("Migration: is_settled Feld zu expenses Tabelle hinzufügen")
    print("=" * 60)
    print()

    try:
        with engine.connect() as conn:
            # Prüfen ob die Spalte bereits existiert
            result = conn.execute(text("PRAGMA table_info(expenses)"))
            columns = [row[1] for row in result.fetchall()]

            if 'is_settled' in columns:
                print("✓ Die Spalte 'is_settled' existiert bereits.")
                return

            # Spalte hinzufügen
            print("Füge Spalte 'is_settled' hinzu...")
            conn.execute(text("ALTER TABLE expenses ADD COLUMN is_settled BOOLEAN DEFAULT 0 NOT NULL"))
            conn.commit()
            print("✓ Spalte 'is_settled' erfolgreich hinzugefügt")

    except Exception as e:
        print(f"✗ Fehler bei der Migration: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Migration erfolgreich abgeschlossen!")
    print("=" * 60)

if __name__ == "__main__":
    migrate()
