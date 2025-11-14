#!/usr/bin/env python3
"""
Migration Script: Remove is_reimbursed from expenses table
Usage: python migrations/run_migration.py
"""
import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings


def run_migration():
    """Execute the migration SQL script"""

    # Extract database path from DATABASE_URL
    db_url = settings.database_url
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
    else:
        print(f"Error: This migration is designed for SQLite databases only")
        sys.exit(1)

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)

    # Read migration SQL
    migration_file = Path(__file__).parent / 'remove_is_reimbursed.sql'
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Create backup
    backup_path = f"{db_path}.backup"
    print(f"Creating backup at: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)

    # Execute migration
    print(f"Running migration on: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        # Check if is_reimbursed column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_reimbursed' not in columns:
            print("Migration already applied - is_reimbursed column does not exist")
            conn.close()
            return

        # Execute migration
        conn.executescript(migration_sql)
        conn.commit()
        print("Migration completed successfully!")
        print(f"Backup saved at: {backup_path}")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        print(f"Database has been rolled back")
        print(f"Backup is available at: {backup_path}")
        sys.exit(1)

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Remove is_reimbursed column from expenses table")
    print("=" * 60)

    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        run_migration()
    else:
        print("Migration cancelled")
