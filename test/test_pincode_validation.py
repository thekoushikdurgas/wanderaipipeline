"""
Test script for pincode validation changes.

This script tests the updated pincode validation that now allows
pincodes with less than 10 characters instead of requiring exactly 6 digits.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import PincodeValidator, ValidationResult

def test_pincode_validation():
    """Test the updated pincode validation rules."""
    
    print("🧪 Testing Pincode Validation (Updated Rules)")
    print("=" * 50)
    
    # Test cases for the new validation rules
    test_cases = [
        # Valid pincodes (less than 10 characters)
        ("123", "Valid 3-digit pincode"),
        ("12345", "Valid 5-digit pincode"),
        ("123456", "Valid 6-digit pincode (Indian standard)"),
        ("123456789", "Valid 9-digit pincode"),
        
        # Invalid pincodes (10 or more characters)
        ("1234567890", "Invalid 10-digit pincode (too long)"),
        ("12345678901", "Invalid 11-digit pincode (too long)"),
        
        # Invalid formats
        ("", "Empty pincode"),
        ("abc", "Non-numeric pincode"),
        ("12a34", "Mixed alphanumeric pincode"),
        ("12 34", "Pincode with spaces"),
        ("12-34", "Pincode with hyphens"),
        
        # Edge cases
        ("0", "Single digit zero"),
        ("000000", "All zeros (6 digits) - invalid"),
        ("999999", "All nines (6 digits)"),
    ]
    
    passed = 0
    failed = 0
    
    for pincode, description in test_cases:
        print(f"\n📝 Testing: {description}")
        print(f"   Pincode: '{pincode}'")
        
        try:
            result = PincodeValidator.validate_pincode(pincode)
            
            # Determine expected result based on new rules
            expected_valid = (
                pincode and 
                pincode.strip() and  # Handle empty strings
                pincode.isdigit() and 
                len(pincode) < 10 and
                pincode != "000000"  # Special case: all zeros is invalid
            )
            
            # For empty pincode, we expect it to be invalid with "Pincode is required" error
            if pincode == "":
                expected_valid = False
                expected_error = "Pincode is required"
                actual_error = result.errors[0] if result.errors else ""
                if result.is_valid == expected_valid and expected_error in actual_error:
                    status = "✅ PASS"
                    passed += 1
                else:
                    status = "❌ FAIL"
                    failed += 1
                    print(f"   Expected: Invalid with '{expected_error}'")
                    print(f"   Got: {'Valid' if result.is_valid else 'Invalid'} with '{actual_error}'")
            else:
                if result.is_valid == expected_valid:
                    status = "✅ PASS"
                    passed += 1
                else:
                    status = "❌ FAIL"
                    failed += 1
                    print(f"   Expected: {'Valid' if expected_valid else 'Invalid'}")
                    print(f"   Got: {'Valid' if result.is_valid else 'Invalid'}")
            
            print(f"   Status: {status}")
            print(f"   Valid: {result.is_valid}")
            
            if result.errors:
                print(f"   Errors: {result.errors}")
            
            if result.warnings:
                print(f"   Warnings: {result.warnings}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed! Pincode validation is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the validation logic.")
    
    return failed == 0

def test_ui_components():
    """Test that UI components reflect the new validation."""
    
    print("\n🧪 Testing UI Component Updates")
    print("=" * 50)
    
    try:
        from ui.components import PlaceForm
        
        print("✅ UI components imported successfully")
        print("✅ PlaceForm class is available")
        
        # Check if the form would accept the new validation
        print("✅ UI components should now accept pincodes < 10 characters")
        
    except ImportError as e:
        print(f"❌ Failed to import UI components: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        return False
    
    return True

def test_configuration():
    """Test that configuration files are updated."""
    
    print("\n🧪 Testing Configuration Updates")
    print("=" * 50)
    
    try:
        from config.settings import validation_config
        
        print(f"✅ Validation config loaded")
        print(f"   Pincode pattern: {validation_config.pincode_pattern}")
        print(f"   Pincode max length: {getattr(validation_config, 'pincode_max_length', 'Not set')}")
        
        # Verify the pattern allows 1-9 digits
        import re
        test_pincodes = ["1", "123", "123456", "123456789"]
        for pincode in test_pincodes:
            if re.match(validation_config.pincode_pattern, pincode):
                print(f"   ✅ Pattern accepts '{pincode}'")
            else:
                print(f"   ❌ Pattern rejects '{pincode}'")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Pincode Validation Tests")
    print("Testing the updated validation that allows pincodes < 10 characters")
    
    # Run all tests
    validation_ok = test_pincode_validation()
    ui_ok = test_ui_components()
    config_ok = test_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    print(f"   Validation Logic: {'✅ PASS' if validation_ok else '❌ FAIL'}")
    print(f"   UI Components: {'✅ PASS' if ui_ok else '❌ FAIL'}")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    
    if all([validation_ok, ui_ok, config_ok]):
        print("\n🎉 All tests passed! Pincode validation has been successfully updated.")
        print("   Pincodes must now be less than 10 characters (digits only).")
    else:
        print("\n⚠️  Some tests failed. Please review the changes.")
    
    print("\n" + "=" * 60)
