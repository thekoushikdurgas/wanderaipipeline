#!/usr/bin/env python3
"""
Test script for the get_bearer_token function in AddPlacePage class.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.add_place_page import AddPlacePage

def test_bearer_token():
    """Test the get_bearer_token function."""
    print("🧪 Testing get_bearer_token function...")
    
    # Create AddPlacePage instance
    add_place_page = AddPlacePage()
    
    try:
        # Call the get_bearer_token function
        result = add_place_page.get_bearer_token()
        
        # Check the result
        if result.get("success"):
            print("✅ Bearer token generated successfully!")
            print(f"Status Code: {result.get('status_code')}")
            print(f"Response Time: {result.get('response_time')} ms")
            print(f"Token Type: {result.get('token_type', 'N/A')}")
            print(f"Expires In: {result.get('expires_in', 'N/A')} seconds")
            print(f"Scope: {result.get('scope', 'N/A')}")
            
            # Show token (masked for security)
            token = result.get("bearer_token", "")
            if token:
                masked_token = token[:20] + "..." + token[-20:] if len(token) > 40 else "***"
                print(f"Bearer Token: {masked_token}")
                print(f"Token Length: {len(token)} characters")
        else:
            print(f"❌ Failed to generate bearer token: {result.get('error', 'Unknown error')}")
            print(f"Status Code: {result.get('status_code')}")
            print(f"Response Time: {result.get('response_time')} ms")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_bearer_token()
