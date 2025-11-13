#!/usr/bin/env python3
"""
Migration: Makes the code field in events table optional (nullable)
"""
import sys
from pathlib import Path

# Pfad zum Projekt-Root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Macht das code Feld in der events Tabelle optional"""
    print("=" * 60)
    print("Migration: code Feld in events Tabelle optional machen")
    print("=" * 60)
    print()

    try:
        with engine.connect() as conn:
            # SQLite unterstützt ALTER COLUMN nicht direkt
            # Wir müssen die Tabelle neu erstellen
            print("Erstelle temporäre Tabelle...")

            # 1. Temporäre Tabelle erstellen
            conn.execute(text("""
                CREATE TABLE events_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    event_type VARCHAR(50) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    location VARCHAR(200),
                    code VARCHAR(20) UNIQUE,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))

            # 2. Daten kopieren
            print("Kopiere Daten...")
            conn.execute(text("""
                INSERT INTO events_new
                SELECT id, name, description, event_type, start_date, end_date,
                       location, code, is_active, created_at, updated_at
                FROM events
            """))

            # 3. Alte Tabelle löschen
            print("Lösche alte Tabelle...")
            conn.execute(text("DROP TABLE events"))

            # 4. Neue Tabelle umbenennen
            print("Benenne neue Tabelle um...")
            conn.execute(text("ALTER TABLE events_new RENAME TO events"))

            # 5. Indizes neu erstellen
            print("Erstelle Indizes...")
            conn.execute(text("CREATE INDEX ix_events_name ON events(name)"))
            conn.execute(text("CREATE INDEX ix_events_code ON events(code)"))

            conn.commit()
            print("✓ Migration erfolgreich abgeschlossen")

    except Exception as e:
        print(f"✗ Fehler bei der Migration: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Migration erfolgreich abgeschlossen!")
    print("=" * 60)
    print()
    print("Das 'code' Feld in der events Tabelle ist jetzt optional.")
    print("Neue Freizeiten können ohne Code erstellt werden.")

if __name__ == "__main__":
    migrate()
