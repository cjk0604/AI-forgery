#!/usr/bin/env python3
"""
Unit test script to verify local programmatic verification rules in forgery_detector.py
"""

from forgery_detector import validate_korean_brn, check_math_consistency

def test_korean_brn_validator():
    print("[🧪] Testing Korean Business Registration Number (BRN) Validator...")
    
    # Test case 1: Valid Hyundai Receipt BRN (124-85-86989)
    valid_hyundai = "124-85-86989"
    res1 = validate_korean_brn(valid_hyundai)
    print(f"  - Hyundai BRN '{valid_hyundai}': Expected True, Got {res1}")
    assert res1 is True, "Failed to validate authentic Hyundai BRN"
    
    # Test case 2: Valid Adidas Receipt BRN (126-81-49677)
    valid_adidas = "126-81-49677"
    res2 = validate_korean_brn(valid_adidas)
    print(f"  - Adidas BRN '{valid_adidas}': Expected True, Got {res2}")
    assert res2 is True, "Failed to validate authentic Adidas BRN"
    
    # Test case 3: Invalid BRN (Check digit manipulated)
    invalid_brn = "126-81-49678"
    res3 = validate_korean_brn(invalid_brn)
    print(f"  - Invalid BRN '{invalid_brn}': Expected False, Got {res3}")
    assert res3 is False, "Failed to reject invalid BRN"
    
    # Test case 4: None and empty handling
    assert validate_korean_brn("") is None
    assert validate_korean_brn(None) is None
    assert validate_korean_brn("123") is None
    
    print("✅ BRN Validator unit tests passed successfully!\n")

def test_math_consistency():
    print("[🧪] Testing Mathematical Total Consistency Checker...")
    
    # Test case 1: Correct matching amounts
    items_ok = [
        {"amount": 160000},
        {"amount": 210000},
        {"amount": 230000}
    ]
    total_ok = 600000.0
    res1 = check_math_consistency(items_ok, total_ok)
    print(f"  - Match Check (Sum={sum(i['amount'] for i in items_ok)}, Stated Total={total_ok}): Expected True, Got {res1}")
    assert res1 is True, "Failed on correct math"
    
    # Test case 2: Mismatched total
    items_bad = [
        {"amount": 160000},
        {"amount": 210000},
        {"amount": 230000}
    ]
    total_bad = 590000.0
    res2 = check_math_consistency(items_bad, total_bad)
    print(f"  - Mismatch Check (Sum={sum(i['amount'] for i in items_bad)}, Stated Total={total_bad}): Expected False, Got {res2}")
    assert res2 is False, "Failed on incorrect math mismatch"
    
    # Test case 3: Empty item list handling
    assert check_math_consistency([], 100) is None
    
    print("✅ Math Consistency unit tests passed successfully!\n")

if __name__ == "__main__":
    print("="*60)
    print("                POC PROGRAMMATIC VALIDATOR UNIT TESTS")
    print("="*60)
    try:
        test_korean_brn_validator()
        test_math_consistency()
        print("🎉 ALL PROGRAMMATIC LAYER UNIT TESTS PASSED SUCCESSFULLY! 🎉")
    except AssertionError as ae:
        print(f"❌ TEST FAILURE: {ae}")
    except Exception as e:
        print(f"❌ ERROR ENCOUNTERED: {e}")
    print("="*60)
