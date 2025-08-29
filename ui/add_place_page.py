"""
Add Place Page Module

This module contains the functionality for the Add New Place page,
including the place form and the Nearby Search API testing section.
"""

import streamlit as st
import json
from typing import Callable, Dict, Any
from utils.logger import get_logger
from ui.components import PlaceForm
from api_testing.ola_maps_api_tester import OLAMapsAPITester
import pandas as pd
logger = get_logger(__name__)


class AddPlacePage:
    """Handles the Add New Place page functionality."""
    
    def __init__(self):
        """Initialize the Add Place Page."""
        self.logger = get_logger(self.__class__.__name__)
    
    def render(self, on_submit: Callable[[Dict[str, Any]], bool]):
        """
        Render the complete Add New Place page.
        
        Args:
            on_submit: Callback function for form submission
        """
        self.logger.debug("Rendering add place page")
        
        # Render the main header
        st.header("➕ Add New Place")
        
        # Render the place form
        PlaceForm.render_add_place_form(on_submit=on_submit)
        
        # Render the API testing section
        self._render_api_testing_section()
    def load_csv(self, file_path, column_name):
        """Load the CSV file."""
        df = pd.read_csv(file_path)
        return df.drop_duplicates(subset=[column_name])[column_name].tolist()
    
    def _render_api_testing_section(self):
        """Render the API testing section for Nearby Search."""
        st.markdown("---")
        st.header("🔍 API Testing - Nearby Search")
        st.markdown("Test the OLA Maps Places API Nearby Search endpoint with dynamic parameters.")
        pincodes = self.load_csv("utils/pincodes.csv", "pincode")
        # Initialize API tester
        try:
            api_tester = OLAMapsAPITester()
            
            # Load Places API collection
            api_tester.load_collection("Places API.postman_collection.json")
            
            if api_tester.endpoints:
                # Get the Nearby Search endpoint
                nearby_endpoint = api_tester.get_endpoint_by_name("4) Nearby Search - GET")
                if nearby_endpoint:
                    # self._render_endpoint_configuration(api_tester, nearby_endpoint)
                    # self._render_parameter_configuration(api_tester)
                    self._render_test_execution(api_tester, nearby_endpoint,pincodes)
                    # self._render_url_structure(api_tester)
                else:
                    st.error("❌ Nearby Search endpoint not found in the Places API collection")
            else:
                st.error("❌ Failed to load Places API collection")
                
        except Exception as e:
            st.error(f"❌ Error initializing API tester: {str(e)}")
            self.logger.error("Error in API testing section", error=str(e))
    
    def _render_endpoint_configuration(self, api_tester: OLAMapsAPITester, nearby_endpoint):
        """Render the endpoint configuration section."""
        st.markdown("### 📍 Nearby Search API Configuration")
        
        # Display endpoint details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            **Endpoint Details:**
            - **Method:** {nearby_endpoint.method}
            - **Category:** {nearby_endpoint.category}
            - **Description:** {nearby_endpoint.description}
            """)
        
        with col2:
            st.markdown(f"""
            **Base URL:** `{api_tester.base_url}`
            **API Key:** `{api_tester.api_key[:10]}...`
            """)
    
    def _render_parameter_configuration(self, api_tester: OLAMapsAPITester):
        """Render the dynamic parameters configuration section."""
        st.markdown("### ⚙️ Dynamic Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            location = st.text_input(
                "Location (lat,lng)",
                value="12.931544865377818,77.61638622280486",
                help="Enter latitude and longitude separated by comma"
            )
            
            types = st.text_input(
                "Types",
                value="restaurant",
                help="Enter place types (e.g., restaurant, hotel, tourist_attraction)"
            )
        
        with col2:
            radius = st.number_input(
                "Radius (meters)",
                min_value=100,
                max_value=50000,
                value=10000,
                step=100,
                help="Search radius in meters"
            )
            
            rank_by = st.selectbox(
                "Rank By",
                options=["popular", "distance", "rating"],
                index=0,
                help="How to rank the results"
            )
        
        with col3:
            # Show current API configuration
            st.markdown("**Current Configuration:**")
            st.json({
                "location": location,
                "types": types,
                "radius": radius,
                "rank_by": rank_by,
                "api_key": f"{api_tester.api_key[:10]}...",
                "bearer_token": f"{api_tester.bearer_token[:20]}..."
            })
        
        # Store parameters in session state for use in test execution
        st.session_state.api_params = {
            "location": location,
            "types": types,
            "radius": radius,
            "rank_by": rank_by
        }
    
    def _render_test_execution(self, api_tester: OLAMapsAPITester, nearby_endpoint,pincodes:list[str]):
        """Render the test execution section."""
        # Test button
        if st.button("🚀 Test Nearby Search API", type="primary"):
            with st.spinner("Testing Nearby Search API..."):
                try:
                    # Get parameters from session state
                    params = st.session_state.get("api_params", {})
                    logger.info(f"Pincodes: {pincodes}")
                    # Prepare custom parameters
                    custom_params = {
                        "location": params.get("location", "12.931544865377818,77.61638622280486"),
                        "types": params.get("types", "restaurant"),
                        "radius": str(params.get("radius", 10000)),
                        "rankBy": params.get("rank_by", "popular")
                    }
                    if not nearby_endpoint.url.startswith("https://"):
                        nearby_endpoint.url = f"https://{nearby_endpoint.url}"
                    # logger.info(f"Nearby endpoint: {nearby_endpoint.url}")
                    # Test the endpoint
                    result = api_tester.test_endpoint(nearby_endpoint, custom_params)
                    # logger.info(f"Result: {result}")
                    # Display results
                    self._render_test_results(nearby_endpoint, result)
                    
                except Exception as e:
                    st.error(f"Error testing API: {str(e)}")
                    self.logger.error("Error testing Nearby Search API", error=str(e))
    
    def _render_test_results(self, nearby_endpoint, result):
        """Render the test results section."""
        st.markdown("### 📊 API Test Results")
        
        # col1, col2 = st.columns(2)
        
        # with col1:
        #     st.markdown("**Request Details:**")
        #     st.json({
        #         "method": nearby_endpoint.method,
        #         "url": result.get("url", "N/A"),
        #         "status_code": result.get("status_code", "N/A"),
        #         "response_time_ms": result.get("response_time", "N/A")
        #     })
        
        # with col2:
        #     st.markdown("**Response Status:**")
        #     if result.get("success", False):
        #         st.success("✅ API call successful!")
        #     else:
        #         st.error("❌ API call failed!")
            
        #     st.markdown(f"**Response Time:** {result.get('response_time', 'N/A')} ms")
        
        # Display response data
        st.markdown("### 📄 Response Data")
        
        response_data = result.get("response", {})
        
        if response_data:
            # Try to parse and display the response nicely
            try:
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                
                # # Display as JSON
                # st.json(response_data)
                for prediction in response_data["predictions"]:
                    place_data = self.place_details(prediction["place_id"])
                    st.markdown(f"**{prediction['place_id']}**")
                    st.markdown(f"**{prediction['description']}**")
                    st.markdown(f"**{prediction['types']}**")
                # If it's a successful response with places, show a summary
                if isinstance(response_data, dict):
                    places = response_data.get("results", [])
                    if places:
                        st.markdown(f"**Found {len(places)} places:**")
                        
                        # Create a simple table of results
                        places_summary = []
                        for place in places[:10]:  # Show first 10
                            places_summary.append({
                                "Name": place.get("name", "N/A"),
                                "Types": ", ".join(place.get("types", [])),
                                "Rating": place.get("rating", "N/A"),
                                "Address": place.get("vicinity", "N/A")
                            })
                        
                        if places_summary:
                            st.dataframe(places_summary, use_container_width=True)
                        
                        if len(places) > 10:
                            st.info(f"... and {len(places) - 10} more places")
                    
                    # Show error if any
                    error_message = response_data.get("error_message")
                    if error_message:
                        st.error(f"API Error: {error_message}")
                
            except json.JSONDecodeError:
                st.text(response_data)
        else:
            st.warning("No response data received")
    
    def _render_url_structure(self, api_tester: OLAMapsAPITester):
        """Render the endpoint URL structure section."""
        st.markdown("### 🔗 Endpoint URL Structure")
        
        # Get parameters from session state
        params = st.session_state.get("api_params", {})
        location = params.get("location", "12.931544865377818,77.61638622280486")
        types = params.get("types", "restaurant")
        radius = params.get("radius", 10000)
        rank_by = params.get("rank_by", "popular")
        
        st.code(f"""
GET {api_tester.base_url}/places/v1/nearbysearch
?location={location}
&types={types}
&radius={radius}
&rankBy={rank_by}
&api_key={api_tester.api_key[:10]}...
        """.strip())


def render_add_place_page(place_ops):
    """
    Render the Add New Place page.
    
    Args:
        place_ops: PlaceOperations instance for handling place operations
    """
    # Create and render the add place page
    add_place_page = AddPlacePage()
    add_place_page.render(on_submit=place_ops.handle_add_place)
