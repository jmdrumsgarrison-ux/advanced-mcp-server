#!/usr/bin/env python3
"""
Minimal test to debug the exact list_spaces API call
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== MINIMAL LIST_SPACES DEBUG ===")

try:
    from huggingface_hub import HfApi, login
    
    # Get token
    token = os.getenv('HUGGINGFACE_TOKEN')
    print(f"Token: {token[:20]}...")
    
    # Create API client
    api = HfApi()
    
    # Test the EXACT call our implementation makes
    print("\n=== TESTING EXACT API CALL ===")
    
    # This mimics our implementation
    kwargs = {
        'token': token,
        'author': 'huggingface',
        'limit': 3
    }
    
    print(f"Calling api.list_spaces with kwargs: {kwargs}")
    
    try:
        spaces = api.list_spaces(**kwargs)
        spaces_list = list(spaces)
        print(f"SUCCESS: Found {len(spaces_list)} spaces")
        for space in spaces_list:
            print(f"  - {space.id}")
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Error type: {type(e)}")
        
        # Try without token parameter
        print("\n=== TESTING WITHOUT EXPLICIT TOKEN ===")
        try:
            login(token=token)
            kwargs_no_token = {'author': 'huggingface', 'limit': 3}
            spaces = api.list_spaces(**kwargs_no_token)
            spaces_list = list(spaces)
            print(f"SUCCESS without explicit token: Found {len(spaces_list)} spaces")
        except Exception as e2:
            print(f"ERROR without token: {e2}")
            
except Exception as e:
    print(f"SETUP ERROR: {e}")
