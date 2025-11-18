#!/usr/bin/env python3
"""
Quick test for role discount case-insensitive matching
"""
from app.services.price_calculator import PriceCalculator

# Simuliere das Regelwerk
role_discounts = {
    "Küchenteam": {
        "discount_percent": 100,
        "max_count": 6
    },
    "Kinderstunde": {
        "discount_percent": 40,
        "max_count": 5
    }
}

# Test verschiedene Schreibweisen
test_cases = [
    ("Küchenteam", 100),  # Exact match
    ("küchenteam", 100),  # lowercase
    ("KÜCHENTEAM", 100),  # uppercase
    ("Kinderstunde", 40),  # Exact match
    ("kinderstunde", 40),  # lowercase
    ("NonExistent", 0),   # Nicht vorhanden
]

print("Testing role discount case-insensitive matching:")
print("=" * 60)

all_passed = True
for role_name, expected_discount in test_cases:
    discount = PriceCalculator._get_role_discount(role_name, role_discounts)
    status = "✓" if discount == expected_discount else "✗"
    if discount != expected_discount:
        all_passed = False
    print(f"{status} Role: '{role_name}' → Discount: {discount}% (expected: {expected_discount}%)")

print("=" * 60)
if all_passed:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed!")
