"""
Add Place Page Module

This module contains the functionality for the Add New Place page,
including the place form and the Nearby Search API testing section.
"""

import random
import streamlit as st
import json
import requests
import time
from typing import Callable, Dict, Any
from utils.settings import get_default_types
from utils.logger import get_logger
from ui.components import PlaceForm
from api_testing.ola_maps_api_tester import OLAMapsAPITester
import pandas as pd
from models.place import Place
from utils.database import PlacesDatabase
logger = get_logger(__name__)

Placesdb = PlacesDatabase()

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
        self.test_bearer_token_demo()
        self._render_api_testing_section()
        
        # Render the place details demo section
        # self.test_place_details_demo()
        
        # Render the bearer token demo section
    
    def get_bearer_token(self) -> Dict[str, Any]:
        """
        Get a new bearer token using the Generate Access Token API.
        
        Returns:
            Dictionary containing the bearer token or error information
        """
        try:
            # API endpoint details from the Postman collection
            url = "https://account.olamaps.io/realms/olamaps/protocol/openid-connect/token"
            
            # Form data parameters from the Postman collection
            form_data = {
                "grant_type": "client_credentials",
                "scope": "openid",
                "client_id": "d4cd55fa-a8d7-4287-b65e-507dc45727b1",
                "client_secret": "bQzMgcE1XCdd1kh8LWQwBFdzRg6hs4UD"
            }
            
            # Headers for form data
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            self.logger.info("Requesting new bearer token from OLA Maps authentication service")
            
            # Make the POST request
            start_time = time.time()
            response = requests.post(
                url=url,
                data=form_data,
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            
            # Prepare result
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": round((end_time - start_time) * 1000, 2),  # ms
                "url": response.url,
                "bearer_token": None,
                "error": None
            }
            
            # Parse response
            try:
                if response.status_code == 200:
                    response_data = response.json()
                    if "access_token" in response_data:
                        result["bearer_token"] = response_data["access_token"]
                        result["token_type"] = response_data.get("token_type", "Bearer")
                        result["expires_in"] = response_data.get("expires_in")
                        result["scope"] = response_data.get("scope")
                        
                        self.logger.info(f"Successfully obtained bearer token. Expires in: {result['expires_in']} seconds")
                    else:
                        result["success"] = False
                        result["error"] = "No access_token in response"
                        self.logger.error("No access_token found in response")
                else:
                    result["error"] = f"HTTP {response.status_code}: {response.reason}"
                    self.logger.error(f"Failed to get bearer token: {result['error']}")
                    
            except json.JSONDecodeError as e:
                result["success"] = False
                result["error"] = f"Invalid JSON response: {str(e)}"
                self.logger.error(f"Invalid JSON response: {str(e)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Exception in get_bearer_token: {str(e)}")
            return {
                "success": False,
                "status_code": None,
                "response_time": None,
                "url": url,
                "bearer_token": None,
                "error": f"Exception occurred: {str(e)}"
            }
    
    def place_details(self, id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place using the Place Details API.
        
        Args:
            id: The place ID to get details for
            
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
            
            # Prepare custom parameters with the id
            custom_params = {
                "place_id": id
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
        # Read CSV with low_memory=False to avoid DtypeWarning for mixed types
        df = pd.read_csv(file_path, low_memory=False).copy()
        
        # Convert latitude and longitude columns to numeric types
        # Handle any conversion errors by coercing to numeric and dropping rows with invalid data
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Drop rows where latitude or longitude is NaN (invalid coordinates)
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])
        
        return df
    
    def _render_api_testing_section(self):
        """Render the API testing section for Nearby Search."""
        st.markdown("---")
        st.header("🔍 API Testing - Nearby Search")
        st.markdown("Test the OLA Maps Places API Nearby Search endpoint with dynamic parameters.")
        # Initialize API tester
        try:
            api_tester = OLAMapsAPITester()
            
            # Load Places API collection
            api_tester.load_collection("Places API.postman_collection.json")
            
            if api_tester.endpoints:
                # Get the Nearby Search endpoint
                nearby_endpoint = api_tester.get_endpoint_by_name("4) Nearby Search - GET")
                latlongs = self.load_location_csv("utils/pincodes.csv")
                if nearby_endpoint:
                    # latlongs['done'] = 0
                    # for i in get_default_types():
                    #     latlongs.drop(columns=i, axis=1, inplace=True)
                    # latlongs.to_csv("utils/pincodes_final.csv", index=False)
                    if st.button("🚀 Test Nearby Search API", type="primary"):
                        with st.spinner("Testing Nearby Search API..."):
                            try:
                                self._render_test_results(latlongs,nearby_endpoint,api_tester)
                            except Exception as e:
                                st.error(f"Error testing API: {str(e)}")
                                self.logger.error("Error testing Nearby Search API", error=str(e))
                else:
                    st.error("❌ Nearby Search endpoint not found in the Places API collection")
            else:
                st.error("❌ Failed to load Places API collection")
                
        except Exception as e:
            st.error(f"❌ Error initializing API tester: {str(e)}")
            self.logger.error("Error in API testing section", error=str(e))
    
    # def _render_test_execution(self, api_tester: OLAMapsAPITester, nearby_endpoint,latlongs:pd.DataFrame):
    #     """Render the test execution section."""
    #     # Test button

    #     # st.button("Rerun")
    
    def _render_test_results(self,latlongs:pd.DataFrame,nearby_endpoint,api_tester: OLAMapsAPITester):
        """Render the test results section."""
        types_list = get_default_types()
        if not nearby_endpoint.url.startswith("https://"):
            nearby_endpoint.url = f"https://{nearby_endpoint.url}"
        total_latlongs = len(latlongs.values.tolist())
        total_types = len(types_list)
        latlong_progress_bar = st.progress(0)
        latlong_progress_text = st.empty()
        types_progress_bar = st.progress(0)
        types_progress_text = st.empty()
        
        for latlong_idx, latlong in latlongs.iterrows():
            # Update Progress Bar 1: Location progress
            latlong_progress_percentage = (latlong_idx + 1) / total_latlongs
            latlong_progress_bar.progress(latlong_progress_percentage)
            latlong_progress_text.text(f"📍 Processing location {latlong_idx + 1}/{total_latlongs} in {latlong['latitude']},{latlong['longitude']}")
            if latlongs.loc[latlong_idx,"done"] == 1:
                break
            for type_idx, types in enumerate(types_list):
                # Update Progress Bar 2: Types progress
                types_progress_percentage = (type_idx + 1) / total_types
                types_progress_bar.progress(types_progress_percentage)
                types_progress_text.text(f"🔍 Processing type {type_idx + 1}/{total_types}: {types} in {latlongs.loc[latlong_idx,'latitude']},{latlongs.loc[latlong_idx,'longitude']}")
                custom_params = {
                    "location": f"{latlongs.loc[latlong_idx,'latitude']},{latlongs.loc[latlong_idx,'longitude']}",
                    "types": types,
                    "radius": str(100000),
                    "rankBy": "popular",
                    "limit": "100"
                }
                result = api_tester.test_endpoint(nearby_endpoint, custom_params)    
                response_data = result["response"]
                if response_data:
                    # Try to parse and display the response nicely
                    try:
                        if isinstance(response_data, str):
                            response_data = json.loads(response_data)
                        if "predictions" in response_data:
                            self.predictions_json(response_data["predictions"],latlongs.loc[latlong_idx],types)
                        elif "message" in response_data:
                            st.warning("Authentication error detected. Attempting to refresh bearer token...")
                            token_result = self.get_bearer_token()
                            if token_result.get("success"):
                                new_token = token_result["bearer_token"]
                                api_tester.change_bearer_token(new_token)
                                st.success(f"✅ Bearer token refreshed successfully! Expires in: {token_result.get('expires_in', 'N/A')} seconds")
                                st.info("🔄 Retrying API call with new token...")
                                retry_result = api_tester.test_endpoint(nearby_endpoint, custom_params)
                                if retry_result.get("success"):
                                    st.success("✅ API call successful with new token!")
                                    retry_response = retry_result["response"]
                                    if isinstance(retry_response, str):
                                        retry_response = json.loads(retry_response)
                                    if "predictions" in retry_response:
                                        self.predictions_json(retry_response["predictions"],latlongs.loc[latlong_idx],types)
                                    elif "error_message" in retry_response:
                                        st.error(f"API Error: {retry_response["error_message"]}")
                                else:
                                    st.error(f"❌ Retry failed: {retry_result.get('error', 'Unknown error')}")
                            else:
                                st.error(f"❌ Failed to refresh bearer token: {token_result.get('error', 'Unknown error')}")
                                st.json(token_result)
                        elif response_data["error_message"] != "":
                            st.error(f"API Error: {response_data["error_message"]}")
                    except json.JSONDecodeError:
                        st.text(response_data)
                else:
                    st.warning("No response data received")
        latlongs.loc[latlong_idx,"done"] = 1
        latlongs.to_csv("utils/pincodes.csv", index=False)
        latlong_progress_bar.progress(1.0)
        types_progress_bar.progress(1.0)
        latlong_progress_text.text("✅ All locations processed!")
        types_progress_text.text("✅ All place types processed!")
        latlong_progress_text.empty()
        types_progress_text.empty()
        latlong_progress_bar.empty()
        types_progress_bar.empty()
        # Show completion message
        total_iterations = total_latlongs * total_types
        st.success(f"🎉 Successfully processed {total_iterations} API calls across {total_latlongs} locations and {total_types} place types!")

    def predictions_json(self,predictions,latlong,types,ui:bool=False):
        """Render the prediction JSON section."""
        if ui:
            st.markdown(f"**Found {len(predictions)} predictions:**")
        for prediction in predictions:
                existing_place = Placesdb.get_place_by_id(prediction["place_id"])
                if existing_place is not None:
                    logger.info(f"Place already exists with ID: {prediction["place_id"]}")
                    break
                place_data = self.place_details(prediction["place_id"])
                result = place_data["data"]["result"]
                if place_data.get("success") and place_data.get("data"):
                    location = result["geometry"]["location"]
                    if  types not in prediction.get('types', []):
                        prediction['types'].append(types)
                    reviews = 0
                    for i in result.get('reviews', []):
                        reviews += i.get('rating', 0)
                    place_detail = Place(
                        id= prediction['place_id'],
                        pincode= str(latlong["pincode"]),
                        name= result.get('name', ''),
                        address= result.get('formatted_address', ''),
                        latitude= location.get('lat', 0.0),
                        longitude= location.get('lng', 0.0),
                        description= prediction.get('description', ''),
                        types= ', '.join(prediction.get('types', [])),
                        rating= result.get('rating', 0),
                        followers= reviews,
                        country='India'
                    )
                    for component in result["address_components"]:
                        if "postal_code" in component:
                            place_detail.postal_code = str(component['postal_code'])
                        if "country" in component:
                            place_detail.country = component['country']
                    # logger.info(f"Place detail: {place_detail}")
                    result = self.add_place_details(place_detail)
                    if result == 1:
                        with st.expander(f"📍 {prediction["place_id"]}", expanded=False):
                            st.json(place_detail.to_dict())
                            st.success("🎉 Place details added successfully!")
                    elif result == 2:
                            st.error("❌ Failed to add place details")
                else:
                    st.warning("No detailed information available")
    def add_place_details(self, place_detail: Place) -> int:
        """Add the place details to the database in table 'places'. It will also sync to excel.
        
        Args:
            place_detail: Place detail dictionary or Place model instance
            
        Returns:
            int: 0,1,2
            0: Place already exists
            1: Place added successfully
            2: Failed to add place
        
        """
        try:
            # Import database operations
            
            # Initialize database
            
            # Convert to Place model if it's a dictionary
            if isinstance(place_detail, Place):
                place = place_detail
            else:
                self.logger.error(f"Invalid place_detail type: {type(place_detail)}")
                return 2
            
            
            # Add place using the model-based method
            # logger.info(f"Adding place: {place}")
            success = Placesdb.add_place_with_model(place)
            
            if success:
                # self.logger.info(f"Place added successfully: {place.name}")
                return 1
            else:
                self.logger.error(f"Failed to add place: {place.name}")
                return 2
                
        except Exception as e:
            self.logger.error(f"Error adding place details: {str(e)}")
            return 2
    def test_bearer_token_demo(self):
        """Demonstrate the get_bearer_token function."""
        st.markdown("---")
        st.header("🔑 Bearer Token Generation Demo")
        st.markdown("Test the Generate Access Token API to get a new bearer token.")
        if st.button("🔑 Generate New Bearer Token", type="primary"):
            with st.spinner("Generating new bearer token..."):
                result = self.get_bearer_token()
                if result.get("success"):
                    st.success("✅ Bearer token generated successfully!")
                    # Display token details
                    st.markdown("### 🔑 Token Information")
                    st.code(result.get("bearer_token", ""), language="python")
                else:
                    st.error(f"❌ Failed to generate bearer token: {result.get('error', 'Unknown error')}")
                    st.markdown(f"**Status Code:** {result.get('status_code', '')}")
                    st.markdown(f"**Response Time:** {result.get('response_time', '')} ms")
                    with st.expander("📄 Error Details"):
                        st.json(result)

def render_add_place_page(place_ops):
    """
    Render the Add New Place page.
    
    Args:
        place_ops: PlaceOperations instance for handling place operations
    """
    # Create and render the add place page
    add_place_page = AddPlacePage()
    add_place_page.render(on_submit=place_ops.handle_add_place)
