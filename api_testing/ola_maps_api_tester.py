"""
OLA Maps API Testing Module

This module provides functionality to test all OLA Maps API endpoints
from the Postman collections with a user-friendly interface.
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import os
from urllib.parse import urlparse

import re
from utils import logger


@dataclass
class APIEndpoint:
    """Represents an API endpoint configuration."""
    name: str
    method: str
    url: str
    description: str
    category: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body_params: Optional[Dict[str, Any]] = None
    required_params: Optional[List[str]] = None


class PostmanCollectionLoader:
    """Loads and parses Postman collection JSON files."""
    
    def __init__(self, collections_dir: str = "OLAMAPSapi"):
        self.collections_dir = Path(collections_dir)
        self.base_url = "https://api.olamaps.io"
        self.variables: Dict[str, Any] = {}
    
    def get_available_collections(self) -> List[str]:
        """Get list of available Postman collection files."""
        if not self.collections_dir.exists():
            return []
        
        collection_files = []
        for file_path in self.collections_dir.glob("*.postman_collection.json"):
            collection_files.append(file_path.name)
        
        return sorted(collection_files)
    
    def load_collection_from_file(self, filename: str) -> Dict[str, List[APIEndpoint]]:
        """Load API endpoints from a Postman collection JSON file."""
        file_path = self.collections_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Collection file not found: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            return self._parse_postman_collection(collection_data, filename)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in collection file {filename}: {e}")
        except Exception as e:
            raise Exception(f"Error loading collection {filename}: {e}")
    
    def _parse_postman_collection(self, collection_data: dict, filename: str) -> Dict[str, List[APIEndpoint]]:
        """Parse Postman collection data into APIEndpoint objects."""
        endpoints = {}
        
        # Extract collection info
        collection_name = collection_data.get('info', {}).get('name', filename.replace('.postman_collection.json', ''))
        
        # Extract variables for substitution
        # variables = {}
        for var in collection_data.get('variable', []):
            self.variables[var.get('key', '')] = var.get('value', '')
        
        # Process items (endpoints) - handle nested structure recursively
        items = collection_data.get('item', [])
        
        for item in items:
            # Recursively process items to handle nested folders
            self._process_postman_item_recursive(item, collection_name, endpoints)
        
        return endpoints
    
    def _process_postman_item_recursive(self, item: dict, collection_name: str, endpoints: Dict[str, List[APIEndpoint]], parent_category: str = None):
        """Recursively process Postman items to handle nested folders and endpoints."""
        item_name = item.get('name', 'Unnamed Item')
        if 'variable' in item:
            for var in item.get('variable', []):
                self.variables[var.get('key', '')] = var.get('value', '')
        # Check if this item has sub-items (it's a folder)
        if 'item' in item and isinstance(item['item'], list):
            # This is a folder, process its sub-items
            if parent_category:
                sub_category = f"{parent_category} - {item_name}"
            else:
                sub_category = f"{self._extract_category_from_name(collection_name)} - {item_name}"
            
            for sub_item in item['item']:
                self._process_postman_item_recursive(sub_item, collection_name, endpoints, sub_category)
        
        # Check if this item has a request (it's an endpoint)
        elif 'request' in item:
            endpoint = self._parse_postman_item(item, collection_name, parent_category)
            if endpoint:
                category = endpoint.category
                if category not in endpoints:
                    endpoints[category] = []
                endpoints[category].append(endpoint)
    
    def _parse_postman_item(self, item: dict, collection_name: str, variables: dict, parent_category: str = None) -> Optional[APIEndpoint]:
        """Parse a single Postman item into an APIEndpoint."""
        if 'request' not in item:
            return None
        # logger.info(f"Parsing item: {item}")
        request = item['request']
        name = item.get('name', 'Unnamed Endpoint')
        description = item.get('description', '') or request.get('description', '')
        
        # Parse URL
        url_data = request["url"]["raw"]
        url = url_data
        url = self._substitute_variables(url)
        # Parse method
        method = request.get('method', 'GET').upper()
        
        # Parse headers
        headers = {}
        for header in request.get('header', []):
            if not header.get('disabled', False):
                key = header.get('key', '')
                value = header.get('value', '')
                if key and value:
                    headers[key] = value
        
        # Parse query parameters
        query_params = {}
        for param in request.get('query', []):
            key = param.get('key', '')
            value = param.get('value', '')
            if key and value:
                query_params[key] = value
        
        # Parse body parameters
        body_params = None
        if method in ['POST', 'PUT', 'PATCH']:
            body = request.get('body', {})
            if body.get('mode') == 'raw':
                try:
                    body_params = json.loads(body.get('raw', '{}'))
                except json.JSONDecodeError:
                    body_params = {'raw_data': body.get('raw', '')}
        
        # Extract required parameters from URL path
        required_params = []
        if '{' in url:
            required_params = re.findall(r'\{([^}]+)\}', url)
        
        # Determine category from collection name and parent category
        if parent_category:
            category = parent_category
        else:
            category = self._extract_category_from_name(collection_name)
        
        return APIEndpoint(
            name=name,
            method=method,
            url=url,
            description=description,
            category=category,
            headers=headers,
            query_params=query_params,
            body_params=body_params,
            required_params=required_params
        )
    
    def _substitute_variables(self, value: str, variables: dict = None) -> str:
        """Substitute Postman variables in a string."""
        if not isinstance(value, str):
            return value
        if not variables:
            variables = self.variables
        for var_key, var_value in variables.items():
            placeholder = f"{{{{{var_key}}}}}"
            if placeholder in value:
                value = value.replace(placeholder, str(var_value))
        
        # Handle common Postman variables that might not be in the collection variables
        common_vars = {
            "{{baseUrl}}": "https://api.olamaps.io",
            "{{protocol}}": "https",
            "{{uuid}}": "test-uuid-123",
            "{{$timestamp}}": "1234567890",
            "{{$randomInt}}": "42"
        }
        
        for placeholder, default_value in common_vars.items():
            if placeholder in value:
                value = value.replace(placeholder, default_value)
        
        return value
    
    def _extract_category_from_name(self, collection_name: str) -> str:
        """Extract category name from collection filename."""
        # Remove common suffixes and clean up
        name = collection_name.replace(' API', '').replace(' APIs', '').replace(' Copy', '')
        return name


class OLAMapsAPITester:
    """Main class for testing OLA Maps API endpoints."""
    
    def __init__(self):
        self.base_url = "https://api.olamaps.io"
        # Use environment variables if available, otherwise use defaults
        import os
        self.api_key = os.getenv("OLA_MAPS_API_KEY", "SxJhsrEpqjBqIdicTM7OsQcaFSRC0KRoq43BiRQf")
        self.bearer_token = os.getenv("OLA_MAPS_BEARER_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0eXAiOiJDbGllbnQiLCJqdGkiOiJyN0p2QThLSExSOGJuSnN0ODN5Y1VkIiwic3ViIjoic2g3ZHVCN2hZSERQUEN1MVp2TnZCZyIsImFjYyI6InA5eXp5dEJHczR2aHZUVEhUbnNtYTkiLCJleHAiOjE3NTY1ODg3OTl9.J_6ajBCWlrTLbYoyvefL_aJGrEgBCuD8yFT4CJC-C2n8CwsFnJR8p8rF_C5w3mzlYestAgocPSrDYEQOeFGSj1DVHrdZSbYvqHJsK4Q7Fnq5JMRxNiIOF6oKLpNOUFDQMPo1F7qR5MPIbvzPMq8VwaRHpOHKvviaJbq4Bxz2wUhAROdiwDKn7d6v8Xz9sh2ue0Fnj-odSlUpjyIuh_G2EaTsCKXeF-tJinJ17KqMQrLIbX2AEuJOt1Dau2r81O_xerb451X3WlpsIhDrjDXRaGME2813QEI_X34bjT8FvDiJBhy8nhdH0UgSypgddrDtyAAkzNqBpd82Xf-8MvJSIQ")
        self.collection_loader = PostmanCollectionLoader()
        self.endpoints = {}
        self.current_collection = None
        self.variables: Dict[str, Any] = {}
    def change_bearer_token(self, bearer_token: str):
        self.bearer_token = bearer_token
    def load_collection(self, collection_filename: str):
        """Load a specific Postman collection file."""
        try:
            if not collection_filename:
                collection_filename = self.get_available_collections()[0]
            self.endpoints = self.collection_loader.load_collection_from_file(collection_filename)
            self.variables = self.collection_loader.variables
            self.current_collection = collection_filename
        except Exception as e:
            st.error(f"Failed to load collection {collection_filename}: {e}")
    
    def get_available_collections(self) -> List[str]:
        """Get list of available Postman collection files."""
        return self.collection_loader.get_available_collections()
    
    def test_endpoint(self, endpoint: APIEndpoint, custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single API endpoint."""
        try:
            url = endpoint.url
            if custom_params:
                for param in endpoint.required_params or []:
                    if param in custom_params:
                        url = url.replace(f"{{{param}}}", str(custom_params[param]))
            
            for param in self.variables:
                url = url.replace(f"{{{param}}}", str(self.variables[param]))
            # Prepare headers
            headers = endpoint.headers.copy()
            for key in headers:
                if 'authorization' in key.lower() and 'bearer' in headers[key].lower():
                    headers[key] = f"Bearer {self.bearer_token}"
            
            # Prepare query parameters
            query_params = endpoint.query_params.copy()
            if custom_params:
                for key, value in custom_params.items():
                    query_params[key] = value
            query_params["api_key"] = self.api_key
            body = None
            if endpoint.method == "POST" and endpoint.body_params:
                body = endpoint.body_params.copy()
                if custom_params:
                    for key, value in custom_params.items():
                        if key not in (endpoint.required_params or []):
                            body[key] = value
                body = json.dumps(body)
            url = url.split("?")[0]
            start_time = time.time()
            response = requests.request(
                method=endpoint.method,
                url=url,
                headers=headers,
                params=query_params,
                data=body,
                timeout=30
            )
            end_time = time.time()
            
            # Prepare result
            result = {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": round((end_time - start_time) * 1000, 2),  # ms
                "url": response.url,
                "headers": dict(response.headers),
                "response": None,
                "error": None
            }
            
            # Parse response
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    result["response"] = response.json()
                else:
                    result["response"] = response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            except Exception as e:
                result["response"] = response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            
            if not result["success"]:
                result["error"] = f"HTTP {response.status_code}: {response.reason}"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response_time": None,
                "url": url,
                "headers": {},
                "response": None,
                "error": str(e)
            }
    
    def get_all_categories(self) -> List[str]:
        """Get all available API categories."""
        return list(self.endpoints.keys())
    
    def get_endpoints_by_category(self, category: str) -> List[APIEndpoint]:
        """Get all endpoints for a specific category."""
        return self.endpoints.get(category, [])
    
    def get_endpoint_by_name(self, name: str) -> Optional[APIEndpoint]:
        """Get a specific endpoint by name."""
        for category_endpoints in self.endpoints.values():
            for endpoint in category_endpoints:
                if endpoint.name == name:
                    return endpoint
        return None


