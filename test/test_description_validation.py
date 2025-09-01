#!/usr/bin/env python3
"""
Test script to verify description field validation in Place model.
"""

import sys
import os
sys.path.append('.')

from models.place import Place

def test_description_validation():
    """Test description field validation."""
    print("Testing description field validation...")
    
    try:
        # Test empty description
        try:
            place = Place(
                id="test_desc_001",
                name="Test Place",
                types="restaurant",
                latitude=28.6139,
                longitude=77.2090,
                address="Test Address",
                pincode="110001",
                country="India",
                rating=4.5,
                followers=1000,
                description=""  # Empty description
            )
            print("❌ Should have failed with empty description")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught empty description: {e}")
        
        # Test whitespace-only description
        try:
            place = Place(
                id="test_desc_002",
                name="Test Place",
                types="restaurant",
                latitude=28.6139,
                longitude=77.2090,
                address="Test Address",
                pincode="110001",
                country="India",
                rating=4.5,
                followers=1000,
                description="   "  # Whitespace-only description
            )
            print("❌ Should have failed with whitespace-only description")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught whitespace-only description: {e}")
        
        # Test valid description
        try:
            place = Place(
                id="test_desc_003",
                name="Test Place",
                types="restaurant",
                latitude=28.6139,
                longitude=77.2090,
                address="Test Address",
                pincode="110001",
                country="India",
                rating=4.5,
                followers=1000,
                description="A wonderful restaurant with great food and ambiance"
            )
            print(f"✅ Successfully created place with valid description: {place.description}")
            return True
        except ValueError as e:
            print(f"❌ Should not have failed with valid description: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error in description validation test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Description Field Validation\n")
    
    success = test_description_validation()
    
    if success:
        print("\n✅ Description field validation test passed!")
    else:
        print("\n❌ Description field validation test failed.")
