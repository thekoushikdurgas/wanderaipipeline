"""
Test script to verify that add_place_page.py works with updated pincode validation.

This script tests that the add_place_page.py no longer throws "exactly 6 characters" errors
and properly handles pincodes with less than 10 characters.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_add_place_page_import():
    """Test that add_place_page.py can be imported without errors."""
    
    print("🧪 Testing Add Place Page Import")
    print("=" * 40)
    
    try:
        from ui.add_place_page import AddPlacePage
        print("✅ AddPlacePage imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AddPlacePage: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing AddPlacePage: {e}")
        return False

def test_place_model_validation():
    """Test that the Place model validation works with new pincode rules."""
    
    print("\n🧪 Testing Place Model Validation")
    print("=" * 40)
    
    try:
        from models.place import PlaceCreate
        
        # Test valid pincodes (less than 10 characters)
        valid_test_cases = [
            "123",      # 3 digits
            "12345",    # 5 digits
            "123456",   # 6 digits
            "123456789" # 9 digits
        ]
        
        for pincode in valid_test_cases:
            try:
                # Create a minimal valid place
                place_data = {
                    "name": "Test Place",
                    "types": "test",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "address": "Test Address",
                    "pincode": pincode,
                    "country": "Test Country"
                }
                
                place = PlaceCreate(**place_data)
                print(f"✅ Valid pincode '{pincode}' accepted")
                
            except ValueError as e:
                if "exactly 6 characters" in str(e):
                    print(f"❌ Old validation still active for '{pincode}': {e}")
                    return False
                else:
                    print(f"❌ Unexpected validation error for '{pincode}': {e}")
                    return False
        
        # Test invalid pincode (10+ characters)
        try:
            place_data = {
                "name": "Test Place",
                "types": "test",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "Test Address",
                "pincode": "1234567890",  # 10 digits - should be rejected
                "country": "Test Country"
            }
            
            place = PlaceCreate(**place_data)
            print(f"❌ Invalid pincode '1234567890' was accepted (should be rejected)")
            return False
            
        except ValueError as e:
            if "less than 10 characters" in str(e):
                print(f"✅ Invalid pincode '1234567890' correctly rejected: {e}")
            else:
                print(f"❌ Unexpected error message for invalid pincode: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import PlaceCreate: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing Place model: {e}")
        return False

def test_validation_function():
    """Test the validate_place_data function with new pincode rules."""
    
    print("\n🧪 Testing validate_place_data Function")
    print("=" * 40)
    
    try:
        from models.place import validate_place_data
        
        # Test valid pincode
        valid_data = {
            "name": "Test Place",
            "types": "test",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "Test Address",
            "pincode": "12345"  # 5 digits - should be valid
        }
        
        errors = validate_place_data(valid_data)
        if not errors:
            print("✅ Valid pincode '12345' accepted by validate_place_data")
        else:
            print(f"❌ Valid pincode '12345' rejected: {errors}")
            return False
        
        # Test invalid pincode (10+ characters)
        invalid_data = {
            "name": "Test Place",
            "types": "test",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "Test Address",
            "pincode": "1234567890"  # 10 digits - should be invalid
        }
        
        errors = validate_place_data(invalid_data)
        if errors and any("less than 10 characters" in error for error in errors):
            print("✅ Invalid pincode '1234567890' correctly rejected by validate_place_data")
        else:
            print(f"❌ Invalid pincode '1234567890' not properly rejected: {errors}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import validate_place_data: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing validate_place_data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Add Place Page Fixes")
    print("Verifying that add_place_page.py works with updated pincode validation")
    print("=" * 60)
    
    # Run all tests
    import_ok = test_add_place_page_import()
    model_ok = test_place_model_validation()
    validation_ok = test_validation_function()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    print(f"   Import Test: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"   Model Validation: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"   Validation Function: {'✅ PASS' if validation_ok else '❌ FAIL'}")
    
    if all([import_ok, model_ok, validation_ok]):
        print("\n🎉 All tests passed! Add place page is now working correctly.")
        print("   The 'exactly 6 characters' error should no longer appear.")
    else:
        print("\n⚠️  Some tests failed. Please check the validation logic.")
    
    print("\n" + "=" * 60)
