"""
Refactored main application for the Places Management System.

This is the main Streamlit application file that uses the modular architecture
for better maintainability, debugging, and scalability.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configuration and utilities
try:
    from config.settings import (
        ui_config, db_config, excel_config, AppConstants, 
        validate_configuration
    )
    from utils.logger import get_logger, setup_logging
    from utils.database import PlacesDatabase
    from utils.error_handlers import (
        handle_errors, safe_execute, get_error_statistics,
        PlacesAppException, DatabaseError
    )
    from utils.validators import PlaceValidator
    from ui.components import DataTable, PlaceForm, TableControls
    from ui.add_place_page import render_add_place_page
    from analytics.dashboard import DashboardRenderer
    from api_testing.ola_maps_api_tester import APITestingUI
except ImportError as e:
    st.error(f"""
    ## Module Import Error
    
    Failed to import required modules: {e}
    
    Please ensure all modules are properly installed and accessible:
    1. Check that all files are in the correct directories
    2. Install missing dependencies: `pip install -r requirements.txt`
    3. Restart the application
    """)
    st.stop()

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title=ui_config.page_title,
    page_icon=ui_config.page_icon,
    layout=ui_config.layout,
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    .stButton > button {
        width: 100%;
        margin: 0.2rem 0;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)


class ApplicationState:
    """Manages application state and session variables."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables with default values."""
        logger.debug("Initializing session state")
        
        # Pagination state
        if AppConstants.SESSION_KEYS["CURRENT_PAGE"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = 1
        
        if AppConstants.SESSION_KEYS["PAGE_SIZE"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["PAGE_SIZE"]] = ui_config.default_page_size
        
        # Sorting state
        if AppConstants.SESSION_KEYS["SORT_BY"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["SORT_BY"]] = AppConstants.DEFAULT_SORT_COLUMN
        
        if AppConstants.SESSION_KEYS["SORT_ORDER"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["SORT_ORDER"]] = AppConstants.SORT_ORDERS["ASC"]
        
        # Search state
        if AppConstants.SESSION_KEYS["SEARCH_TERM"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["SEARCH_TERM"]] = ""
        
        # Edit mode state
        if AppConstants.SESSION_KEYS["EDIT_PLACE_ID"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["EDIT_PLACE_ID"]] = None
        
        if AppConstants.SESSION_KEYS["EDIT_MODE"] not in st.session_state:
            st.session_state[AppConstants.SESSION_KEYS["EDIT_MODE"]] = False
            
        if AppConstants.SESSION_KEYS["SELECTED_COLLECTION_KEY"] not in st.session_state:
            st.session_state.selected_collection_key = 'Elevation API.postman_collection.json'
        
        logger.debug("Session state initialized successfully")
    
    @staticmethod
    def reset_pagination():
        """Reset pagination to first page."""
        st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = 1
        logger.debug("Pagination reset to first page")
    
    @staticmethod
    def clear_edit_mode():
        """Clear edit mode state."""
        if AppConstants.SESSION_KEYS["EDIT_PLACE_ID"] in st.session_state:
            del st.session_state[AppConstants.SESSION_KEYS["EDIT_PLACE_ID"]]
        if AppConstants.SESSION_KEYS["EDIT_MODE"] in st.session_state:
            del st.session_state[AppConstants.SESSION_KEYS["EDIT_MODE"]]
        logger.debug("Edit mode cleared")


class DatabaseManager:
    """Manages database operations and connections."""
    
    @staticmethod
    @st.cache_resource
    def get_database_instance():
        """
        Get cached database instance.
        
        Returns:
            PlacesDatabase: Database instance or None if connection fails
        """
        logger.info("Initializing database connection")
        
        try:
            # Validate configuration first
            config_errors = validate_configuration()
            if config_errors:
                logger.error("Configuration validation failed", errors=config_errors)
                for error in config_errors:
                    st.error(f"Configuration Error: {error}")
                return None
            
            db = PlacesDatabase()
            
            # Verify the database instance is properly initialized
            if not hasattr(db, 'engine'):
                logger.error("Database instance missing engine attribute")
                st.error("Database initialization incomplete - missing engine")
                return None
            
            # Test the connection to ensure it's working
            if not db.test_connection():
                logger.error("Database connection test failed after initialization")
                st.error("Database connection test failed")
                return None
            
            logger.info("Database connection established successfully")
            return db
            
        except DatabaseError as e:
            logger.error("Database connection failed", error=str(e))
            st.error(f"""
            ## Database Connection Error
            
            **Error:** {e}
            
            **Please check:**
            1. Your PostgreSQL credentials in the `.env` file
            2. Database server is running and accessible
            3. Network connectivity
            4. Firewall settings
            """)
            return None
        except Exception as e:
            logger.error("Unexpected error during database initialization", error=str(e))
            st.error(f"Unexpected database error: {e}")
            return None
    
    @staticmethod
    def clear_cache():
        """Clear the cached database instance."""
        try:
            st.cache_resource.clear()
            logger.info("Database cache cleared")
        except Exception as e:
            logger.warning("Failed to clear database cache", error=str(e))


class PlaceOperations:
    """Handles all place-related operations."""
    
    def __init__(self, db: PlacesDatabase):
        """
        Initialize place operations with database instance.
        
        Args:
            db: Database instance
        """
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
    
    @handle_errors(show_user_message=True)
    def handle_add_place(self, form_data: dict) -> bool:
        """
        Handle adding a new place.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            bool: True if successful
        """
        self.logger.info("Processing add place request", place_name=form_data.get('name'))
        
        success = safe_execute(
            lambda: self.db.add_place(
                form_data['latitude'],
                form_data['longitude'], 
                form_data['types'],
                form_data['name'],
                form_data['address'],
                form_data['pincode']
            ),
            "add_place_operation",
            default_return=False
        )
        
        if success:
            self.logger.info("Place added successfully", place_name=form_data.get('name'))
            ApplicationState.reset_pagination()
            return True
        else:
            self.logger.error("Failed to add place", place_name=form_data.get('name'))
            return False
    
    @handle_errors(show_user_message=True)
    def handle_edit_place(self, form_data: dict) -> bool:
        """
        Handle editing an existing place.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            bool: True if successful
        """
        place_id = form_data['place_id']
        self.logger.info("Processing edit place request", place_id=place_id)
        
        success = safe_execute(
            lambda: self.db.update_place(
                place_id,
                form_data['latitude'],
                form_data['longitude'],
                form_data['types'], 
                form_data['name'],
                form_data['address'],
                form_data['pincode']
            ),
            "edit_place_operation",
            default_return=False
        )
        
        if success:
            self.logger.info("Place updated successfully", place_id=place_id)
            ApplicationState.clear_edit_mode()
            return True
        else:
            self.logger.error("Failed to update place", place_id=place_id)
            return False
    
    @handle_errors(show_user_message=True)
    def handle_delete_place(self, place_id: int) -> bool:
        """
        Handle deleting a place.
        
        Args:
            place_id: ID of place to delete
            
        Returns:
            bool: True if successful
        """
        self.logger.info("Processing delete place request", place_id=place_id)
        
        success = safe_execute(
            lambda: self.db.delete_place(place_id),
            "delete_place_operation", 
            default_return=False
        )
        
        if success:
            self.logger.info("Place deleted successfully", place_id=place_id)
            return True
        else:
            self.logger.error("Failed to delete place", place_id=place_id)
            return False
    
    @handle_errors(show_user_message=False)
    def get_place_for_editing(self, place_id: int) -> dict:
        """
        Get place data for editing.
        
        Args:
            place_id: ID of place to edit
            
        Returns:
            dict: Place data or None if not found
        """
        self.logger.debug("Retrieving place for editing", place_id=place_id)
        
        place_data = safe_execute(
            lambda: self.db.get_place_by_id(place_id),
            "get_place_for_edit",
            default_return=None
        )
        
        if place_data:
            self.logger.debug("Place data retrieved successfully", place_id=place_id)
        else:
            self.logger.warning("Place not found for editing", place_id=place_id)
        
        return place_data


def render_header():
    """Render the application header."""
    st.markdown(
        f'<h1 class="main-header">{ui_config.page_icon} Places Management System (Enhanced)</h1>', 
        unsafe_allow_html=True
    )
    
    # Add application info
    with st.expander("ℹ️ Application Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🏗️ Architecture:**
            - Modular design
            - Enhanced error handling
            - Comprehensive logging
            - Performance monitoring
            """)
        
        with col2:
            st.info("""
            **🛠️ Features:**
            - Advanced pagination
            - Real-time search
            - Data validation
            - Analytics dashboard
            """)
        
        with col3:
            # Show error statistics if available
            error_stats = get_error_statistics()
            if error_stats and error_stats['total_errors'] > 0:
                st.warning(f"""
                **⚠️ System Status:**
                - Total Errors: {error_stats['total_errors']}
                - Recent Issues: {len(error_stats['recent_errors'])}
                """)
            else:
                st.success("""
                **✅ System Status:**
                - All systems operational
                - No recent errors
                """)


def render_sidebar_navigation():
    """Render the sidebar navigation."""
    st.sidebar.title("🧭 Navigation")
    
    # Navigation options
    page = st.sidebar.selectbox(
        "Choose an action:",
        list(AppConstants.PAGES.values()),
        help="Select the page you want to navigate to"
    )
    
    # Additional sidebar information
    st.sidebar.markdown("---")
    
    # Quick stats
    with st.sidebar.expander("📊 Quick Stats"):
        db = DatabaseManager.get_database_instance()
        if db:
            try:
                # Try Excel first for faster loading
                all_places = safe_execute(
                    lambda: db.get_all_places(prefer_excel=excel_config.use_excel_cache),
                    "get_quick_stats",
                    default_return=None
                )
                
                if all_places is not None and not all_places.empty:
                    st.metric("Total Places", len(all_places))
                    st.metric("Unique Types", all_places['types'].nunique())
                    
                    # Show data source
                    source = "Excel Cache" if excel_config.use_excel_cache else "Database"
                    st.caption(f"📍 Data source: {source}")
                else:
                    st.info("No data available")
            except Exception:
                st.info("Stats unavailable")
    
    # Excel Management
    if excel_config.enable_excel_sync:
        with st.sidebar.expander("📈 Excel Management"):
            db = DatabaseManager.get_database_instance()
            if db:
                # Excel statistics
                excel_stats = safe_execute(
                    lambda: db.get_excel_statistics(),
                    "get_excel_stats",
                    default_return={}
                )
                
                if excel_stats and not excel_stats.get('error'):
                    st.metric("Excel Records", excel_stats.get('record_count', 0))
                    st.metric("File Size", f"{excel_stats.get('file_size_mb', 0):.2f} MB")
                    
                    sync_status = excel_stats.get('sync_status', 'unknown')
                    if sync_status == 'synced':
                        st.success("✅ Synced")
                    elif sync_status == 'out_of_sync':
                        st.warning(f"⚠️ Out of sync ({excel_stats.get('record_difference', 0)} records)")
                    else:
                        st.info("❓ Unknown status")
                
                # Management buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Force Sync", help="Force sync database to Excel"):
                        with st.spinner("Syncing..."):
                            success = safe_execute(
                                lambda: db.force_excel_sync(),
                                "force_sync_excel",
                                default_return=False
                            )
                            if success:
                                st.success("✅ Sync completed!")
                                st.rerun()
                            else:
                                st.error("❌ Sync failed")
                
                with col2:
                    if st.button("🗑️ Clear Cache", help="Clear Excel cache"):
                        safe_execute(
                            lambda: db.clear_excel_cache(),
                            "clear_excel_cache"
                        )
                        st.success("🧹 Cache cleared!")
                        st.rerun()
    
    # System information
    with st.sidebar.expander("🔧 System Info"):
        st.text(f"Database Host: {db_config.host if hasattr(db_config, 'host') else 'N/A'}")
        st.text(f"Excel Sync: {'✅ Enabled' if excel_config.enable_excel_sync else '❌ Disabled'}")
        st.text(f"Excel Cache: {'✅ Enabled' if excel_config.use_excel_cache else '❌ Disabled'}")
        st.text(f"Page Size: {st.session_state.get(AppConstants.SESSION_KEYS['PAGE_SIZE'], 'N/A')}")
        st.text(f"Current Page: {st.session_state.get(AppConstants.SESSION_KEYS['CURRENT_PAGE'], 'N/A')}")
    
    return page


def main():
    """Main application function."""
    logger.info("Starting Places Management System application")
    
    # Initialize session state
    ApplicationState.initialize_session_state()
    
    # Render header
    render_header()
    
    # Get database instance
    db = DatabaseManager.get_database_instance()
    if not db:
        st.error("""
        ## Database Connection Failed
        
        Unable to establish database connection. Please check your configuration and try again.
        
        **Troubleshooting:**
        1. Verify your `.env` file contains correct database credentials
        2. Check if the database server is accessible
        3. Try refreshing the page
        """)
        st.stop()
    
    # Verify database instance has required attributes
    if not hasattr(db, 'engine'):
        st.error("""
        ## Database Initialization Error
        
        Database instance is missing required attributes. This may be due to a caching issue.
        
        **Solution:** Please refresh the page to reinitialize the database connection.
        """)
        st.stop()
    
    # Initialize place operations
    place_ops = PlaceOperations(db)
    
    # Render navigation and get selected page
    selected_page = render_sidebar_navigation()
    
    logger.debug("Page selected", page=selected_page)
    
    # Route to appropriate page handler
    try:
        if selected_page == AppConstants.PAGES["VIEW_ALL"]:
            render_view_all_page(db, place_ops)
        elif selected_page == AppConstants.PAGES["ADD_NEW"]:
            render_add_place_page(place_ops)
        elif selected_page == AppConstants.PAGES["SEARCH"]:
            render_search_page(db, place_ops)
        elif selected_page == AppConstants.PAGES["ANALYTICS"]:
            render_analytics_page(db)
        elif selected_page == AppConstants.PAGES["API_TESTING"]:
            render_api_testing_page()
        else:
            st.error(f"Unknown page: {selected_page}")
    
    except Exception as e:
        logger.error("Error rendering page", page=selected_page, error=str(e))
        st.error(f"An error occurred while loading the page: {e}")
    
    # Render footer
    render_footer()


def render_view_all_page(db: PlacesDatabase, place_ops: PlaceOperations):
    """Render the view all places page."""
    logger.debug("Rendering view all places page")
    
    # Header with performance toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📋 All Places")
    
    with col2:
        if excel_config.enable_excel_sync:
            use_fast_mode = st.checkbox(
                "⚡ Fast Mode", 
                value=excel_config.use_excel_cache,
                help="Use Excel cache for faster response times"
            )
        else:
            use_fast_mode = False
    
    # Get current pagination settings
    current_page = st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]]
    page_size = st.session_state[AppConstants.SESSION_KEYS["PAGE_SIZE"]]
    sort_by = st.session_state[AppConstants.SESSION_KEYS["SORT_BY"]]
    sort_order = st.session_state[AppConstants.SESSION_KEYS["SORT_ORDER"]]
    search_term = st.session_state[AppConstants.SESSION_KEYS["SEARCH_TERM"]]
    
    # Show loading indicator
    loading_text = "⚡ Loading from Excel cache..." if use_fast_mode else "🗄️ Loading from database..."
    
    # Get paginated data
    with st.spinner(loading_text):
        places_df, total_count = safe_execute(
            lambda: db.get_places_paginated(
                page=current_page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
                search_term=search_term
            ),
            "get_paginated_places",
            default_return=(None, 0)
        )
    
    if places_df is None:
        st.error("Failed to load places data")
        return
    
    # Define action handlers
    def handle_edit(place_id: int):
        st.session_state[AppConstants.SESSION_KEYS["EDIT_PLACE_ID"]] = place_id
        st.session_state[AppConstants.SESSION_KEYS["EDIT_MODE"]] = True
        st.rerun()
    
    def handle_delete(place_id: int):
        if place_ops.handle_delete_place(place_id):
            st.success("Place deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete place")
    
    def handle_view(place_id: int):
        place_data = place_ops.get_place_for_editing(place_id)
        if place_data:
            st.info(f"""
            **Place Details:**
            - **ID:** {place_data['place_id']}
            - **Name:** {place_data['name']}
            - **Type:** {place_data['types']}
            - **Address:** {place_data['address']}
            - **Coordinates:** {place_data['latitude']:.6f}, {place_data['longitude']:.6f}
            - **Pincode:** {place_data['pincode']}
            - **Created:** {place_data.get('created_at', 'N/A')}
            """)
    
    # Check if in edit mode
    edit_place_id = st.session_state.get(AppConstants.SESSION_KEYS["EDIT_PLACE_ID"])
    edit_mode = st.session_state.get(AppConstants.SESSION_KEYS["EDIT_MODE"])
    
    if edit_mode and edit_place_id:
        # Render edit form
        place_data = place_ops.get_place_for_editing(edit_place_id)
        if place_data:
            PlaceForm.render_edit_place_form(
                place_data=place_data,
                on_submit=place_ops.handle_edit_place,
                on_cancel=lambda: ApplicationState.clear_edit_mode()
            )
        else:
            st.error("Place not found for editing")
            ApplicationState.clear_edit_mode()
    else:
        # Render places table
        DataTable.render_places_table(
            places_df=places_df,
            total_count=total_count,
            on_edit=handle_edit,
            on_delete=handle_delete,
            on_view=handle_view
        )


def render_add_place_page(place_ops: PlaceOperations):
    """Render the add new place page."""
    logger.debug("Rendering add place page")
    
    # Import and use the modular add place page
    from ui.add_place_page import render_add_place_page as render_add_place_page_module
    render_add_place_page_module(place_ops)


def render_search_page(db: PlacesDatabase, place_ops: PlaceOperations):
    """Render the search places page."""
    logger.debug("Rendering search page")
    
    st.header("🔍 Search Places")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input(
            "Search by name, type, or address:", 
            placeholder="Enter search term...",
            help="Search across place names, types, and addresses"
        )
        if st.button("🔍 Search", type="primary"):
            if search_term:
                st.session_state[AppConstants.SESSION_KEYS["SEARCH_TERM"]] = search_term
                ApplicationState.reset_pagination()
                st.rerun()
            else:
                st.warning("Please enter a search term")
    
    with col2:
        # Type filter
        place_types = ["All Types"] + db_config.place_types if hasattr(db_config, 'place_types') else ["All Types"]
        selected_type = st.selectbox(
            "Filter by type:", 
            place_types,
            help="Filter places by their type"
        )
        if st.button("🎯 Filter", type="secondary"):
            if selected_type != "All Types":
                # Get places by type
                places_df, total_count = safe_execute(
                    lambda: db.get_places_by_type_paginated(
                        selected_type,
                        page=st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]],
                        page_size=st.session_state[AppConstants.SESSION_KEYS["PAGE_SIZE"]],
                        sort_by=st.session_state[AppConstants.SESSION_KEYS["SORT_BY"]],
                        sort_order=st.session_state[AppConstants.SESSION_KEYS["SORT_ORDER"]]
                    ),
                    "get_places_by_type",
                    default_return=(None, 0)
                )
                
                if places_df is not None:
                    DataTable.render_places_table(places_df, total_count)
            else:
                st.session_state[AppConstants.SESSION_KEYS["SEARCH_TERM"]] = ""
                st.rerun()


def render_analytics_page(db: PlacesDatabase):
    """Render the analytics dashboard page."""
    logger.debug("Rendering analytics page")
    
    # Add performance toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        use_excel_cache = st.checkbox(
            "⚡ Fast Mode (Excel Cache)", 
            value=excel_config.use_excel_cache,
            help="Use Excel cache for faster loading. May show slightly outdated data."
        )
    
    with col1:
        st.markdown("### 📊 Analytics Dashboard")
    
    # Get all data for analytics
    with st.spinner("📊 Loading analytics data..."):
        all_places = safe_execute(
            lambda: db.get_all_places(prefer_excel=use_excel_cache),
            "get_all_places_for_analytics", 
            default_return=None
        )
    
    if all_places is None:
        st.error("Failed to load data for analytics")
        return
    
    if all_places.empty:
        st.info("📭 No data available for analytics. Add some places first!")
        return
    
    # Show data info
    data_source = "Excel Cache" if use_excel_cache and excel_config.enable_excel_sync else "Database"
    st.info(f"📍 Analyzing {len(all_places)} places from {data_source}")
    
    # Render analytics dashboard
    DashboardRenderer.render_analytics_dashboard(all_places)


def render_api_testing_page():
    """Render the OLA Maps API testing page."""
    logger.debug("Rendering API testing page")
    
    try:
        # Initialize API testing UI
        api_ui = APITestingUI()
        
        # Render the API testing interface
        api_ui.render()
        
    except Exception as e:
        logger.error("Error rendering API testing page", error=str(e))
        st.error(f"""
        ## API Testing Error
        
        An error occurred while loading the API testing interface: {e}
        
        Please check the logs for more information.
        """)


def render_footer():
    """Render the application footer."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <h3>🗺️ Places Management System - Enhanced Version</h3>
        <p>Built with Streamlit, PostgreSQL, and ❤️</p>
        <p><strong>Features:</strong> Modular Architecture | Comprehensive Logging | Advanced Analytics | Error Handling</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("Critical application error", error=str(e))
        st.error(f"""
        ## Critical Application Error
        
        A critical error occurred: {e}
        
        Please contact support or check the logs for more information.
        """)
        st.stop()
