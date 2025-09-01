#!/usr/bin/env python3
"""
Simple test script for the updated Place model.
"""

import sys
import os
sys.path.append('.')

from models.place import Place

def test_place_creation():
    """Test creating a Place instance with all core fields."""
    print("Testing Place model creation...")
    
    try:
        # Create a place with all core fields
        place = Place(
            id="test_001",
            name="Test Place",
            types="restaurant, cafe",
            latitude=28.6139,
            longitude=77.2090,
            address="Test Address, New Delhi, Delhi 110001",
            pincode="110001",
            country="India",
            rating=4.5,
            followers=1000,
            description="A popular restaurant and cafe in New Delhi"
        )
        
        print(f"✅ Successfully created place: {place.name}")
        print(f"   ID: {place.id}")
        print(f"   Location: {place.latitude}, {place.longitude}")
        print(f"   Address: {place.address}")
        print(f"   Pincode: {place.pincode}")
        print(f"   Country: {place.country}")
        print(f"   Rating: {place.rating}")
        print(f"   Followers: {place.followers}")
        print(f"   Description: {place.description}")
        
        # Test to_dict method
        place_dict = place.to_dict()
        print(f"   Dictionary: {place_dict}")
        
        # Test from_dict method
        place_from_dict = Place.from_dict(place_dict)
        print(f"✅ Successfully recreated place from dict: {place_from_dict.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating place: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_place_validation():
    """Test place validation."""
    print("\nTesting Place validation...")
    
    try:
        # Test invalid coordinates
        try:
            place = Place(
                id="test_002",
                name="Invalid Place",
                types="restaurant",
                latitude=100.0,  # Invalid latitude
                longitude=77.2090,
                            address="Test Address",
            pincode="110001",
            country="India",
            rating=4.5,
            followers=1000,
            description="Test description"
            )
            print("❌ Should have failed with invalid latitude")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught invalid latitude: {e}")
        
        # Test invalid rating
        try:
            place = Place(
                id="test_003",
                name="Invalid Place",
                types="restaurant",
                latitude=28.6139,
                longitude=77.2090,
                            address="Test Address",
            pincode="110001",
            country="India",
            rating=6.0,  # Invalid rating
            followers=1000,
            description="Test description"
            )
            print("❌ Should have failed with invalid rating")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught invalid rating: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in validation test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Updated Place Model\n")
    
    success1 = test_place_creation()
    success2 = test_place_validation()
    
    if success1 and success2:
        print("\n✅ All tests passed! Place model is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
