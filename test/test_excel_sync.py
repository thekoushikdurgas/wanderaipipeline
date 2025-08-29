#!/usr/bin/env python3
"""
Test script to verify Excel sync is working without timezone errors.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_excel_sync():
    """Test Excel sync functionality."""
    print("Testing Excel sync functionality...")
    
    try:
        from utils.database import PlacesDatabase
        from utils.excel_handler import excel_handler
        
        # Initialize database
        print("Initializing database...")
        db = PlacesDatabase()
        
        # Test getting all places
        print("Getting all places from database...")
        places_df = db.get_all_places(prefer_excel=False)
        print(f"Retrieved {len(places_df)} places from database")
        
        if not places_df.empty:
            print("Sample place data:")
            print(places_df.head(1).to_string())
            
            # Test Excel sync
            print("Testing Excel sync...")
            success = excel_handler.sync_from_database(places_df)
            
            if success:
                print("✅ Excel sync successful!")
                
                # Test reading from Excel
                print("Testing Excel read...")
                excel_df = excel_handler.read_excel_data(use_cache=False)
                print(f"Retrieved {len(excel_df)} places from Excel")
                
                if len(excel_df) == len(places_df):
                    print("✅ Excel read successful - record count matches!")
                else:
                    print(f"⚠️ Record count mismatch: DB={len(places_df)}, Excel={len(excel_df)}")
                
            else:
                print("❌ Excel sync failed!")
                return False
        else:
            print("⚠️ No places found in database")
        
        print("✅ Excel sync test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Excel sync test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_sync()
    sys.exit(0 if success else 1)
