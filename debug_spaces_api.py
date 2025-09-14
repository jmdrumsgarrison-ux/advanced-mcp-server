#!/usr/bin/env python3
"""
Debug script to test HuggingFace list_spaces API directly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== HUGGINGFACE SPACES API DEBUG ===")

try:
    from huggingface_hub import HfApi, login
    print("[OK] HuggingFace Hub library imported")
    
    # Get token
    token = os.getenv('HUGGINGFACE_TOKEN')
    print(f"[OK] Token loaded: {token[:20]}..." if token else "[ERROR] No token found")
    
    # Login and create API client
    login(token=token)
    api = HfApi()
    print("[OK] HF API client created")
    
    # Test 1: Check whoami (this should work)
    print("\n=== TEST 1: WHOAMI ===")
    try:
        user_info = api.whoami(token=token)
        print(f"[SUCCESS] Authenticated as: {user_info['name']}")
    except Exception as e:
        print(f"[ERROR] Whoami failed: {e}")
    
    # Test 2: Try list_spaces with minimal parameters
    print("\n=== TEST 2: LIST_SPACES (MINIMAL) ===")
    try:
        # Using exact parameter names from documentation
        spaces = api.list_spaces(
            limit=3,
            token=token
        )
        spaces_list = list(spaces)
        print(f"[SUCCESS] Listed {len(spaces_list)} spaces")
        for space in spaces_list:
            print(f"  - {space.id}")
    except Exception as e:
        print(f"[ERROR] list_spaces minimal failed: {e}")
        print(f"[ERROR] Error type: {type(e)}")
    
    # Test 3: Try list_spaces with author parameter
    print("\n=== TEST 3: LIST_SPACES (WITH AUTHOR) ===")
    try:
        spaces = api.list_spaces(
            author="huggingface",
            limit=2,
            token=token
        )
        spaces_list = list(spaces)
        print(f"[SUCCESS] Listed {len(spaces_list)} spaces by huggingface")
        for space in spaces_list:
            print(f"  - {space.id}")
    except Exception as e:
        print(f"[ERROR] list_spaces with author failed: {e}")
        print(f"[ERROR] Error type: {type(e)}")
    
    # Test 4: Check if the issue is parameter-related
    print("\n=== TEST 4: PARAMETER TEST ===")
    try:
        # Try with potential wrong parameter name
        print("Testing parameter combinations...")
        
        # Correct parameters (per documentation)
        correct_kwargs = {
            'author': 'huggingface',
            'limit': 2,
            'token': token
        }
        
        print(f"Correct parameters: {list(correct_kwargs.keys())}")
        spaces = api.list_spaces(**correct_kwargs)
        spaces_list = list(spaces)
        print(f"[SUCCESS] Correct parameters worked: {len(spaces_list)} spaces")
        
    except Exception as e:
        print(f"[ERROR] Parameter test failed: {e}")
    
    print("\n=== DIAGNOSTIC COMPLETE ===")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
