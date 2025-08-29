"""
UI Components for the Places Management System.

This module contains reusable UI components for the Streamlit application,
including table rendering, forms, and other interactive elements.
Optimized with numpy and pandas vectorization for faster response times.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime

# Import utilities and configuration
try:
    from config.settings import ui_config, AppConstants
    from utils.logger import get_logger
    from utils.validators import PlaceValidator, ValidationResult
    from utils.error_handlers import handle_errors, safe_execute
except ImportError:
    # Fallback imports for development
    class MockConfig:
        default_page_size = 10
        page_size_options = [10, 25, 50, 100]
        search_placeholder = "Search places..."
    
    class MockConstants:
        SESSION_KEYS = {
            "CURRENT_PAGE": "current_page",
            "PAGE_SIZE": "page_size", 
            "SORT_BY": "sort_by",
            "SORT_ORDER": "sort_order",
            "SEARCH_TERM": "search_term",
            "EDIT_PLACE_ID": "edit_place_id",
            "EDIT_MODE": "edit_mode"
        }
    
    ui_config = MockConfig()
    AppConstants = MockConstants()
    
    class MockLogger:
        def debug(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def info(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def warning(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def error(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
    
    def get_logger(_name):
        # Mock function - parameter name ignored
        return MockLogger()
    
    def handle_errors(**_kwargs):
        # Mock decorator - kwargs ignored
        def decorator(func):
            return func
        return decorator
    
    def safe_execute(op, _name, default=None, _context=None):
        # Mock function - execute operation with basic error handling
        try:
            return op()
        except Exception:  # Catch specific exception type
            return default

logger = get_logger(__name__)


class TableControls:
    """Component for table pagination and search controls with optimized operations."""
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def render_search_and_pagination_controls(total_count: int) -> Tuple[int, str]:
        """
        Render search and pagination controls with optimized state management.
        
        Args:
            total_count: Total number of records
            
        Returns:
            Tuple of (page_size, search_term)
        """
        logger.debug("Rendering table controls", total_count=total_count)
        
        # Create columns for controls
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Page size selector with optimized options
            current_page_size = st.session_state.get(AppConstants.SESSION_KEYS["PAGE_SIZE"], ui_config.default_page_size)
            page_size_index = ui_config.page_size_options.index(current_page_size) if current_page_size in ui_config.page_size_options else 0
            
            page_size = st.selectbox(
                "Entries per page:",
                ui_config.page_size_options,
                index=page_size_index,
                key="page_size_selector",
                help="Select number of entries to display per page"
            )
            
            # Update session state if page size changed
            if page_size != st.session_state.get(AppConstants.SESSION_KEYS["PAGE_SIZE"]):
                st.session_state[AppConstants.SESSION_KEYS["PAGE_SIZE"]] = page_size
                st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = 1
                logger.debug("Page size changed", new_size=page_size)
                st.rerun()
        
        with col2:
            # Search input with optimized state management
            current_search = st.session_state.get(AppConstants.SESSION_KEYS["SEARCH_TERM"], "")
            search_term = st.text_input(
                "Search:",
                value=current_search,
                placeholder=ui_config.search_placeholder,
                key="search_input",
                help="Search places by name, type, or address"
            )
            
            # Update session state if search term changed
            if search_term != current_search:
                st.session_state[AppConstants.SESSION_KEYS["SEARCH_TERM"]] = search_term
                st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = 1
                logger.debug("Search term changed", term=search_term[:50])
                st.rerun()
        
        return page_size, search_term
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def render_pagination_controls(total_count: int, page_size: int) -> None:
        """
        Render pagination controls at the bottom of the table with optimized calculations.
        
        Args:
            total_count: Total number of records
            page_size: Number of records per page
        """
        logger.debug("Rendering pagination controls", total_count=total_count, page_size=page_size)
        
        if total_count == 0:
            return
        
        current_page = st.session_state.get(AppConstants.SESSION_KEYS["CURRENT_PAGE"], 1)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Optimized entry calculation
        start_entry = (current_page - 1) * page_size + 1
        end_entry = min(current_page * page_size, total_count)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"**Showing {start_entry} to {end_entry} of {total_count} entries**")
        
        with col2:
            if total_pages > 1:
                # Create pagination buttons with optimized layout
                pagination_cols = st.columns(7)
                
                # First page button
                if pagination_cols[0].button("«", key="first_page", help="Go to first page"):
                    st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = 1
                    logger.debug("Navigation to first page")
                    st.rerun()
                
                # Previous page button
                if pagination_cols[1].button("‹", key="prev_page", help="Go to previous page"):
                    if current_page > 1:
                        st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = current_page - 1
                        logger.debug("Navigation to previous page", page=current_page - 1)
                        st.rerun()
                
                # Page number buttons (show 3 pages around current)
                start_page = max(1, current_page - 1)
                end_page = min(total_pages, current_page + 1)
                
                # Use numpy for optimized page range calculation
                page_range = np.arange(start_page, end_page + 1)
                for i, page_num in enumerate(page_range):
                    if i < 3:  # Limit to 3 page number buttons
                        button_type = "primary" if page_num == current_page else "secondary"
                        if pagination_cols[2 + i].button(
                            str(page_num),
                            key=f"page_{page_num}",
                            type=button_type,
                            help=f"Go to page {page_num}"
                        ):
                            st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = page_num
                            logger.debug("Navigation to page", page=page_num)
                            st.rerun()
                
                # Next page button
                if pagination_cols[5].button("›", key="next_page", help="Go to next page"):
                    if current_page < total_pages:
                        st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = current_page + 1
                        logger.debug("Navigation to next page", page=current_page + 1)
                        st.rerun()
                
                # Last page button
                if pagination_cols[6].button("»", key="last_page", help="Go to last page"):
                    st.session_state[AppConstants.SESSION_KEYS["CURRENT_PAGE"]] = total_pages
                    logger.debug("Navigation to last page", page=total_pages)
                    st.rerun()


class DataTable:
    """Component for rendering data tables with actions and optimized data processing."""
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error displaying table data")
    def render_places_table(
        places_df: pd.DataFrame, 
        total_count: int,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_view: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Render the main places table with actions using optimized data processing.
        
        Args:
            places_df: DataFrame containing place data
            total_count: Total number of records
            on_edit: Callback function for edit action
            on_delete: Callback function for delete action  
            on_view: Callback function for view action
        """
        logger.debug("Rendering places table", 
                    records_count=len(places_df), 
                    total_count=total_count)
        
        if places_df.empty:
            st.info("📭 No places found. Add some places to get started!")
            return
        
        # Render controls
        page_size, search_term = TableControls.render_search_and_pagination_controls(total_count)
        
        # Custom CSS for table styling
        DataTable._inject_table_styles()
        
        # Display data using Streamlit's native dataframe with optimized formatting
        display_df = DataTable._prepare_display_dataframe_optimized(places_df)
        
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
        
        # Render action buttons for each place
        DataTable._render_action_buttons(places_df, on_edit, on_delete, on_view)
        
        # Render pagination controls
        TableControls.render_pagination_controls(total_count, page_size)
    
    @staticmethod
    def _prepare_display_dataframe_optimized(places_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare dataframe for display by formatting columns using vectorized operations.
        
        Args:
            places_df: Original places dataframe
            
        Returns:
            Formatted dataframe for display
        """
        logger.debug("Preparing display dataframe", columns=list(places_df.columns))
        
        # Use vectorized operations for better performance
        display_df = places_df[['name', 'types', 'address', 'latitude', 'longitude', 'pincode']].copy()
        
        # Vectorized coordinate formatting using numpy
        lat_array = display_df['latitude'].to_numpy()
        lon_array = display_df['longitude'].to_numpy()
        
        # Create coordinates column using vectorized string formatting
        coordinates = np.char.add(
            np.char.add(
                lat_array.astype(str), 
                ', '
            ),
            lon_array.astype(str)
        )
        
        display_df['Coordinates'] = coordinates
        
        # Drop individual coordinate columns
        display_df = display_df.drop(['latitude', 'longitude'], axis=1)
        
        # Rename columns for better display
        display_df.columns = ['Name', 'Type', 'Address', 'Pincode', 'Coordinates']
        
        return display_df
    
    @staticmethod
    def _inject_table_styles() -> None:
        """Inject custom CSS styles for the table."""
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
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def _render_action_buttons(
        places_df: pd.DataFrame,
        on_edit: Optional[Callable[[int], None]],
        on_delete: Optional[Callable[[int], None]],
        on_view: Optional[Callable[[int], None]]
    ) -> None:
        """
        Render action buttons for each place using optimized iteration.
        
        Args:
            places_df: DataFrame containing place data
            on_edit: Callback function for edit action
            on_delete: Callback function for delete action
            on_view: Callback function for view action
        """
        logger.debug("Rendering action buttons", place_count=len(places_df))
        
        st.markdown("### 🔧 Actions")
        
        # Use vectorized operations for better performance
        place_ids = places_df['place_id'].to_numpy()
        names = places_df['name'].to_numpy()
        types = places_df['types'].to_numpy()
        
        # Create expandable sections for each place
        for i in range(len(places_df)):
            place_id = place_ids[i]
            name = names[i]
            place_type = types[i]
            
            # Create an expander for each place with action buttons
            with st.expander(f"📍 {name} ({place_type})", expanded=False):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**Address:** {places_df.iloc[i]['address']}")
                    st.write(f"**Coordinates:** {places_df.iloc[i]['latitude']:.6f}, {places_df.iloc[i]['longitude']:.6f}")
                    st.write(f"**Pincode:** {places_df.iloc[i]['pincode']}")
                
                with col2:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_btn_{place_id}", type="primary"):
                        logger.debug("Edit button clicked", place_id=place_id)
                        if on_edit:
                            safe_execute(
                                lambda: on_edit(place_id),
                                f"edit_place_{place_id}",
                                context={"place_id": place_id, "action": "edit"}
                            )
                
                with col3:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_btn_{place_id}", type="secondary"):
                        logger.debug("Delete button clicked", place_id=place_id)
                        if on_delete:
                            safe_execute(
                                lambda: on_delete(place_id),
                                f"delete_place_{place_id}",
                                context={"place_id": place_id, "action": "delete"}
                            )
                
                with col4:
                    # View details button
                    if st.button("👁️ View", key=f"view_btn_{place_id}"):
                        logger.debug("View button clicked", place_id=place_id)
                        if on_view:
                            safe_execute(
                                lambda: on_view(place_id),
                                f"view_place_{place_id}",
                                context={"place_id": place_id, "action": "view"}
                            )


class PlaceForm:
    """Component for place add/edit forms with optimized validation."""
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error rendering form")
    def render_add_place_form(on_submit: Callable[[Dict[str, Any]], bool]) -> None:
        """
        Render the add new place form with optimized validation.
        
        Args:
            on_submit: Callback function when form is submitted
        """
        logger.debug("Rendering add place form")
        
        with st.form("add_place_form", clear_on_submit=False):
            st.markdown("### 📍 Add New Place")
            st.markdown("Fill in all the required information below:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                name = st.text_input(
                    "Place Name *", 
                    placeholder="Enter place name",
                    help="Enter a descriptive name for the place"
                )
                address = st.text_area(
                    "Address *", 
                    placeholder="Enter full address",
                    help="Enter the complete address including street, city, state",
                    height=100
                )
                types = st.text_input(
                    "Types *", 
                    placeholder="e.g., restaurant, hotel, tourist_attraction",
                    help="Enter place types separated by commas"
                )
            
            with col2:
                st.markdown("#### Location Information")
                latitude = st.number_input(
                    "Latitude *", 
                    min_value=-90.0, 
                    max_value=90.0, 
                    value=0.0, 
                    format="%.6f",
                    help="Latitude coordinate between -90 and 90"
                )
                longitude = st.number_input(
                    "Longitude *", 
                    min_value=-180.0, 
                    max_value=180.0, 
                    value=0.0, 
                    format="%.6f",
                    help="Longitude coordinate between -180 and 180"
                )
                pincode = st.text_input(
                    "Pincode *", 
                    placeholder="6-digit pincode", 
                    max_chars=6,
                    help="Enter 6-digit postal code"
                )
            
            # Submit button
            submitted = st.form_submit_button("📍 Add Place", type="primary")
            
            if submitted:
                logger.debug("Add place form submitted", 
                           name=name, types=types, pincode=pincode)
                
                # Prepare form data with optimized validation
                form_data = {
                    'name': name,
                    'address': address,
                    'types': types,
                    'latitude': latitude,
                    'longitude': longitude,
                    'pincode': pincode
                }
                
                # Validate and submit
                if PlaceForm._validate_and_submit_form(form_data, on_submit):
                    st.rerun()
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error rendering edit form")
    def render_edit_place_form(
        place_data: Dict[str, Any], 
        on_submit: Callable[[Dict[str, Any]], bool],
        on_cancel: Callable[[], None]
    ) -> None:
        """
        Render the edit place form with optimized data handling.
        
        Args:
            place_data: Current place data
            on_submit: Callback function when form is submitted
            on_cancel: Callback function when form is cancelled
        """
        logger.debug("Rendering edit place form", place_id=place_data.get('place_id'))
        
        place_id = place_data['place_id']
        
        # Enhanced Edit Place Header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <h2 style='margin: 0; text-align: center;'>✏️ Edit Place</h2>
            <p style='margin: 5px 0 0 0; text-align: center; opacity: 0.9;'>
                Modify place information below
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current place information display
        PlaceForm._render_current_place_info(place_data)
        
        st.markdown("---")
        st.markdown("### ✏️ Edit Form")
        
        with st.form(f"edit_place_form_{place_id}"):
            st.markdown("**Please update the place information:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                edit_name = st.text_input(
                    "Place Name *", 
                    value=place_data['name'], 
                    key=f"edit_name_{place_id}",
                    help="Enter the name of the place"
                )
                edit_address = st.text_area(
                    "Address *", 
                    value=place_data['address'], 
                    key=f"edit_address_{place_id}",
                    help="Enter the full address of the place", 
                    height=100
                )
                edit_types = st.text_input(
                    "Types *", 
                    value=place_data['types'], 
                    key=f"edit_types_{place_id}",
                    help="Enter place types (e.g., restaurant, hotel, tourist_attraction)"
                )
            
            with col2:
                st.markdown("#### Location Information")
                edit_latitude = st.number_input(
                    "Latitude *", 
                    min_value=-90.0, 
                    max_value=90.0,
                    value=float(place_data['latitude']), 
                    format="%.6f",
                    key=f"edit_lat_{place_id}",
                    help="Latitude must be between -90 and 90"
                )
                edit_longitude = st.number_input(
                    "Longitude *", 
                    min_value=-180.0, 
                    max_value=180.0,
                    value=float(place_data['longitude']), 
                    format="%.6f",
                    key=f"edit_lon_{place_id}",
                    help="Longitude must be between -180 and 180"
                )
                edit_pincode = st.text_input(
                    "Pincode *", 
                    value=place_data['pincode'], 
                    max_chars=6,
                    key=f"edit_pincode_{place_id}",
                    help="Enter 6-digit postal code"
                )
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submitted = st.form_submit_button(
                    "💾 Update Place", 
                    type="primary",
                    help="Save the changes to the database"
                )
            
            with col2:
                if st.form_submit_button("❌ Cancel", help="Cancel editing and return to view mode"):
                    logger.debug("Edit form cancelled", place_id=place_id)
                    if on_cancel:
                        safe_execute(on_cancel, f"cancel_edit_{place_id}")
                    st.rerun()
            
            with col3:
                if st.form_submit_button("🔄 Reset", help="Reset all fields to original values"):
                    logger.debug("Edit form reset", place_id=place_id)
                    st.rerun()
            
            if submitted:
                logger.debug("Edit place form submitted", place_id=place_id)
                
                # Prepare form data with optimized validation
                form_data = {
                    'place_id': place_id,
                    'name': edit_name,
                    'address': edit_address,
                    'types': edit_types,
                    'latitude': edit_latitude,
                    'longitude': edit_longitude,
                    'pincode': edit_pincode
                }
                
                # Validate and submit
                if PlaceForm._validate_and_submit_form(form_data, on_submit):
                    st.rerun()
    
    @staticmethod
    def _render_current_place_info(place_data: Dict[str, Any]) -> None:
        """Render current place information display."""
        st.markdown("### 📍 Current Place Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Current Details:**
            - **Name:** {place_data['name']}
            - **Type:** {place_data['types']}
            - **Address:** {place_data['address']}
            """)
        
        with col2:
            created_at = place_data.get('created_at', 'Unknown')
            st.info(f"""
            **Location Details:**
            - **Latitude:** {place_data['latitude']:.6f}
            - **Longitude:** {place_data['longitude']:.6f}
            - **Pincode:** {place_data['pincode']}
            - **Created:** {created_at}
            """)
    
    @staticmethod
    def _validate_and_submit_form(
        form_data: Dict[str, Any], 
        on_submit: Callable[[Dict[str, Any]], bool]
    ) -> bool:
        """
        Validate form data and submit if valid using optimized validation.
        
        Args:
            form_data: Form data to validate
            on_submit: Callback function for submission
            
        Returns:
            bool: True if validation passed and form submitted
        """
        logger.debug("Validating form data", fields=list(form_data.keys()))
        
        # Validate using the validator
        try:
            from utils.validators import PlaceValidator
            validation_result = PlaceValidator.validate_place_data(form_data)
        except ImportError:
            # Fallback basic validation
            validation_result = PlaceForm._basic_validation(form_data)
        
        if not validation_result.is_valid:
            logger.warning("Form validation failed", errors=validation_result.errors)
            st.error("❌ **Validation Errors:**\n" + "\n".join([f"• {error}" for error in validation_result.errors]))
            return False
        
        # Show warnings if any
        if validation_result.warnings:
            logger.info("Form validation warnings", warnings=validation_result.warnings)
            st.warning("⚠️ **Warnings:**\n" + "\n".join([f"• {warning}" for warning in validation_result.warnings]))
        
        # Submit the form
        with st.spinner("🔄 Processing..."):
            success = safe_execute(
                lambda: on_submit(form_data),
                "submit_place_form",
                default_return=False,
                context={"form_data": {k: str(v)[:50] for k, v in form_data.items()}}
            )
            
            if success:
                st.success("✅ Place saved successfully!")
                return True
            else:
                st.error("❌ Failed to save place. Please try again.")
                return False
    
    @staticmethod
    def _basic_validation(form_data: Dict[str, Any]) -> 'ValidationResult':
        """Basic validation fallback when validators module is not available."""
        class BasicValidationResult:
            def __init__(self):
                self.is_valid = True
                self.errors = []
                self.warnings = []
        
        result = BasicValidationResult()
        
        # Check required fields using optimized validation
        required_fields = ['name', 'address', 'types', 'pincode']
        for field in required_fields:
            if not form_data.get(field) or not str(form_data[field]).strip():
                result.errors.append(f"{field.title()} is required")
                result.is_valid = False
        
        return result


# Export all UI components
__all__ = [
    'TableControls',
    'DataTable', 
    'PlaceForm'
]