class APITestingUI:
    """UI class for the API testing interface."""
    
    def __init__(self):
        self.api_tester = OLAMapsAPITester()
    
    def render(self):
        """Render the main API testing interface."""
        st.title("🗺️ OLA Maps API Testing")
        st.markdown("Test all OLA Maps API endpoints from Postman collections with real-time requests and responses.")
        
        # Collection selection
        self.render_collection_selector()
        
        # Sidebar for API configuration
        with st.sidebar:
            self.render_sidebar_config()

    def render_collection_selector(self):
        """Render the collection file selector."""
        st.markdown("### 📁 Select Postman Collection")
        
        # Get available collections
        available_collections = self.api_tester.get_available_collections()
        
        if not available_collections:
            st.error("No Postman collection files found in the OLAMAPSapi/ directory.")
            st.info("Please ensure your Postman collection files are in the OLAMAPSapi/ folder with the naming pattern: `*.postman_collection.json`")
            return
        # Collection selector
        selected_collection = st.selectbox(
            "Choose a Postman collection:",
            available_collections,
            help="Select a Postman collection file to load its API endpoints",
            index=1,
            key="selected_collection_key",
            on_change=self.api_tester.load_collection(st.session_state.selected_collection_key)
        )
        logger.info(f"Selected collection: {selected_collection}")
        # Load button
        # col1, col2 = st.columns([1, 4])
        # with col1:
        # if st.button("📂 Load Collection", type="primary"):
        #     with st.spinner(f"Loading {selected_collection}..."):
        #         if self.api_tester.load_collection(selected_collection):
        #             st.success(f"✅ Loaded {selected_collection} successfully!")
        #         else:
        #             st.error(f"❌ Failed to load {selected_collection}")
        if not self.api_tester.endpoints:
            st.info("Please select a Postman collection file to start testing.")
            return
        # st.markdown("---")

        self.render_category_view()
        self.render_individual_testing()
        self.render_endpoint_list_view()
        self.render_test_results()
    
    def render_sidebar_config(self):
        """Render the sidebar configuration."""
        st.header("⚙️ API Configuration")
        
        # API Key
        api_key = st.text_input(
            "API Key",
            value=self.api_tester.api_key,
            type="password",
            help="Your OLA Maps API key"
        )
        
        # Bearer Token
        bearer_token = st.text_input(
            "Bearer Token",
            value=self.api_tester.bearer_token,
            type="password",
            help="Your OLA Maps bearer token"
        )
        
        # Update tokens if changed
        if api_key != self.api_tester.api_key:
            self.api_tester.api_key = api_key
        if bearer_token != self.api_tester.bearer_token:
            self.api_tester.bearer_token = bearer_token
        
        st.markdown("---")
        
        # Collection info
        if self.api_tester.current_collection:
            st.subheader("📁 Collection Info")
            st.text(f"File: {self.api_tester.current_collection}")
            
            total_endpoints = sum(len(endpoints) for endpoints in self.api_tester.endpoints.values())
            st.metric("Total Endpoints", total_endpoints)
            st.metric("API Categories", len(self.api_tester.endpoints))
        # input fields for variables also with a button to update the variables
        if self.api_tester.variables:
            for var in self.api_tester.variables:
                st.text_input(f"Variable: {var}", value=self.api_tester.variables[var], key=f"variable_{var}")
            if st.button("Update Variables"):
                self.api_tester.variables = {var: st.session_state.get(f"variable_{var}", self.api_tester.variables[var]) for var in self.api_tester.variables}
                st.success("Variables updated")
        
        # # Quick stats
        # if self.api_tester.endpoints:
        #     st.markdown("---")
        #     st.subheader("📊 Quick Stats")
            
        #     # Count by method
        #     method_counts = {}
        #     for endpoints in self.api_tester.endpoints.values():
        #         for endpoint in endpoints:
        #             method = endpoint.method
        #             method_counts[method] = method_counts.get(method, 0) + 1
            
        #     for method, count in method_counts.items():
        #         st.metric(f"{method} Endpoints", count)
    
    def render_category_view(self):
        """Render the category-based testing view."""
        st.header("📋 API Categories")
        
        if not self.api_tester.endpoints:
            st.info("No endpoints loaded. Please select and load a Postman collection first.")
            return
        
        # Category selection
        selected_category = st.selectbox(
            "Select API Category:",
            self.api_tester.get_all_categories(),
            help="Choose an API category to test all its endpoints"
        )
        
        if selected_category:
            endpoints = self.api_tester.get_endpoints_by_category(selected_category)
            
            st.subheader(f"Endpoints in {selected_category}")
            
            # Test all endpoints in category
            if st.button(f"🧪 Test All {selected_category} Endpoints", type="primary"):
                self.test_category_endpoints(selected_category, endpoints)
            
            # Individual endpoint testing
            for i, endpoint in enumerate(endpoints):
                with st.expander(f"{endpoint.method} {endpoint.name}"):
                    st.markdown(f"**Description:** {endpoint.description}")
                    st.code(f"URL: {endpoint.url}")
                    
                    # Show parameters
                    if endpoint.query_params:
                        st.markdown("**Query Parameters:**")
                        params_df = pd.DataFrame([
                            {"Parameter": k, "Value": v} 
                            for k, v in endpoint.query_params.items()
                        ])
                        st.dataframe(params_df, width='stretch')
                    
                    if endpoint.body_params:
                        st.markdown("**Body Parameters:**")
                        st.json(endpoint.body_params)
                    
                    # Test button
                    if st.button(f"Test {endpoint.name}", key=f"test_{i}"):
                        self.display_test_result(endpoint)
    
    def render_individual_testing(self):
        """Render the individual endpoint testing view."""
        st.header("🔍 Individual Endpoint Testing")
        
        if not self.api_tester.endpoints:
            st.info("No endpoints loaded. Please select and load a Postman collection first.")
            return
        
        # Create a comprehensive endpoint list with better formatting
        endpoint_options = []
        for category, endpoints in self.api_tester.endpoints.items():
            for endpoint in endpoints:
                # Create a more descriptive display name
                display_name = f"[{endpoint.method}] {endpoint.name} ({category})"
                endpoint_options.append((display_name, endpoint))
        
        # Endpoint selection with search
        st.markdown("### 📋 Select Endpoint")
        selected_endpoint_name, selected_endpoint = st.selectbox(
            "Choose an endpoint to test:",
            endpoint_options,
            format_func=lambda x: x[0],
            help="Select an endpoint from the dropdown. Use the search to filter endpoints by name, method, or category."
        )
        logger.info(f"Selected endpoint: {selected_endpoint_name}")
        if selected_endpoint:
            # Display comprehensive endpoint details
            self.display_endpoint_details(selected_endpoint)
            
            # Parameter customization and testing
            self.render_endpoint_testing_interface(selected_endpoint)
    
    def display_endpoint_details(self, endpoint: APIEndpoint):
        """Display comprehensive details for a selected endpoint."""
        st.markdown("---")
        st.markdown("### 📊 Endpoint Details")
        
        # Basic information in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Method", endpoint.method)
        with col2:
            st.metric("Category", endpoint.category)
        with col3:
            required_count = len(endpoint.required_params) if endpoint.required_params else 0
            st.metric("Required Params", required_count)
        
        # Description
        if endpoint.description:
            st.markdown("**Description:**")
            st.info(endpoint.description)
        
        # URL information
        st.markdown("**Endpoint URL:**")
        full_url = f"{endpoint.url}"
        st.code(full_url, language="text")
        
        # Required parameters
        if endpoint.required_params:
            st.markdown("**Required Path Parameters:**")
            for param in endpoint.required_params:
                st.markdown(f"- `{param}`")
        
        # Headers
        if endpoint.headers:
            st.markdown("**Request Headers:**")
            headers_df = pd.DataFrame([
                {"Header": k, "Value": v} 
                for k, v in endpoint.headers.items()
            ])
            st.dataframe(headers_df, width='stretch', hide_index=True)
        
        # Query parameters
        if endpoint.query_params:
            st.markdown("**Query Parameters:**")
            query_params_df = pd.DataFrame([
                {"Parameter": k, "Value": v, "Type": "Query"} 
                for k, v in endpoint.query_params.items()
            ])
            st.dataframe(query_params_df, width='stretch', hide_index=True)
        
        # Body parameters
        if endpoint.body_params:
            st.markdown("**Body Parameters:**")
            st.json(endpoint.body_params)
        
        st.markdown("---")
    
    def render_endpoint_testing_interface(self, endpoint: APIEndpoint):
        """Render the testing interface for a selected endpoint."""
        st.markdown("### 🧪 Test Configuration")
        
        custom_params = {}
        
        # Required parameters input
        if endpoint.required_params:
            st.markdown("**Required Path Parameters:**")
            for param in endpoint.required_params:
                param_value = st.text_input(
                    f"Enter value for `{param}`:",
                    key=f"required_{param}",
                    help=f"Required path parameter: {param}"
                )
                custom_params[param] = param_value
        
        # Query parameters customization
        if endpoint.query_params:
            st.markdown("**Query Parameters:**")
            for key, default_value in endpoint.query_params.items():
                if key != "api_key":  # Don't allow API key modification
                    new_value = st.text_input(
                        f"Query Parameter: `{key}`",
                        value=default_value,
                        key=f"query_{key}",
                        help=f"Query parameter: {key}"
                    )
                    custom_params[key] = new_value
        
        # Body parameters for POST/PUT/PATCH requests
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and endpoint.body_params:
            st.markdown("**Body Parameters:**")
            body_json = st.text_area(
                "Request Body (JSON):",
                value=json.dumps(endpoint.body_params, indent=2),
                height=200,
                key="body_json",
                help="Modify the request body JSON as needed"
            )
            try:
                body_params = json.loads(body_json)
                custom_params.update(body_params)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format in body parameters")
                return
        
        # Test button
        if st.button("🚀 Test Endpoint", type="primary", width='stretch'):
                # Validate required parameters
                missing_params = []
                for param in (endpoint.required_params or []):
                    if not custom_params.get(param):
                        missing_params.append(param)
                logger.info(f"Missing parameters: {missing_params}")
                if missing_params:
                    st.error(f"❌ Missing required parameters: {missing_params}")
                else:
                    with st.spinner("Testing endpoint..."):
                        self.display_test_result(endpoint, custom_params)
        if st.button("🔄 Reset Parameters", width='stretch'):
                st.rerun()
    
    def render_endpoint_list_view(self):
        """Render a comprehensive endpoint list view with filtering and search."""
        st.header("📋 Complete Endpoint List")
        
        if not self.api_tester.endpoints:
            st.info("No endpoints loaded. Please select and load a Postman collection first.")
            return
        
        # Get all endpoints
        all_endpoints = []
        for category, endpoints in self.api_tester.endpoints.items():
            for endpoint in endpoints:
                all_endpoints.append(endpoint)
        
        # Summary statistics
        st.markdown("### 📊 Endpoint Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Endpoints", len(all_endpoints))
        with col2:
            categories = len(self.api_tester.endpoints)
            st.metric("Categories", categories)
        with col3:
            methods = set(endpoint.method for endpoint in all_endpoints)
            st.metric("HTTP Methods", len(methods))
        with col4:
            required_total = sum(len(endpoint.required_params) if endpoint.required_params else 0 for endpoint in all_endpoints)
            st.metric("Required Params", required_total)
        
        # Filtering options
        st.markdown("### 🔍 Filter Endpoints")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Category filter
            all_categories = ["All Categories"] + self.api_tester.get_all_categories()
            selected_category_filter = st.selectbox(
                "Filter by Category:",
                all_categories,
                help="Filter endpoints by API category"
            )
        
        with col2:
            # Method filter
            all_methods = ["All Methods"] + sorted(list(set(endpoint.method for endpoint in all_endpoints)))
            selected_method_filter = st.selectbox(
                "Filter by Method:",
                all_methods,
                help="Filter endpoints by HTTP method"
            )
        
        with col3:
            # Search by name
            search_term = st.text_input(
                "Search by name:",
                placeholder="Enter endpoint name...",
                help="Search endpoints by name"
            )
        
        # Apply filters
        filtered_endpoints = all_endpoints.copy()
        
        if selected_category_filter != "All Categories":
            filtered_endpoints = [ep for ep in filtered_endpoints if ep.category == selected_category_filter]
        
        if selected_method_filter != "All Methods":
            filtered_endpoints = [ep for ep in filtered_endpoints if ep.method == selected_method_filter]
        
        if search_term:
            filtered_endpoints = [ep for ep in filtered_endpoints if search_term.lower() in ep.name.lower()]
        
        # Show filter results
        st.markdown(f"### 📋 Endpoints ({len(filtered_endpoints)} found)")
        
        if not filtered_endpoints:
            st.info("No endpoints match the current filters.")
            return
        
        # Create endpoint options for selection
        endpoint_options = []
        for endpoint in filtered_endpoints:
            display_name = f"[{endpoint.method}] {endpoint.name} ({endpoint.category})"
            endpoint_options.append((display_name, endpoint))
        
        # Endpoint selection
        selected_endpoint_name, selected_endpoint = st.selectbox(
            "Select an endpoint to view details:",
            endpoint_options,
            format_func=lambda x: x[0],
            help="Choose an endpoint from the filtered list to view its details"
        )
        logger.info(f"Selected endpoint: {selected_endpoint_name}")
        if selected_endpoint:
            # Display endpoint details
            self.display_endpoint_details(selected_endpoint)
            
            # Quick test interface
            st.markdown("### 🧪 Quick Test")
            if st.button(f"🚀 Test {selected_endpoint.name}", type="secondary"):
                self.display_test_result(selected_endpoint)
        
        # Show all filtered endpoints in a table
        st.markdown("### 📋 All Filtered Endpoints")
        
        # Create a summary table
        endpoint_summary_data = []
        for endpoint in filtered_endpoints:
            endpoint_summary_data.append({
                "Method": endpoint.method,
                "Name": endpoint.name,
                "Category": endpoint.category,
                "Required Params": len(endpoint.required_params) if endpoint.required_params else 0,
                "Query Params": len(endpoint.query_params) if endpoint.query_params else 0,
                "Has Body": "Yes" if endpoint.body_params else "No",
                "Description": endpoint.description[:100] + "..." if len(endpoint.description) > 100 else endpoint.description
            })
        
        if endpoint_summary_data:
            summary_df = pd.DataFrame(endpoint_summary_data)
            st.dataframe(summary_df, width='stretch')
        
        # Alternative: Show endpoints in expandable sections
        st.markdown("### 📋 Detailed View")
        for i, endpoint in enumerate(filtered_endpoints):
            with st.expander(f"{endpoint.method} {endpoint.name} ({endpoint.category})"):
                st.markdown(f"**Description:** {endpoint.description}")
                st.code(f"URL: {endpoint.url}")
                
                # Show parameters
                if endpoint.query_params:
                    st.markdown("**Query Parameters:**")
                    params_df = pd.DataFrame([
                        {"Parameter": k, "Value": v} 
                        for k, v in endpoint.query_params.items()
                    ])
                    st.dataframe(params_df, width='stretch')
                
                if endpoint.body_params:
                    st.markdown("**Body Parameters:**")
                    st.json(endpoint.body_params)
                
                # Test button
                if st.button(f"Test {endpoint.name}", key=f"list_test_{i}"):
                    self.display_test_result(endpoint)
    
    def render_test_results(self):
        """Render the test results view."""
        st.header("📊 Test Results")
        
        # Initialize session state for results if not exists
        if "api_test_results" not in st.session_state:
            st.session_state.api_test_results = []
        
        if st.session_state.api_test_results:
            # Summary statistics
            total_tests = len(st.session_state.api_test_results)
            successful_tests = sum(1 for r in st.session_state.api_test_results if r["success"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tests", total_tests)
            with col2:
                st.metric("Successful", successful_tests)
            with col3:
                st.metric("Success Rate", f"{(successful_tests/total_tests)*100:.1f}%")
            
            # Results table
            st.subheader("Test Results")
            results_df = pd.DataFrame(st.session_state.api_test_results)
            st.dataframe(results_df, width='stretch')
            
            # Clear results
            if st.button("🗑️ Clear Results"):
                st.session_state.api_test_results = []
                st.rerun()
        else:
            st.info("No test results available. Run some tests to see results here.")
    
    def test_category_endpoints(self, category: str, endpoints: List[APIEndpoint]):
        """Test all endpoints in a category."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        for i, endpoint in enumerate(endpoints):
            status_text.text(f"Testing {endpoint.name}...")
            result = self.api_tester.test_endpoint(endpoint)
            result["endpoint_name"] = endpoint.name
            result["category"] = category
            results.append(result)
            progress_bar.progress((i + 1) / len(endpoints))
        
        status_text.text("Testing completed!")
        
        # Store results in session state
        if "api_test_results" not in st.session_state:
            st.session_state.api_test_results = []
        st.session_state.api_test_results.extend(results)
        
        # Show summary
        successful = sum(1 for r in results if r["success"])
        st.success(f"✅ Completed testing {len(endpoints)} endpoints. {successful} successful, {len(endpoints) - successful} failed.")
    
    def display_test_result(self, endpoint: APIEndpoint,custom_params: Dict[str, Any] = None):
        """Display a single test result."""
        st.markdown("### 📊 Test Result")
        result = self.api_tester.test_endpoint(endpoint, custom_params)
        # logger.info(f"Test endpoint: {endpoint}")
        # logger.info(f"Test result: {result}")
        # Status indicator
        if result["success"]:
            st.success(f"✅ Success (HTTP {result['status_code']})")
        else:
            st.error(f"❌ Failed: {result['error']}")
        
        # Response details
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Response Time", f"{result['response_time']}ms" if result['response_time'] else "N/A")
        with col2:
            st.metric("Status Code", result['status_code'] or "N/A")
        
        # URL
        st.markdown("**Request URL:**")
        st.code(result['url'])
        
        # Response
        if result["response"]:
            st.markdown("**Response:**")
            if isinstance(result["response"], dict):
                st.json(result["response"], expanded=False)
            else:
                st.text(result["response"])
        
        # Store result
        if "api_test_results" not in st.session_state:
            st.session_state.api_test_results = []
        
        result_copy = result.copy()
        result_copy["endpoint_name"] = endpoint.name
        result_copy["category"] = endpoint.category
        st.session_state.api_test_results.append(result_copy)
