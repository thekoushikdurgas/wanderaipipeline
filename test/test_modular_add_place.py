#!/usr/bin/env python3
"""
Test script for the modular Add Place Page functionality.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.add_place_page import AddPlacePage, render_add_place_page

def test_add_place_page_class():
    """Test the AddPlacePage class functionality."""
    print("🧪 Testing AddPlacePage class...")
    
    try:
        # Initialize the AddPlacePage class
        add_place_page = AddPlacePage()
        print("✅ AddPlacePage class initialized successfully")
        
        # Test that the class has the expected methods
        expected_methods = [
            'render',
            '_render_api_testing_section',
            '_render_endpoint_configuration',
            '_render_parameter_configuration',
            '_render_test_execution',
            '_render_test_results',
            '_render_url_structure'
        ]
        
        for method_name in expected_methods:
            if hasattr(add_place_page, method_name):
                print(f"✅ Method '{method_name}' found")
            else:
                print(f"❌ Method '{method_name}' not found")
                return False
        
        print("✅ All expected methods are present")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_render_function():
    """Test the render_add_place_page function."""
    print("🧪 Testing render_add_place_page function...")
    
    try:
        # Test that the function exists and is callable
        if callable(render_add_place_page):
            print("✅ render_add_place_page function is callable")
        else:
            print("❌ render_add_place_page is not callable")
            return False
        
        # Test function signature
        import inspect
        sig = inspect.signature(render_add_place_page)
        params = list(sig.parameters.keys())
        
        if 'place_ops' in params:
            print("✅ Function has correct parameter 'place_ops'")
        else:
            print(f"❌ Function parameters: {params}")
            return False
        
        print("✅ render_add_place_page function signature is correct")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all required imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test UI components import
        from ui.components import PlaceForm
        print("✅ PlaceForm import successful")
        
        # Test API tester import
        from api_testing.ola_maps_api_tester import OLAMapsAPITester
        print("✅ OLAMapsAPITester import successful")
        
        # Test logger import
        from utils.logger import get_logger
        print("✅ Logger import successful")
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Modular Add Place Page Tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("AddPlacePage Class Tests", test_add_place_page_class),
        ("Render Function Tests", test_render_function)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! The modular add place page is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
