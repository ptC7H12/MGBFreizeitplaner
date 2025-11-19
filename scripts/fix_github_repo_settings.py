#!/usr/bin/env python3
"""
Fix script: Update existing settings to have default_github_repo value.

This script updates all settings that have NULL or empty default_github_repo
to use the default GitHub repository URL.
"""

from app.database import SessionLocal
from app.models import Setting

# Default GitHub repo URL
DEFAULT_GITHUB_REPO = "https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/"

def main():
    db = SessionLocal()
    try:
        # Find all settings with NULL or empty default_github_repo
        settings = db.query(Setting).filter(
            (Setting.default_github_repo == None) | (Setting.default_github_repo == '')
        ).all()

        if not settings:
            print("✓ All settings already have default_github_repo configured")
            return

        print(f"Found {len(settings)} settings without default_github_repo")

        # Update each setting
        for setting in settings:
            setting.default_github_repo = DEFAULT_GITHUB_REPO
            print(f"  Updated setting for event_id={setting.event_id}")

        db.commit()
        print(f"\n✓ Successfully updated {len(settings)} settings")

    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
