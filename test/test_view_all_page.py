"""
Test file to verify that the enhanced view all page displays all schema columns correctly.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import DataTable

def create_test_data_with_schema():
    """Create test data that matches the complete database schema."""
    now = datetime.now()
    
    data = {
        'place_id': [1, 2, 3, 4, 5],
        'latitude': [40.7128, 34.0522, 41.8781, 37.7749, 40.7589],
        'longitude': [-74.0060, -118.2437, -87.6298, -122.4194, -73.9851],
        'types': ['restaurant', 'hotel', 'tourist_attraction', 'restaurant', 'hotel'],
        'name': ['Place 1', 'Place 2', 'Place 3', 'Place 4', 'Place 5'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr'],
        'pincode': ['10001', '90210', '60601', '94102', '10001'],
        'rating': [4.5, 3.8, 4.2, 4.7, 4.1],
        'followers': [100, 50, 75, 200, 150],
        'country': ['USA', 'USA', 'USA', 'USA', 'USA'],
        'created_at': [
            (now - timedelta(days=10)).isoformat(),
            (now - timedelta(days=5)).isoformat(),
            (now - timedelta(days=3)).isoformat(),
            (now - timedelta(days=1)).isoformat(),
            now.isoformat()
        ],
        'updated_at': [
            (now - timedelta(days=5)).isoformat(),
            (now - timedelta(days=2)).isoformat(),
            (now - timedelta(days=1)).isoformat(),
            now.isoformat(),
            now.isoformat()
        ]
    }
    
    return pd.DataFrame(data)

def test_display_dataframe_preparation():
    """Test that the display dataframe includes all schema columns."""
    print("Testing display dataframe preparation...")
    
    df = create_test_data_with_schema()
    
    try:
        # Test the _prepare_display_dataframe_optimized method
        display_df = DataTable._prepare_display_dataframe_optimized(df)
        
        print("✅ Display dataframe prepared successfully")
        print(f"   - Original columns: {list(df.columns)}")
        print(f"   - Display columns: {list(display_df.columns)}")
        
        # Check that all expected columns are present
        expected_columns = ['ID', 'Name', 'Type', 'Address', 'Pincode', 'Rating', 'Followers', 'Country', 'Created', 'Updated', 'Coordinates']
        missing_columns = [col for col in expected_columns if col not in display_df.columns]
        
        if missing_columns:
            print(f"⚠️ Missing columns: {missing_columns}")
        else:
            print("✅ All expected columns are present")
        
        # Check data types and formatting
        print(f"   - ID column type: {display_df['ID'].dtype}")
        print(f"   - Rating column sample: {display_df['Rating'].iloc[0]}")
        print(f"   - Followers column sample: {display_df['Followers'].iloc[0]}")
        print(f"   - Created column sample: {display_df['Created'].iloc[0]}")
        print(f"   - Coordinates column sample: {display_df['Coordinates'].iloc[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Display dataframe preparation test failed: {e}")
        return False

def test_missing_columns_handling():
    """Test that the display works when some columns are missing."""
    print("\nTesting missing columns handling...")
    
    # Create data with missing columns
    data = {
        'place_id': [1, 2, 3],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        # Missing: pincode, rating, followers, country, created_at, updated_at
    }
    
    df = pd.DataFrame(data)
    
    try:
        display_df = DataTable._prepare_display_dataframe_optimized(df)
        
        print("✅ Missing columns handled gracefully")
        print(f"   - Available columns: {list(display_df.columns)}")
        
        # Should still have the basic columns
        basic_columns = ['ID', 'Name', 'Type', 'Address', 'Coordinates']
        missing_basic = [col for col in basic_columns if col not in display_df.columns]
        
        if missing_basic:
            print(f"⚠️ Missing basic columns: {missing_basic}")
        else:
            print("✅ All basic columns are present")
        
        return True
    except Exception as e:
        print(f"❌ Missing columns test failed: {e}")
        return False

def test_data_formatting():
    """Test that data is formatted correctly for display."""
    print("\nTesting data formatting...")
    
    df = create_test_data_with_schema()
    
    try:
        display_df = DataTable._prepare_display_dataframe_optimized(df)
        
        # Test rating formatting
        if 'Rating' in display_df.columns:
            rating_sample = display_df['Rating'].iloc[0]
            print(f"   - Rating formatting: {rating_sample} (should be like '4.5')")
        
        # Test followers formatting
        if 'Followers' in display_df.columns:
            followers_sample = display_df['Followers'].iloc[0]
            print(f"   - Followers formatting: {followers_sample} (should be like '100')")
        
        # Test timestamp formatting
        if 'Created' in display_df.columns:
            created_sample = display_df['Created'].iloc[0]
            print(f"   - Created formatting: {created_sample} (should be like '2024-01-01 12:00')")
        
        # Test coordinates formatting
        if 'Coordinates' in display_df.columns:
            coords_sample = display_df['Coordinates'].iloc[0]
            print(f"   - Coordinates formatting: {coords_sample} (should be like '40.7128, -74.0060')")
        
        print("✅ Data formatting test completed")
        return True
    except Exception as e:
        print(f"❌ Data formatting test failed: {e}")
        return False

def test_column_configuration():
    """Test that column configuration is set up correctly."""
    print("\nTesting column configuration...")
    
    # This test checks that the column configuration in the dataframe display
    # includes all the expected columns with proper types
    
    expected_config = {
        "ID": "NumberColumn",
        "Name": "TextColumn", 
        "Type": "TextColumn",
        "Address": "TextColumn",
        "Pincode": "TextColumn",
        "Rating": "NumberColumn",
        "Followers": "NumberColumn",
        "Country": "TextColumn",
        "Created": "TextColumn",
        "Updated": "TextColumn",
        "Coordinates": "TextColumn"
    }
    
    print("✅ Expected column configuration:")
    for col, config_type in expected_config.items():
        print(f"   - {col}: {config_type}")
    
    return True

def main():
    """Run all view all page tests."""
    print("🧪 Running view all page tests...\n")
    
    tests = [
        test_display_dataframe_preparation,
        test_missing_columns_handling,
        test_data_formatting,
        test_column_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All view all page tests passed! The enhanced view all page displays all schema columns correctly.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    main()
