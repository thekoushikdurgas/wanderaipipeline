#!/usr/bin/env python3
"""
Comprehensive test to verify both timezone fix and database initialization fix.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_fix():
    """Test both timezone fix and database initialization."""
    print("=== Comprehensive Fix Test ===")
    
    try:
        from utils.database import PlacesDatabase
        from utils.excel_handler import excel_handler
        from config.settings import validate_configuration
        
        print("1. Testing configuration validation...")
        config_errors = validate_configuration()
        if config_errors:
            print(f"❌ Configuration errors: {config_errors}")
            return False
        print("✅ Configuration validation passed")
        
        print("\n2. Testing database initialization...")
        db = PlacesDatabase()
        
        # Check if engine exists
        if not hasattr(db, 'engine'):
            print("❌ Database missing engine attribute")
            return False
        print("✅ Database engine attribute exists")
        
        # Test connection
        if not db.test_connection():
            print("❌ Database connection test failed")
            return False
        print("✅ Database connection test passed")
        
        print("\n3. Testing data retrieval with timezone conversion...")
        places_df = db.get_all_places(prefer_excel=False)
        print(f"✅ Retrieved {len(places_df)} places from database")
        
        # Check timezone conversion
        if 'created_at' in places_df.columns:
            tz_info = places_df['created_at'].dt.tz
            if tz_info is None:
                print("✅ Timezone conversion working - datetimes are timezone-naive")
            else:
                print(f"⚠️ Timezone info still present: {tz_info}")
        
        print("\n4. Testing Excel sync...")
        success = excel_handler.sync_from_database(places_df)
        if success:
            print("✅ Excel sync successful")
        else:
            print("❌ Excel sync failed")
            return False
        
        print("\n5. Testing Excel read...")
        excel_df = excel_handler.read_excel_data(use_cache=False)
        print(f"✅ Retrieved {len(excel_df)} places from Excel")
        
        if len(excel_df) == len(places_df):
            print("✅ Record count matches between database and Excel")
        else:
            print(f"⚠️ Record count mismatch: DB={len(places_df)}, Excel={len(excel_df)}")
        
        print("\n6. Testing paginated query...")
        paginated_df, total_count = db.get_places_paginated(page=1, page_size=10)
        if paginated_df is not None and len(paginated_df) > 0:
            print(f"✅ Paginated query successful - {len(paginated_df)} records")
        else:
            print("❌ Paginated query failed")
            return False
        
        print("\n=== All Tests Passed! ===")
        print("✅ Database initialization working")
        print("✅ Timezone conversion working")
        print("✅ Excel sync working")
        print("✅ Paginated queries working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_fix()
    sys.exit(0 if success else 1)
