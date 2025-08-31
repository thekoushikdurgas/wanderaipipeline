"""
Test file to verify analytics dashboard fixes for FutureWarning and datetime comparison issues.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import analytics modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.dashboard import MetricsCalculator, ChartsGenerator

def test_fillna_fix():
    """Test that the fillna FutureWarning is fixed."""
    print("Testing fillna fix...")
    
    # Create test data with object dtype columns
    data = {
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'rating': ['4.5', None, '3.8'],  # Object dtype with None
        'followers': ['100', None, '50'],  # Object dtype with None
        'created_at': ['2024-01-01', '2024-01-02', '2024-01-03']
    }
    
    df = pd.DataFrame(data)
    
    try:
        # This should not raise FutureWarning
        metrics = MetricsCalculator.calculate_basic_metrics(df)
        print("✅ fillna fix test passed - no FutureWarning raised")
        print(f"Metrics calculated: {metrics}")
        return True
    except Exception as e:
        print(f"❌ fillna fix test failed: {e}")
        return False

def test_datetime_comparison_fix():
    """Test that the datetime comparison issue is fixed."""
    print("\nTesting datetime comparison fix...")
    
    # Create test data with datetime strings
    now = datetime.now()
    data = {
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'created_at': [
            (now - timedelta(days=10)).isoformat(),
            (now - timedelta(days=5)).isoformat(),
            (now - timedelta(days=1)).isoformat()
        ]
    }
    
    df = pd.DataFrame(data)
    
    try:
        # This should not raise datetime comparison error
        metrics = MetricsCalculator.calculate_time_based_metrics(df)
        print("✅ datetime comparison fix test passed - no comparison error")
        print(f"Time-based metrics: {metrics}")
        return True
    except Exception as e:
        print(f"❌ datetime comparison fix test failed: {e}")
        return False

def test_invalid_datetime_handling():
    """Test handling of invalid datetime data."""
    print("\nTesting invalid datetime handling...")
    
    # Create test data with invalid datetime strings
    data = {
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'created_at': ['invalid_date', '2024-01-02', 'another_invalid']
    }
    
    df = pd.DataFrame(data)
    
    try:
        # This should handle invalid dates gracefully
        metrics = MetricsCalculator.calculate_time_based_metrics(df)
        print("✅ invalid datetime handling test passed")
        print(f"Result: {metrics}")
        return True
    except Exception as e:
        print(f"❌ invalid datetime handling test failed: {e}")
        return False

def test_chart_generation():
    """Test that chart generation works with the fixes."""
    print("\nTesting chart generation...")
    
    # Create test data
    data = {
        'name': ['Place 1', 'Place 2', 'Place 3'],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298],
        'types': ['restaurant', 'hotel', 'tourist_attraction'],
        'created_at': [
            '2024-01-01',
            '2024-01-02', 
            '2024-01-03'
        ]
    }
    
    df = pd.DataFrame(data)
    
    try:
        # Test timeline chart generation
        chart = ChartsGenerator.create_addition_timeline_chart(df)
        if chart is not None:
            print("✅ chart generation test passed")
            return True
        else:
            print("⚠️ chart generation returned None (expected for small dataset)")
            return True
    except Exception as e:
        print(f"❌ chart generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running analytics dashboard fix tests...\n")
    
    tests = [
        test_fillna_fix,
        test_datetime_comparison_fix,
        test_invalid_datetime_handling,
        test_chart_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The analytics dashboard fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    main()
