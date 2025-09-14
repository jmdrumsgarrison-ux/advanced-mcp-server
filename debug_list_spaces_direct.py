#!/usr/bin/env python3
"""
Debug script to test HuggingFace list_spaces function directly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from huggingface_hub import login, list_spaces
    
    # Get token
    token = os.getenv("HUGGINGFACE_TOKEN")
    print(f"Token available: {bool(token)}")
    print(f"Token starts with: {token[:10] if token else 'None'}...")
    
    # Login globally
    print("Attempting global login...")
    login(token=token)
    print("Global login successful!")
    
    # Test list_spaces with minimal parameters
    print("Testing list_spaces with no parameters...")
    spaces_iter = list_spaces(limit=3)
    spaces_list = list(spaces_iter)
    
    print(f"Retrieved {len(spaces_list)} spaces")
    for space in spaces_list:
        print(f"- {space.id}")
        
    print("SUCCESS: Direct list_spaces works!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
