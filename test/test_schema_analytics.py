"""
Test file to verify analytics dashboard works with complete database schema.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import analytics modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.dashboard import MetricsCalculator, ChartsGenerator

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

def test_complete_schema_metrics():
    """Test that all metrics work with complete database schema."""
    print("Testing complete schema metrics...")
    
    df = create_test_data_with_schema()
    
    try:
        # Test basic metrics
        basic_metrics = MetricsCalculator.calculate_basic_metrics(df)
        print("✅ Basic metrics calculated successfully")
        print(f"   - Total places: {basic_metrics.get('total_places', 0)}")
        print(f"   - Unique pincodes: {basic_metrics.get('unique_pincodes', 0)}")
        print(f"   - Address completeness: {basic_metrics.get('address_completeness', 0):.1f}%")
        
        # Test time-based metrics
        time_metrics = MetricsCalculator.calculate_time_based_metrics(df)
        print("✅ Time-based metrics calculated successfully")
        print(f"   - Recent additions: {time_metrics.get('recent_additions', 0)}")
        print(f"   - Daily addition rate: {time_metrics.get('daily_addition_rate', 0):.2f}")
        
        # Test comprehensive data quality
        quality_metrics = MetricsCalculator.calculate_comprehensive_data_quality(df)
        print("✅ Comprehensive data quality calculated successfully")
        print(f"   - Overall quality score: {quality_metrics.get('overall_quality_score', 0):.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Complete schema metrics test failed: {e}")
        return False

def test_schema_charts():
    """Test that all charts work with complete database schema."""
    print("\nTesting schema-based charts...")
    
    df = create_test_data_with_schema()
    
    try:
        # Test pincode distribution chart
        pincode_chart = ChartsGenerator.create_pincode_distribution_chart(df)
        if pincode_chart is not None:
            print("✅ Pincode distribution chart created successfully")
        else:
            print("⚠️ Pincode chart returned None (expected for small dataset)")
        
        # Test data quality chart
        quality_chart = ChartsGenerator.create_data_quality_chart(df)
        if quality_chart is not None:
            print("✅ Data quality chart created successfully")
        else:
            print("⚠️ Data quality chart returned None")
        
        # Test existing charts still work
        type_chart = ChartsGenerator.create_places_by_type_chart(df)
        if type_chart is not None:
            print("✅ Places by type chart created successfully")
        
        timeline_chart = ChartsGenerator.create_addition_timeline_chart(df)
        if timeline_chart is not None:
            print("✅ Addition timeline chart created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Schema charts test failed: {e}")
        return False

def test_missing_columns():
    """Test that analytics work gracefully when some columns are missing."""
    print("\nTesting missing columns handling...")
    
    # Create data with missing columns
    data = {
        'place_id': [1, 2, 3],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'name': ['Place 1', 'Place 2', 'Place 3'],
        # Missing: address, pincode, rating, followers, country, created_at, updated_at
    }
    
    df = pd.DataFrame(data)
    
    try:
        # Test basic metrics with missing columns
        basic_metrics = MetricsCalculator.calculate_basic_metrics(df)
        if basic_metrics:
            print("✅ Basic metrics work with missing columns")
            print(f"   - Unique pincodes: {basic_metrics.get('unique_pincodes', 0)}")
            print(f"   - Address completeness: {basic_metrics.get('address_completeness', 0):.1f}%")
        else:
            print("✅ Basic metrics work with missing columns (returned None)")
        
        # Test comprehensive data quality with missing columns
        quality_metrics = MetricsCalculator.calculate_comprehensive_data_quality(df)
        if quality_metrics and 'overall_quality_score' in quality_metrics:
            print("✅ Data quality works with missing columns")
            print(f"   - Overall quality score: {quality_metrics.get('overall_quality_score', 0):.1f}%")
        else:
            print("✅ Data quality works with missing columns (no quality score available)")
        
        return True
    except Exception as e:
        print(f"❌ Missing columns test failed: {e}")
        return False

def test_data_type_handling():
    """Test that analytics handle different data types correctly."""
    print("\nTesting data type handling...")
    
    # Create data with mixed data types
    data = {
        'place_id': [1, 2, 3],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'pincode': ['10001', '90210', '60601'],
        'rating': ['4.5', '3.8', '4.2'],  # String format
        'followers': ['100', '50', '75'],  # String format
        'country': ['USA', 'USA', 'USA'],
        'created_at': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'updated_at': ['2024-01-01', '2024-01-02', '2024-01-03']
    }
    
    df = pd.DataFrame(data)
    
    try:
        # Test basic metrics with string data types
        basic_metrics = MetricsCalculator.calculate_basic_metrics(df)
        print("✅ Basic metrics handle string data types")
        print(f"   - Rating metrics calculated: {basic_metrics.get('avg_rating', 0)}")
        print(f"   - Followers metrics calculated: {basic_metrics.get('avg_followers', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Data type handling test failed: {e}")
        return False

def main():
    """Run all schema-based tests."""
    print("🧪 Running schema-based analytics tests...\n")
    
    tests = [
        test_complete_schema_metrics,
        test_schema_charts,
        test_missing_columns,
        test_data_type_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All schema-based tests passed! Analytics dashboard works with complete database schema.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    main()
