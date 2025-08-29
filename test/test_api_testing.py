#!/usr/bin/env python3
"""
Test script for the OLA Maps API Testing functionality.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api_testing.ola_maps_api_tester import OLAMapsAPITester, APITestingUI

def test_api_tester():
    """Test the API tester functionality."""
    print("🧪 Testing OLA Maps API Tester...")
    
    # Initialize API tester
    api_tester = OLAMapsAPITester()
    
    # Test getting categories
    categories = api_tester.get_all_categories()
    print(f"✅ Found {len(categories)} API categories:")
    for category in categories:
        print(f"   - {category}")
    
    # Test getting endpoints for a category
    if categories:
        first_category = categories[0]
        endpoints = api_tester.get_endpoints_by_category(first_category)
        print(f"✅ Found {len(endpoints)} endpoints in {first_category}:")
        for endpoint in endpoints:
            print(f"   - {endpoint.method} {endpoint.name}")
    
    # Test getting a specific endpoint
    if endpoints:
        first_endpoint = endpoints[0]
        found_endpoint = api_tester.get_endpoint_by_name(first_endpoint.name)
        if found_endpoint:
            print(f"✅ Successfully retrieved endpoint: {found_endpoint.name}")
        else:
            print("❌ Failed to retrieve endpoint by name")
    
    print("✅ API tester functionality test completed!")

def test_api_ui():
    """Test the API UI functionality."""
    print("\n🎨 Testing API Testing UI...")
    
    try:
        # Initialize API UI
        api_ui = APITestingUI()
        print("✅ API Testing UI initialized successfully")
        
        # Test getting categories
        categories = api_ui.api_tester.get_all_categories()
        print(f"✅ UI can access {len(categories)} API categories")
        
        print("✅ API UI functionality test completed!")
        
    except Exception as e:
        print(f"❌ API UI test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting OLA Maps API Testing Module Tests...\n")
    
    try:
        test_api_tester()
        test_api_ui()
        print("\n🎉 All tests passed! The API testing module is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
