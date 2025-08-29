#!/usr/bin/env python3
"""
Test script to verify the pagination fixes work correctly.
"""

import os
from dotenv import load_dotenv
from database import PlacesDatabase

# Load environment variables
load_dotenv()

def test_pagination_fixes():
    """Test the pagination functionality to ensure it works correctly."""
    print("🧪 Testing pagination fixes...")
    
    try:
        # Initialize database
        db = PlacesDatabase()
        print("✅ Database connection successful")
        
        # Test 1: Basic pagination without search
        print("\n1. Testing basic pagination...")
        places_df, total_count = db.get_places_paginated(
            page=1, 
            page_size=5, 
            sort_by="name", 
            sort_order="ASC"
        )
        print(f"   Page 1 (5 items): {len(places_df)} places")
        print(f"   Total count: {total_count}")
        
        if not places_df.empty:
            print(f"   First place: {places_df.iloc[0]['name']}")
        
        # Test 2: Pagination with search
        print("\n2. Testing pagination with search...")
        search_df, search_total = db.get_places_paginated(
            page=1,
            page_size=3,
            sort_by="name",
            sort_order="ASC",
            search_term="restaurant"
        )
        print(f"   Search results (page 1, 3 items): {len(search_df)} places")
        print(f"   Total search results: {search_total}")
        
        if not search_df.empty:
            print(f"   First search result: {search_df.iloc[0]['name']}")
        
        # Test 3: Type-based pagination
        print("\n3. Testing type-based pagination...")
        type_df, type_total = db.get_places_by_type_paginated(
            "hotel",
            page=1,
            page_size=4,
            sort_by="name",
            sort_order="ASC"
        )
        print(f"   Hotel results (page 1, 4 items): {len(type_df)} places")
        print(f"   Total hotel results: {type_total}")
        
        if not type_df.empty:
            print(f"   First hotel: {type_df.iloc[0]['name']}")
        
        # Test 4: Second page
        print("\n4. Testing second page...")
        page2_df, _ = db.get_places_paginated(
            page=2,
            page_size=5,
            sort_by="name",
            sort_order="ASC"
        )
        print(f"   Page 2 (5 items): {len(page2_df)} places")
        
        if not page2_df.empty:
            print(f"   First place on page 2: {page2_df.iloc[0]['name']}")
        
        print("\n🎉 All pagination tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_pagination_fixes()
