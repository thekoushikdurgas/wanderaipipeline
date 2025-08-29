#!/usr/bin/env python3
"""
Test script for the enhanced OLA Maps API Tester
"""

import streamlit as st
from api_testing.ola_maps_api_tester import APITestingUI

def main():
    """Main function to run the API testing interface."""
    # Set page config
    st.set_page_config(
        page_title="OLA Maps API Tester",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize and render the API testing UI
    ui = APITestingUI()
    ui.render()

if __name__ == "__main__":
    main()
