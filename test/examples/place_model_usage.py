"""
Example usage of the Place model for the Places Management System.

This script demonstrates how to use the Place model for creating,
validating, and managing place data.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.place import (
    Place, PlaceType, Coordinates, PlaceRating, PlaceAddress, 
    PlaceTimestamps, validate_place_data, create_place_from_api_data
)


def example_basic_place_creation():
    """Example of creating a basic place."""
    print("=== Basic Place Creation ===")
    
    # Create the place with all core fields
    place = Place(
        id="cp_001",
        name="Connaught Place",
        types="tourist_attraction, shopping_mall, restaurant",
        latitude=28.6139,
        longitude=77.2090,
        address="Connaught Place, New Delhi, Delhi 110001",
        pincode="110001",
        country="India",
        rating=4.5,
        followers=1250,
        description="A historic circular market and tourist attraction in New Delhi"
    )
    
    print(f"Created place: {place.name}")
    print(f"Location: {place.latitude}, {place.longitude}")
    print(f"Rating: {place.rating}/5.0")
    print(f"Followers: {place.followers}")
    print(f"Country: {place.country}")
    print(f"Description: {place.description}")
    print()


def example_place_from_dict():
    """Example of creating a place from dictionary data."""
    print("=== Place from Dictionary ===")
    
    # Sample place data (like from API or database)
    place_data = {
        'id': 'taj_mahal_001',
        'name': 'Taj Mahal',
        'types': 'tourist_attraction, landmark, museum',
        'latitude': 27.1751,
        'longitude': 78.0421,
        'address': 'Agra, Uttar Pradesh 282001',
        'pincode': '282001',
        'country': 'India',
        'rating': 4.8,
        'followers': 5000,
        'description': 'A stunning white marble mausoleum and UNESCO World Heritage site'
    }
    
    # Validate the data
    errors = validate_place_data(place_data)
    if errors:
        print(f"Validation errors: {errors}")
        return
    
    # Create place from dictionary
    place = Place.from_dict(place_data)
    
    print(f"Created place: {place.name}")
    print(f"Types: {place.types}")
    print(f"Location: {place.latitude}, {place.longitude}")
    print(f"Rating: {place.rating}/5.0")
    print()


def example_place_validation():
    """Example of place validation."""
    print("=== Place Validation ===")
    
    # Valid place data
    valid_data = {
        'name': 'Valid Place',
        'types': 'restaurant',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': '123 Main St, New York, NY 10001',
        'pincode': '100001',
        'country': 'USA',
        'rating': 4.0,
        'followers': 100,
        'description': 'A popular restaurant in New York'
    }
    
    # Invalid place data
    invalid_data = {
        'name': '',  # Empty name
        'types': 'restaurant',
        'latitude': 200.0,  # Invalid latitude
        'longitude': -74.0060,
        'address': '123 Main St',
        'pincode': '123',  # Invalid pincode
        'country': 'USA',
        'rating': 6.0,  # Invalid rating
        'followers': -10,  # Negative followers
        'description': ''  # Empty description
    }
    
    # Validate valid data
    print("Validating valid data:")
    errors = validate_place_data(valid_data)
    if errors:
        print(f"Errors: {errors}")
    else:
        print("✅ Valid data - no errors")
    
    # Validate invalid data
    print("\nValidating invalid data:")
    errors = validate_place_data(invalid_data)
    if errors:
        print(f"Errors: {errors}")
    else:
        print("✅ Valid data - no errors")
    print()


def example_place_operations():
    """Example of place operations."""
    print("=== Place Operations ===")
    
    # Create two places
    place1 = Place.from_dict({
        'name': 'Central Park',
        'types': 'park, tourist_attraction',
        'latitude': 40.7829,
        'longitude': -73.9654,
        'address': 'Central Park, New York, NY',
        'pincode': '100001',
        'country': 'USA',
        'rating': 4.7,
        'followers': 2000,
        'description': 'A large urban park in Manhattan'
    })
    
    place2 = Place.from_dict({
        'name': 'Times Square',
        'types': 'tourist_attraction, point_of_interest',
        'latitude': 40.7580,
        'longitude': -73.9855,
        'address': 'Times Square, New York, NY',
        'pincode': '100001',
        'country': 'USA',
        'rating': 4.3,
        'followers': 1500,
        'description': 'A major commercial intersection and tourist destination'
    })
    
    # Calculate distance between places
    distance = place1.get_distance_to(place2)
    print(f"Distance between {place1.name} and {place2.name}: {distance:.2f} km")
    
    # Check if places are near each other
    is_near = place1.is_near(place2, max_distance_km=5.0)
    print(f"Are they within 5km? {'Yes' if is_near else 'No'}")
    
    # Check place types
    has_restaurant = place1.has_type('restaurant')
    print(f"Does {place1.name} have restaurant type? {'Yes' if has_restaurant else 'No'}")
    
    # Get types list
    types_list = place1.get_types_list()
    print(f"Types for {place1.name}: {types_list}")
    
    # Update place
    place1.update(name="Central Park (Updated)")
    print(f"Updated name: {place1.name}")
    print()


def example_api_data_conversion():
    """Example of converting API data to Place model."""
    print("=== API Data Conversion ===")
    
    # Simulate API response data
    api_data = {
        'id': 'eiffel_tower_001',
        'name': 'Eiffel Tower',
        'types': ['tourist_attraction', 'landmark', 'point_of_interest'],
        'geometry': {
            'location': {
                'lat': 48.8584,
                'lng': 2.2945
            }
        },
        'formatted_address': 'Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France',
        'address_components': [
            {
                'long_name': '75007',
                'short_name': '75007',
                'types': ['postal_code']
            },
            {
                'long_name': 'France',
                'short_name': 'FR',
                'types': ['country', 'political']
            }
        ],
        'rating': 4.6,
        'user_ratings_total': 3500,
        'description': 'Iconic iron lattice tower on the Champ de Mars in Paris'
    }
    
    # Convert API data to Place model
    place = create_place_from_api_data(api_data)
    
    print(f"Converted API data to place: {place.name}")
    print(f"Location: {place.latitude}, {place.longitude}")
    print(f"Address: {place.address}")
    print(f"Country: {place.country}")
    print(f"Pincode: {place.pincode}")
    print(f"Rating: {place.rating}/5.0")
    print(f"Followers: {place.followers}")
    print(f"Description: {place.description}")
    print()


def example_place_type_enum():
    """Example of using PlaceType enum."""
    print("=== Place Type Enum ===")
    
    # Get all available place types
    all_types = PlaceType.get_all_types()
    print(f"Total place types available: {len(all_types)}")
    
    # Validate some place types
    test_types = ['restaurant', 'hotel', 'invalid_type', 'museum']
    for place_type in test_types:
        is_valid = PlaceType.validate_type(place_type)
        print(f"'{place_type}' is valid: {'Yes' if is_valid else 'No'}")
    
    # Show some specific types
    print(f"\nFood types: {[PlaceType.RESTAURANT, PlaceType.CAFE, PlaceType.BAR]}")
    print(f"Accommodation types: {[PlaceType.HOTEL, PlaceType.LODGING]}")
    print(f"Attraction types: {[PlaceType.TOURIST_ATTRACTION, PlaceType.MUSEUM, PlaceType.PARK]}")
    print()


def main():
    """Run all examples."""
    print("🏛️ Place Model Usage Examples\n")
    
    try:
        example_basic_place_creation()
        example_place_from_dict()
        example_place_validation()
        example_place_operations()
        example_api_data_conversion()
        example_place_type_enum()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
