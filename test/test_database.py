#!/usr/bin/env python3
"""
Test script for the Places Database functionality with PostgreSQL.
This script tests all CRUD operations and adds sample data.
"""

import os
from dotenv import load_dotenv
from database import PlacesDatabase
import pandas as pd

# Load environment variables
load_dotenv()

def test_database():
    """Test all database operations."""
    print("🗺️ Testing Places Database with PostgreSQL...")
    
    # Check if environment variables are set
    required_vars = ["user", "password", "host", "port", "dbname"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {missing_vars}")
        print("Please create a .env file with your PostgreSQL credentials:")
        print("user=postgres")
        print("password=your_password")
        print("host=your_host")
        print("port=5432")
        print("dbname=postgres")
        return False
    
    try:
        # Initialize database
        db = PlacesDatabase()
        print("✅ Successfully connected to PostgreSQL")
        
        # Test connection
        if db.test_connection():
            print("✅ Database connection test passed")
        else:
            print("❌ Database connection test failed")
            return False
        
        # Test 1: Add sample places
        print("\n1. Adding sample places...")
        sample_places = [
            # Original sample places
            (40.7128, -74.0060, "tourist_attraction", "Statue of Liberty", "Liberty Island, New York, NY", "10004"),
            (34.0522, -118.2437, "restaurant", "In-N-Out Burger", "7000 Sunset Blvd, Los Angeles, CA", "90028"),
            (51.5074, -0.1278, "hotel", "The Ritz London", "150 Piccadilly, St. James's, London", "W1J 9BR"),
            (35.6762, 139.6503, "tourist_attraction", "Tokyo Tower", "4 Chome-2-8 Shibakoen, Minato City, Tokyo", "105-0011"),
            (48.8584, 2.2945, "tourist_attraction", "Eiffel Tower", "Champ de Mars, 5 Avenue Anatole France, Paris", "75007"),
            
            # Additional places for pagination testing
            (40.7589, -73.9851, "tourist_attraction", "Times Square", "Manhattan, New York, NY", "10036"),
            (34.1016, -118.3267, "restaurant", "The Ivy", "113 N Robertson Blvd, Los Angeles, CA", "90048"),
            (51.5007, -0.1246, "hotel", "The Savoy", "Strand, London", "WC2R 0EZ"),
            (35.6586, 139.7454, "restaurant", "Sukiyabashi Jiro", "4-2-15 Ginza, Chuo City, Tokyo", "104-0061"),
            (48.8738, 2.2950, "hotel", "Hotel Ritz Paris", "15 Place Vendôme, Paris", "75001"),
            
            # More places for comprehensive testing
            (40.7484, -73.9857, "restaurant", "Le Bernardin", "155 W 51st St, New York, NY", "10019"),
            (34.0736, -118.2400, "hotel", "Beverly Hills Hotel", "9641 Sunset Blvd, Beverly Hills, CA", "90210"),
            (51.5194, -0.1270, "tourist_attraction", "Big Ben", "Westminster, London", "SW1A 0AA"),
            (35.6895, 139.6917, "restaurant", "Narisawa", "2-6-15 Minato, Minato City, Tokyo", "107-0062"),
            (48.8606, 2.3376, "tourist_attraction", "Louvre Museum", "Rue de Rivoli, Paris", "75001"),
            
            # Even more places for pagination
            (40.7505, -73.9934, "hotel", "The Plaza", "768 5th Ave, New York, NY", "10019"),
            (34.0928, -118.3287, "tourist_attraction", "Hollywood Walk of Fame", "Hollywood Blvd, Los Angeles, CA", "90028"),
            (51.5033, -0.1195, "restaurant", "Gordon Ramsay Restaurant", "68 Royal Hospital Rd, London", "SW3 4HP"),
            (35.6812, 139.7671, "hotel", "Park Hyatt Tokyo", "3-7-1-2 Nishi-Shinjuku, Tokyo", "163-1055"),
            (48.8589, 2.3200, "restaurant", "L'Arpège", "84 Rue de Varenne, Paris", "75007"),
            
            # Final batch for pagination testing
            (40.7587, -73.9787, "restaurant", "Per Se", "10 Columbus Circle, New York, NY", "10019"),
            (34.0522, -118.2437, "hotel", "The Beverly Hills Hotel", "9641 Sunset Blvd, Beverly Hills, CA", "90210"),
            (51.5074, -0.1278, "tourist_attraction", "Buckingham Palace", "London", "SW1A 1AA"),
            (35.6762, 139.6503, "hotel", "Aman Tokyo", "1-5-6 Otemachi, Tokyo", "100-0004"),
            (48.8566, 2.3522, "hotel", "Four Seasons Hotel George V", "31 Avenue George V, Paris", "75008"),
            
            # Additional variety
            (40.7829, -73.9654, "restaurant", "Eleven Madison Park", "11 Madison Ave, New York, NY", "10010"),
            (34.0736, -118.2400, "tourist_attraction", "Rodeo Drive", "Beverly Hills, CA", "90210"),
            (51.4994, -0.1245, "restaurant", "Sketch", "9 Conduit St, London", "W1S 2XG"),
            (35.6895, 139.6917, "tourist_attraction", "Shibuya Crossing", "Shibuya City, Tokyo", "150-0002"),
            (48.8584, 2.2945, "restaurant", "L'Astrance", "4 Rue Beethoven, Paris", "75016")
        ]
        
        for lat, lon, types, name, address, pincode in sample_places:
            success = db.add_place(lat, lon, types, name, address, pincode)
            if success:
                print(f"   ✅ Added: {name}")
            else:
                print(f"   ❌ Failed to add: {name}")
        
        # Test 2: Retrieve all places
        print("\n2. Retrieving all places...")
        places_df = db.get_all_places()
        print(f"   Found {len(places_df)} places:")
        for _, row in places_df.iterrows():
            print(f"   - {row['name']} ({row['types']})")
        
        # Test 3: Get specific place
        print("\n3. Getting specific place...")
        if not places_df.empty:
            first_place_id = places_df.iloc[0]['place_id']
            place = db.get_place_by_id(first_place_id)
            if place:
                print(f"   ✅ Found place: {place['name']}")
            else:
                print(f"   ❌ Place not found")
        
        # Test 4: Update place
        print("\n4. Updating a place...")
        if not places_df.empty:
            place_to_update = places_df.iloc[0]
            success = db.update_place(
                place_to_update['place_id'],
                place_to_update['latitude'],
                place_to_update['longitude'],
                "updated_" + place_to_update['types'],
                place_to_update['name'] + " (Updated)",
                place_to_update['address'],
                place_to_update['pincode']
            )
            if success:
                print(f"   ✅ Updated: {place_to_update['name']}")
            else:
                print(f"   ❌ Failed to update: {place_to_update['name']}")
        
        # Test 5: Search functionality
        print("\n5. Testing search functionality...")
        search_results = db.search_places("restaurant")
        print(f"   Found {len(search_results)} places matching 'restaurant'")
        
        # Test 6: Filter by type
        print("\n6. Testing filter by type...")
        hotel_results = db.get_places_by_type("hotel")
        print(f"   Found {len(hotel_results)} hotels")
        
        # Test 7: Pagination functionality
        print("\n7. Testing pagination functionality...")
        places_paginated, total_count = db.get_places_paginated(
            page=1, 
            page_size=10, 
            sort_by="name", 
            sort_order="ASC"
        )
        print(f"   Page 1 (10 items): {len(places_paginated)} places")
        print(f"   Total count: {total_count}")
        
        places_paginated_page2, _ = db.get_places_paginated(
            page=2, 
            page_size=10, 
            sort_by="name", 
            sort_order="ASC"
        )
        print(f"   Page 2 (10 items): {len(places_paginated_page2)} places")
        
        # Test 8: Search with pagination
        print("\n8. Testing search with pagination...")
        search_paginated, search_total = db.get_places_paginated(
            page=1,
            page_size=5,
            sort_by="name",
            sort_order="ASC",
            search_term="restaurant"
        )
        print(f"   Search results (page 1, 5 items): {len(search_paginated)} places")
        print(f"   Total search results: {search_total}")
        
        # Test 9: Sort functionality
        print("\n9. Testing sort functionality...")
        places_sorted_asc, _ = db.get_places_paginated(
            page=1,
            page_size=5,
            sort_by="name",
            sort_order="ASC"
        )
        print(f"   Sorted ASC by name (first 5):")
        for _, row in places_sorted_asc.iterrows():
            print(f"   - {row['name']}")
        
        places_sorted_desc, _ = db.get_places_paginated(
            page=1,
            page_size=5,
            sort_by="name",
            sort_order="DESC"
        )
        print(f"   Sorted DESC by name (first 5):")
        for _, row in places_sorted_desc.iterrows():
            print(f"   - {row['name']}")
        
        # Test 10: Delete a place
        print("\n10. Deleting a place...")
        if len(places_df) > 1:
            place_to_delete = places_df.iloc[1]
            success = db.delete_place(place_to_delete['place_id'])
            if success:
                print(f"   ✅ Deleted: {place_to_delete['name']}")
            else:
                print(f"   ❌ Failed to delete: {place_to_delete['name']}")
        
        # Test 11: Final count
        print("\n11. Final database state...")
        final_df = db.get_all_places()
        print(f"   Total places in database: {len(final_df)}")
        
        print("\n🎉 Database testing completed successfully!")
        print(f"📊 Total places available for pagination testing: {len(final_df)}")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def setup_instructions():
    """Display setup instructions."""
    print("""
📋 PostgreSQL Setup Instructions:

1. Your PostgreSQL database is already configured with the following details:
   - Host: db.evsjreawstqtkcsbwfjt.supabase.co
   - Port: 5432
   - Database: postgres
   - User: postgres
   - Password: F5jhYj-X3Wx!nf7

2. The .env file has been created with the correct credentials

3. The application will automatically create the places table on first run

4. To test the connection, run:
   python test_database.py

5. To start the application, run:
   streamlit run app.py

6. New Features Available:
   - Modern table with pagination (10, 25, 50, 100 entries per page)
   - Real-time search functionality
   - Sortable columns with visual indicators
   - Analytics dashboard with charts
   - Responsive design for mobile devices
   - Enhanced CRUD operations
""")

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        setup_instructions()
    else:
        test_database()
