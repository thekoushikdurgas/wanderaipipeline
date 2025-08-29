import streamlit as st
import pandas as pd
from utils.database import PlacesDatabase
import re
import os
from dotenv import load_dotenv
import plotly.express as px
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Places CRUD Application - PostgreSQL",
    page_icon="🗺️",
    layout="wide"
)

# Initialize database
@st.cache_resource
def get_database():
    try:
        return PlacesDatabase()
    except ValueError as e:
        st.error(f"Database configuration error: {e}")
        st.info("Please set up your Supabase credentials in the .env file")
        return None

db = get_database()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.2rem 0;
    }
    .action-buttons {
        display: flex;
        gap: 0.5rem;
    }
    .action-buttons > button {
        flex: 1;
        font-size: 0.8rem;
        padding: 0.3rem 0.6rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .search-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .modern-table {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        margin: 20px 0;
    }
    .table-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    .table-controls {
        display: flex;
        align-items: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    .entries-control {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .search-control {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pagination-info {
        background: #f8f9fa;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🗺️ Places Management System (PostgreSQL)</h1>', unsafe_allow_html=True)

# Check if database is available
if db is None:
    st.error("""
    ## Database Connection Error
    
    Please set up your PostgreSQL credentials:
    
    1. Create a `.env` file in the project root
    2. Add your database credentials:
    ```
    DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
    user=postgres
    password=[YOUR-PASSWORD]
    host=[HOST]
    port=5432
    dbname=postgres
    ```
    3. Restart the application
    """)
    st.stop()

# Initialize session state for pagination
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'page_size' not in st.session_state:
    st.session_state.page_size = 10
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = 'place_id'
if 'sort_order' not in st.session_state:
    st.session_state.sort_order = 'ASC'
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''
if 'selected_collection_key' not in st.session_state:
    st.session_state.selected_collection_key = 'OLAMAPSapi.postman_collection.json'

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose an action:",
    ["View All Places", "Add New Place", "Search Places", "Analytics Dashboard"]
)

# Validation functions
def validate_coordinates(lat, lon):
    """Validate latitude and longitude coordinates."""
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except ValueError:
        return False

def validate_pincode(pincode):
    """Validate pincode format (6 digits)."""
    return bool(re.match(r'^\d{6}$', pincode))

def render_modern_table(places_df, total_count):
    """Render a modern table with pagination and search."""
    if places_df.empty:
        st.info("No places found. Add some places to get started!")
        return
    
    # Table header with controls
    col2, col3 = st.columns([1, 3])
    with col2:
        page_size = st.selectbox(
            "Entries per page:",
            [10, 25, 50, 100],
            index=[10, 25, 50, 100].index(st.session_state.page_size),
            key="page_size_selector"
        )
        if page_size != st.session_state.page_size:
            st.session_state.page_size = page_size
            st.session_state.current_page = 1
            st.rerun()
    
    with col3:
        search_term = st.text_input(
            "Search:",
            value=st.session_state.search_term,
            placeholder="Search places...",
            key="search_input"
        )
        if search_term != st.session_state.search_term:
            st.session_state.search_term = search_term
            st.session_state.current_page = 1
            st.rerun()
    
    # Display places in a modern table format with action buttons
    st.markdown("""
    <style>
    .places-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    .places-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 14px;
    }
    .places-table td {
        padding: 12px;
        border-bottom: 1px solid #dee2e6;
        font-size: 14px;
        color: #495057;
    }
    .places-table tbody tr:hover {
        background-color: #f8f9fa;
    }
    .places-table tbody tr:nth-child(even) {
        background-color: #fafbfc;
    }
    .action-buttons {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .btn-edit, .btn-delete {
        padding: 6px 12px;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .btn-edit {
        background-color: #17a2b8;
        color: white;
    }
    .btn-edit:hover {
        background-color: #138496;
        transform: translateY(-1px);
    }
    .btn-delete {
        background-color: #dc3545;
        color: white;
    }
    .btn-delete:hover {
        background-color: #c82333;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display data using Streamlit's native dataframe with custom formatting
    display_df = places_df[['name', 'types', 'address', 'latitude', 'longitude', 'pincode']].copy()
    display_df['Coordinates'] = display_df['latitude'].astype(str) + ', ' + display_df['longitude'].astype(str)
    display_df = display_df.drop(['latitude', 'longitude'], axis=1)
    
    # Rename columns for better display
    display_df.columns = ['Name', 'Type', 'Address', 'Pincode', 'Coordinates']
    
    # Display the table using Streamlit's dataframe
    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Address": st.column_config.TextColumn("Address", width="large"),
            "Pincode": st.column_config.TextColumn("Pincode", width="small"),
            "Coordinates": st.column_config.TextColumn("Coordinates", width="medium")
        }
    )
    
    # Handle edit and delete actions using Streamlit buttons
    st.markdown("### Action Buttons")
    
    # Create a more organized layout for action buttons
    for index, row in places_df.iterrows():
        place_id = row['place_id']
        name = row['name']
        types = row['types']
        
        # Create an expander for each place with action buttons
        with st.expander(f"📍 {name} ({types})", expanded=False):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**Address:** {row['address']}")
                st.write(f"**Coordinates:** {row['latitude']:.6f}, {row['longitude']:.6f}")
                st.write(f"**Pincode:** {row['pincode']}")
            
            with col2:
                # Edit button
                if st.button("✏️ Edit", key=f"edit_btn_{place_id}", type="primary"):
                    st.session_state.edit_place_id = place_id
                    st.session_state.edit_mode = True
                    st.rerun()
            
            with col3:
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_btn_{place_id}", type="secondary"):
                    if db.delete_place(place_id):
                        st.success(f"Place '{name}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete place '{name}'. Please try again.")
            
            with col4:
                # View details button
                if st.button("👁️ View", key=f"view_btn_{place_id}"):
                    st.info(f"**Place Details:**\n- **ID:** {place_id}\n- **Name:** {name}\n- **Type:** {types}\n- **Address:** {row['address']}\n- **Coordinates:** {row['latitude']:.6f}, {row['longitude']:.6f}\n- **Pincode:** {row['pincode']}")
            
            # Check if this place is being edited
            if 'edit_place_id' in st.session_state and st.session_state.edit_place_id == place_id and st.session_state.edit_mode:
                st.markdown("---")
                
                # Enhanced Edit Place Page within expander
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
                    <h2 style='margin: 0; text-align: center;'>✏️ Edit Place Page</h2>
                    <p style='margin: 5px 0 0 0; text-align: center; opacity: 0.9;'>Modify place information below</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Get the place data for editing
                place = db.get_place_by_id(place_id)
                if place:
                    # Current place information display
                    st.markdown("### 📍 Current Place Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Current Details:**
                        - **Name:** {place['name']}
                        - **Type:** {place['types']}
                        - **Address:** {place['address']}
                        """)
                    
                    with col2:
                        st.info(f"""
                        **Location Details:**
                        - **Latitude:** {place['latitude']:.6f}
                        - **Longitude:** {place['longitude']:.6f}
                        - **Pincode:** {place['pincode']}
                        - **Created:** {place['created_at']}
                        """)
                    
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Form")
                    
                    with st.form(f"edit_place_form_{place_id}"):
                        # Form header
                        st.markdown("**Please update the place information:**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Basic Information")
                            edit_name = st.text_input("Place Name *", value=place['name'], key=f"edit_name_{place_id}", 
                                                     help="Enter the name of the place")
                            edit_address = st.text_area("Address *", value=place['address'], key=f"edit_address_{place_id}", 
                                                       help="Enter the full address of the place", height=100)
                            edit_types = st.text_input("Types *", value=place['types'], key=f"edit_types_{place_id}", 
                                                      help="Enter place types (e.g., restaurant, hotel, tourist_attraction)")
                        
                        with col2:
                            st.markdown("#### Location Information")
                            edit_latitude = st.number_input("Latitude *", min_value=-90.0, max_value=90.0, 
                                                           value=float(place['latitude']), format="%.6f", 
                                                           key=f"edit_lat_{place_id}", 
                                                           help="Latitude must be between -90 and 90")
                            edit_longitude = st.number_input("Longitude *", min_value=-180.0, max_value=180.0, 
                                                            value=float(place['longitude']), format="%.6f", 
                                                            key=f"edit_lon_{place_id}", 
                                                            help="Longitude must be between -180 and 180")
                            edit_pincode = st.text_input("Pincode *", value=place['pincode'], max_chars=6, 
                                                        key=f"edit_pincode_{place_id}", 
                                                        help="Enter 6-digit postal code")
                        
                        # Action buttons
                        st.markdown("---")
                        st.markdown("### Action Buttons")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            submitted = st.form_submit_button("💾 Update Place", type="primary", 
                                                            help="Save the changes to the database")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel", 
                                                   help="Cancel editing and return to view mode"):
                                del st.session_state.edit_place_id
                                del st.session_state.edit_mode
                                st.rerun()
                        
                        with col3:
                            if st.form_submit_button("🔄 Reset to Original", 
                                                   help="Reset all fields to original values"):
                                st.rerun()
                        
                        with col4:
                            if st.form_submit_button("👁️ Preview Changes", 
                                                   help="Preview the changes before saving"):
                                st.info(f"""
                                **Preview of Changes:**
                                - **Name:** {place['name']} → {edit_name}
                                - **Type:** {place['types']} → {edit_types}
                                - **Address:** {place['address']} → {edit_address}
                                - **Coordinates:** {place['latitude']:.6f}, {place['longitude']:.6f} → {edit_latitude:.6f}, {edit_longitude:.6f}
                                - **Pincode:** {place['pincode']} → {edit_pincode}
                                """)
                        
                        if submitted:
                            # Validation
                            if not all([edit_name, edit_address, edit_types, edit_pincode]):
                                st.error("❌ **Validation Error:** Please fill in all required fields.")
                            elif not validate_pincode(edit_pincode):
                                st.error("❌ **Validation Error:** Please enter a valid 6-digit pincode.")
                            elif not validate_coordinates(edit_latitude, edit_longitude):
                                st.error("❌ **Validation Error:** Please enter valid coordinates.")
                            else:
                                # Show processing message
                                with st.spinner("🔄 Updating place information..."):
                                    if db.update_place(place_id, edit_latitude, edit_longitude, edit_types, edit_name, edit_address, edit_pincode):
                                        st.success(f"""
                                        ✅ **Success!** Place '{edit_name}' has been updated successfully!
                                        
                                        **Updated Information:**
                                        - **Name:** {edit_name}
                                        - **Type:** {edit_types}
                                        - **Address:** {edit_address}
                                        - **Coordinates:** {edit_latitude:.6f}, {edit_longitude:.6f}
                                        - **Pincode:** {edit_pincode}
                                        """)
                                        del st.session_state.edit_place_id
                                        del st.session_state.edit_mode
                                        st.rerun()
                                    else:
                                        st.error("❌ **Error:** Failed to update place. Please try again.")
                else:
                    st.error("❌ **Error:** Place not found in database.")
                    del st.session_state.edit_place_id
                    del st.session_state.edit_mode
    
    # Pagination info
    total_pages = (total_count + st.session_state.page_size - 1) // st.session_state.page_size
    start_entry = (st.session_state.current_page - 1) * st.session_state.page_size + 1
    end_entry = min(st.session_state.current_page * st.session_state.page_size, total_count)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"**Showing {start_entry} to {end_entry} of {total_count} entries**")
    
    with col2:
        # Pagination controls
        pagination_cols = st.columns(7)
        
        # First page
        if pagination_cols[0].button("«", key="first_page"):
            st.session_state.current_page = 1
            st.rerun()
        
        # Previous page
        if pagination_cols[1].button("‹", key="prev_page"):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
        
        # Page numbers
        start_page = max(1, st.session_state.current_page - 2)
        end_page = min(total_pages, st.session_state.current_page + 2)
        
        for i, page_num in enumerate(range(start_page, end_page + 1)):
            if i < 3:  # Limit to 3 page number buttons
                if pagination_cols[2 + i].button(
                    str(page_num),
                    key=f"page_{page_num}",
                    type="primary" if page_num == st.session_state.current_page else "secondary"
                ):
                    st.session_state.current_page = page_num
                    st.rerun()
        
        # Next page
        if pagination_cols[5].button("›", key="next_page"):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()
        
        # Last page
        if pagination_cols[6].button("»", key="last_page"):
            st.session_state.current_page = total_pages
            st.rerun()

# View All Places Page
if page == "View All Places":
    st.header("📋 All Places")
    
    # Get paginated data
    places_df, total_count = db.get_places_paginated(
        page=st.session_state.current_page,
        page_size=st.session_state.page_size,
        sort_by=st.session_state.sort_by,
        sort_order=st.session_state.sort_order,
        search_term=st.session_state.search_term
    )
    
    render_modern_table(places_df, total_count)

# Search Places Page
elif page == "Search Places":
    st.header("🔍 Search Places")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search by name or type:", placeholder="Enter search term...")
        if st.button("Search"):
            if search_term:
                st.session_state.search_term = search_term
                st.session_state.current_page = 1
                st.rerun()
            else:
                st.warning("Please enter a search term")
    
    with col2:
        place_types = ["restaurant", "hotel", "tourist_attraction", "museum", "park", "shopping_mall"]
        selected_type = st.selectbox("Filter by type:", ["All Types"] + place_types)
        if st.button("Filter"):
            if selected_type != "All Types":
                places_df, total_count = db.get_places_by_type_paginated(
                    selected_type,
                    page=st.session_state.current_page,
                    page_size=st.session_state.page_size,
                    sort_by=st.session_state.sort_by,
                    sort_order=st.session_state.sort_order
                )
                render_modern_table(places_df, total_count)
            else:
                places_df, total_count = db.get_places_paginated(
                    page=st.session_state.current_page,
                    page_size=st.session_state.page_size,
                    sort_by=st.session_state.sort_by,
                    sort_order=st.session_state.sort_order
                )
                render_modern_table(places_df, total_count)

# Analytics Dashboard Page
elif page == "Analytics Dashboard":
    st.header("📊 Analytics Dashboard")
    
    # Get all data for analytics
    all_places = db.get_all_places()
    
    if not all_places.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Places", len(all_places))
        
        with col2:
            unique_types = all_places['types'].nunique()
            st.metric("Unique Types", unique_types)
        
        with col3:
            avg_lat = all_places['latitude'].mean()
            st.metric("Avg Latitude", f"{avg_lat:.4f}")
        
        with col4:
            avg_lon = all_places['longitude'].mean()
            st.metric("Avg Longitude", f"{avg_lon:.4f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Places by type
            type_counts = all_places['types'].value_counts()
            fig_types = px.bar(
                x=type_counts.values,
                y=type_counts.index,
                orientation='h',
                title="Places by Type",
                labels={'x': 'Count', 'y': 'Type'}
            )
            st.plotly_chart(fig_types, width='stretch')
        
        with col2:
            # Geographic distribution
            fig_map = px.scatter_map(
                all_places,
                lat='latitude',
                lon='longitude',
                hover_name='name',
                hover_data=['types', 'address'],
                title="Geographic Distribution",
                zoom=1
            )
            fig_map.update_layout(
                map_style="open-street-map",
                margin={"r":0,"t":30,"l":0,"b":0}
            )
            st.plotly_chart(fig_map, width='stretch')
        
        # Recent activity
        st.subheader("Recent Activity")
        recent_places = all_places.sort_values('created_at', ascending=False).head(10)
        st.dataframe(
            recent_places[['name', 'types', 'address', 'created_at']],
            width='stretch'
        )
    else:
        st.info("No data available for analytics. Add some places first!")

# Add New Place Page
elif page == "Add New Place":
    st.header("➕ Add New Place")
    
    with st.form("add_place_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Place Name *", placeholder="Enter place name")
            address = st.text_area("Address *", placeholder="Enter full address")
            types = st.text_input("Types *", placeholder="e.g., restaurant, hotel, tourist_attraction")
        
        with col2:
            latitude = st.number_input("Latitude *", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
            longitude = st.number_input("Longitude *", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")
            pincode = st.text_input("Pincode *", placeholder="6-digit pincode", max_chars=6)
        
        submitted = st.form_submit_button("Add Place")
        
        if submitted:
            # Validation
            if not all([name, address, types, pincode]):
                st.error("Please fill in all required fields.")
            elif not validate_pincode(pincode):
                st.error("Please enter a valid 6-digit pincode.")
            elif not validate_coordinates(latitude, longitude):
                st.error("Please enter valid coordinates.")
            else:
                if db.add_place(latitude, longitude, types, name, address, pincode):
                    st.success(f"Place '{name}' added successfully!")
                    # Clear form
                    st.rerun()
                else:
                    st.error("Failed to add place. Please try again.")



# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Places Management System | Built with Streamlit & PostgreSQL</p>
</div>
""", unsafe_allow_html=True)
