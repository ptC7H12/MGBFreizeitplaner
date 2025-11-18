#!/usr/bin/env python3
"""
Diagnostic script to check and clean up manual_price_override values
"""
from app.database import get_db
from app.models.participant import Participant

def check_manual_prices():
    db = next(get_db())
    try:
        # Check for participants with manual_price_override = 0.0
        zero_prices = db.query(Participant).filter(
            Participant.manual_price_override == 0.0
        ).all()

        print(f"Found {len(zero_prices)} participants with manual_price_override = 0.0")
        if zero_prices:
            print("\nParticipants with 0.0 manual price override:")
            for p in zero_prices:
                print(f"  ID: {p.id}, Name: {p.first_name} {p.last_name}, "
                      f"manual_price_override: {p.manual_price_override}")

        # Check for participants with non-null manual_price_override
        manual_prices = db.query(Participant).filter(
            Participant.manual_price_override.isnot(None)
        ).all()

        print(f"\nFound {len(manual_prices)} participants with non-NULL manual_price_override")
        if manual_prices:
            print("\nAll participants with manual price override:")
            for p in manual_prices:
                print(f"  ID: {p.id}, Name: {p.first_name} {p.last_name}, "
                      f"manual_price_override: {p.manual_price_override}")

        # Option to clean up
        if zero_prices:
            print("\n" + "="*60)
            print("Would you like to clean up these 0.0 values? (yes/no)")
            response = input().strip().lower()
            if response == 'yes':
                for p in zero_prices:
                    p.manual_price_override = None
                db.commit()
                print(f"✓ Cleaned up {len(zero_prices)} participants")
            else:
                print("No changes made")

    finally:
        db.close()

if __name__ == "__main__":
    check_manual_prices()
