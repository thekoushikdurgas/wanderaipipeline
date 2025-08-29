#!/usr/bin/env python3
"""
Test script for the Nearby Search API functionality.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api_testing.ola_maps_api_tester import OLAMapsAPITester

def test_nearby_search_api():
    """Test the Nearby Search API functionality."""
    print("🧪 Testing Nearby Search API...")
    
    try:
        # Initialize API tester
        api_tester = OLAMapsAPITester()
        print("✅ API tester initialized")
        
        # Load Places API collection
        api_tester.load_collection("Places API.postman_collection.json")
        print("✅ Places API collection loaded")
        
        # Get the Nearby Search endpoint
        nearby_endpoint = api_tester.get_endpoint_by_name("4) Nearby Search - GET")
        
        if nearby_endpoint:
            print(f"✅ Found Nearby Search endpoint: {nearby_endpoint.name}")
            print(f"   Method: {nearby_endpoint.method}")
            print(f"   Category: {nearby_endpoint.category}")
            print(f"   Description: {nearby_endpoint.description}")
            
            # Test with sample parameters
            custom_params = {
                "location": "12.931544865377818,77.61638622280486",
                "types": "restaurant",
                "radius": "10000",
                "rankBy": "popular"
            }
            
            print("🚀 Testing API with sample parameters...")
            result = api_tester.test_endpoint(nearby_endpoint, custom_params)
            
            print(f"✅ API test completed")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Status Code: {result.get('status_code', 'N/A')}")
            print(f"   Response Time: {result.get('response_time', 'N/A')} ms")
            print(f"   URL: {result.get('url', 'N/A')}")
            
            if result.get('success', False):
                response = result.get('response', {})
                if isinstance(response, dict):
                    places = response.get("results", [])
                    print(f"   Found {len(places)} places")
                    
                    if places:
                        print("   Sample places:")
                        for i, place in enumerate(places[:3]):
                            print(f"     {i+1}. {place.get('name', 'N/A')} - {place.get('vicinity', 'N/A')}")
                else:
                    print(f"   Response: {response}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        else:
            print("❌ Nearby Search endpoint not found")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Nearby Search API Test...\n")
    test_nearby_search_api()
    print("\n�� Test completed!")
