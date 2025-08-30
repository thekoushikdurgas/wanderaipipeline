"""
Add Place Page Module

This module contains the functionality for the Add New Place page,
including the place form and the Nearby Search API testing section.
"""

import random
import streamlit as st
import json
from typing import Callable, Dict, Any
from config.settings import get_default_types
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
        
        # Render the place details demo section
        # self.test_place_details_demo()
    
    def place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place using the Place Details API.
        
        Args:
            place_id: The place ID to get details for
            
        Returns:
            Dictionary containing the place details or error information
        """
        try:
            # Initialize API tester
            api_tester = OLAMapsAPITester()
            
            # Load Places API collection
            api_tester.load_collection("Places API.postman_collection.json")
            
            if not api_tester.endpoints:
                return {"error": "Failed to load Places API collection"}
            
            # Get the Place Details endpoint
            place_details_endpoint = api_tester.get_endpoint_by_name("2) Place Details - GET")
            
            if not place_details_endpoint:
                return {"error": "Place Details endpoint not found in the Places API collection"}
            
            # Prepare custom parameters with the place_id
            custom_params = {
                "place_id": place_id
            }
            
            # Ensure URL has proper protocol
            if not place_details_endpoint.url.startswith("https://"):
                place_details_endpoint.url = f"https://{place_details_endpoint.url}"
            
            # Test the endpoint
            result = api_tester.test_endpoint(place_details_endpoint, custom_params)
            
            # Return the result
            if result.get("success", False):
                return {
                    "success": True,
                    "data": result.get("response", {}),
                    "status_code": result.get("status_code"),
                    "response_time": result.get("response_time")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error occurred"),
                    "status_code": result.get("status_code"),
                    "response_time": result.get("response_time")
                }
                
        except Exception as e:
            self.logger.error(f"Error in place_details: {str(e)}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }

    def load_location_csv(self, file_path):
        """Load the CSV file."""
        df = pd.read_csv(file_path)
        # 28.6174167,77.2129167
        # return df.drop_duplicates(subset=[column_name])[column_name].tolist()
        return df
    
    def _render_api_testing_section(self):
        """Render the API testing section for Nearby Search."""
        st.markdown("---")
        st.header("🔍 API Testing - Nearby Search")
        st.markdown("Test the OLA Maps Places API Nearby Search endpoint with dynamic parameters.")
        latlongs = self.load_location_csv("utils/pincodes.csv")
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
                    self._render_test_execution(api_tester, nearby_endpoint,latlongs)
                    # self._render_url_structure(api_tester)
                else:
                    st.error("❌ Nearby Search endpoint not found in the Places API collection")
            else:
                st.error("❌ Failed to load Places API collection")
                
        except Exception as e:
            st.error(f"❌ Error initializing API tester: {str(e)}")
            self.logger.error("Error in API testing section", error=str(e))
    
    def _render_test_execution(self, api_tester: OLAMapsAPITester, nearby_endpoint,latlongs:pd.DataFrame):
        """Render the test execution section."""
        # Test button
        if st.button("🚀 Test Nearby Search API", type="primary"):
            with st.spinner("Testing Nearby Search API..."):
                try:
                    # Get parameters from session state
                    params = st.session_state.get("api_params", {})
                    # logger.info(f"Latlongs: {latlongs}")
                    # Prepare custom parameters
                    # logger.info(f"Response data: {latlongs.values.tolist()}")
                    latlong = random.choice(latlongs.values.tolist())
                    # logger.info(f"Response data: {latlong}")
                    types_list = get_default_types()
                    # for latlong in latlongs.values.tolist()[:10]:
                    for types in types_list:
                            custom_params = {
                                "location": f"{latlong[-2]},{latlong[-1]}",
                                "types": types,
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
                            self._render_test_results(result,latlong)
                    
                except Exception as e:
                    st.error(f"Error testing API: {str(e)}")
                    self.logger.error("Error testing Nearby Search API", error=str(e))
    
    def _render_test_results(self, result,latlong):
        """Render the test results section."""
        st.markdown("### 📊 API Test Results")        
        response_data = result.get("response", {})
        # logger.info(f"Response data: {latlong}")
        if response_data:
            # Try to parse and display the response nicely
            try:
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                st.json(response_data)
                # # Display predictions with place details
                # if "predictions" in response_data:
                #     # st.markdown("### 🏢 Place Predictions with Details")
                #     for prediction in response_data["predictions"]:  # Show first 5 predictions
                #         with st.expander(f"📍 {prediction.get('description', 'Unknown Place')}", expanded=False):
                #             # Get detailed place information
                #             logger.info(f"Place ID: {prediction["place_id"]}")
                #             place_data = self.place_details(prediction["place_id"])
                #             if place_data.get("success") and place_data.get("data"):
                #                 location = place_data["data"]["result"]["geometry"]["location"]
                #                 # logger.info(f"Location: {location}")
                #                 place_detail = {
                #                     "pincode": latlong[-3],
                #                     "place_id": prediction['place_id']	,
                #                     "name": place_data["data"]["result"].get('name', 'N/A'),
                #                     "address": place_data["data"]["result"].get('formatted_address', 'N/A'),
                #                     "latitude": location.get('lat', 'N/A'),
                #                     "longitude": location.get('lng', 'N/A'),
                #                     "description": prediction.get('description', 'N/A'),
                #                     "types": ', '.join(prediction.get('types', [])),
                #                 }
                #                 for component in place_data["data"]["result"]["address_components"]:
                #                     if "postal_code" in component:
                #                         place_detail["postal_code"] = component['postal_code']
                #                         break
                #                 st.json(place_detail)
                #             else:
                #                 st.warning("No detailed information available")
                            
                            # col1, col2 = st.columns([1, 2])
                            
                            # with col1:
                            #     # if place_data.get("success"):
                            #     #     st.success("✅ Place details retrieved successfully")
                            #     # else:
                            #     #     st.error(f"❌ Failed to get place details: {place_data.get('error', 'Unknown error')}")
                            
                            # with col2:
                            #     st.markdown("**Detailed Information:**")
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
    
    # def test_place_details_demo(self):
    #     """Demonstrate the place_details function with a sample place_id."""
    #     st.markdown("---")
    #     st.header("🧪 Place Details API Demo")
    #     st.markdown("Test the Place Details API with a sample place ID.")
        
    #     # Sample place ID from the Postman collection
    #     sample_place_id = "ola-platform:a79ed32419962a11a588ea92b83ca78e"
        
    #     col1, col2 = st.columns([2, 1])
        
    #     with col1:
    #         place_id = st.text_input(
    #             "Place ID",
    #             value=sample_place_id,
    #             help="Enter a place ID to get detailed information"
    #         )
        
    #     with col2:
    #         if st.button("🔍 Get Place Details", type="primary"):
    #             with st.spinner("Fetching place details..."):
    #                 result = self.place_details(place_id)
                    
    #                 if result.get("success"):
    #                     st.success("✅ Place details retrieved successfully!")
                        
    #                     # Display the results
    #                     detail_data = result.get("data", {})
    #                     if "result" in detail_data:
    #                         place_info = detail_data["result"]
                            
    #                         st.markdown("### 📍 Place Information")
    #                         st.markdown(f"**Name:** {place_info.get('name', 'N/A')}")
    #                         st.markdown(f"**Address:** {place_info.get('formatted_address', 'N/A')}")
    #                         st.markdown(f"**Phone:** {place_info.get('formatted_phone_number', 'N/A')}")
    #                         st.markdown(f"**Website:** {place_info.get('website', 'N/A')}")
    #                         st.markdown(f"**Rating:** {place_info.get('rating', 'N/A')}")
    #                         st.markdown(f"**Price Level:** {place_info.get('price_level', 'N/A')}")
                            
    #                         # Show geometry
    #                         if "geometry" in place_info and "location" in place_info["geometry"]:
    #                             location = place_info["geometry"]["location"]
    #                             st.markdown(f"**Coordinates:** {location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}")
                            
    #                         # Show opening hours
    #                         if "opening_hours" in place_info:
    #                             opening_hours = place_info["opening_hours"]
    #                             st.markdown(f"**Open Now:** {opening_hours.get('open_now', 'N/A')}")
    #                             if opening_hours.get('weekday_text'):
    #                                 st.markdown("**Opening Hours:**")
    #                                 for day in opening_hours["weekday_text"]:
    #                                     st.markdown(f"- {day}")
                        
    #                     st.markdown(f"**Response Time:** {result.get('response_time', 'N/A')} ms")
                        
    #                     # Show raw response in expandable section
    #                     with st.expander("📄 Raw API Response"):
    #                         st.json(detail_data)
    #                 else:
    #                     st.error(f"❌ Failed to get place details: {result.get('error', 'Unknown error')}")


def render_add_place_page(place_ops):
    """
    Render the Add New Place page.
    
    Args:
        place_ops: PlaceOperations instance for handling place operations
    """
    # Create and render the add place page
    add_place_page = AddPlacePage()
    add_place_page.render(on_submit=place_ops.handle_add_place)
