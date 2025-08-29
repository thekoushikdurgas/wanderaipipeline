#!/usr/bin/env python3
"""
Test script for the place_details function in AddPlacePage class.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.add_place_page import AddPlacePage

def test_place_details():
    """Test the place_details function."""
    print("🧪 Testing place_details function...")
    
    # Create AddPlacePage instance
    add_place_page = AddPlacePage()
    
    # Test with a sample place ID from the Postman collection
    sample_place_id = "ola-platform:a79ed32419962a11a588ea92b83ca78e"
    
    print(f"Testing with place ID: {sample_place_id}")
    
    try:
        # Call the place_details function
        result = add_place_page.place_details(sample_place_id)
        
        # Check the result
        if result.get("success"):
            print("✅ Place details retrieved successfully!")
            print(f"Status Code: {result.get('status_code')}")
            print(f"Response Time: {result.get('response_time')} ms")
            
            # Show some key details
            data = result.get("data", {})
            if "result" in data:
                place_info = data["result"]
                print(f"Name: {place_info.get('name', 'N/A')}")
                print(f"Address: {place_info.get('formatted_address', 'N/A')}")
                print(f"Phone: {place_info.get('formatted_phone_number', 'N/A')}")
                print(f"Website: {place_info.get('website', 'N/A')}")
                print(f"Rating: {place_info.get('rating', 'N/A')}")
                
                # Show coordinates if available
                if "geometry" in place_info and "location" in place_info["geometry"]:
                    location = place_info["geometry"]["location"]
                    print(f"Coordinates: {location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}")
            else:
                print("❌ No 'result' field in response data")
                print(f"Response data: {data}")
        else:
            print(f"❌ Failed to get place details: {result.get('error', 'Unknown error')}")
            print(f"Status Code: {result.get('status_code')}")
            print(f"Response Time: {result.get('response_time')} ms")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_place_details()
