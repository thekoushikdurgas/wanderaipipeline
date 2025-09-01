#!/usr/bin/env python3
"""
Test script to verify performance logging functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger, log_performance
from utils.database import PlacesDatabase
from utils.excel_handler import ExcelHandler

def test_performance_logging():
    """Test that performance logging works correctly."""
    print("Testing performance logging functionality...")
    
    # Test basic performance logging
    @log_performance("test_operation")
    def test_function():
        import time
        time.sleep(0.1)  # Simulate some work
        return "success"
    
    # Test the function
    result = test_function()
    print(f"Test function result: {result}")
    
    # Test database performance logging
    try:
        db = PlacesDatabase()
        print("Database initialized successfully")
        
        # Test a database operation that uses @log_performance
        places = db.get_all_places()
        print(f"Retrieved {len(places)} places from database")
        
    except Exception as e:
        print(f"Database test failed: {e}")
    
    # Test excel handler performance logging
    try:
        excel = ExcelHandler()
        print("Excel handler initialized successfully")
        
        # Test excel read operation
        data = excel.read_excel_data()
        print(f"Retrieved {len(data)} records from Excel")
        
    except Exception as e:
        print(f"Excel handler test failed: {e}")
    
    print("Performance logging test completed!")

if __name__ == "__main__":
    test_performance_logging()
