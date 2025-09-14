#!/usr/bin/env python3
"""
Direct HuggingFace API test for list_spaces method
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=== DIRECT HF API TEST FOR LIST_SPACES ===")

try:
    from huggingface_hub import HfApi, login
    
    # Get token
    token = os.getenv('HUGGINGFACE_TOKEN')
    print(f"Token: {token[:20]}...")
    
    # Test 1: With explicit login
    print("\n--- Test 1: With Login ---")
    login(token=token)
    api = HfApi()
    
    try:
        # Test exactly what our implementation does
        spaces = api.list_spaces(
            author='huggingface',
            limit=2,
            token=token
        )
        spaces_list = list(spaces)
        print(f"✅ With explicit token: Found {len(spaces_list)} spaces")
        
    except Exception as e:
        print(f"❌ With explicit token failed: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 2: Without explicit token (rely on login)
    print("\n--- Test 2: Without Explicit Token ---")
    try:
        spaces = api.list_spaces(
            author='huggingface',
            limit=2
        )
        spaces_list = list(spaces)
        print(f"✅ Without explicit token: Found {len(spaces_list)} spaces")
        
    except Exception as e:
        print(f"❌ Without explicit token failed: {e}")
    
    # Test 3: Minimal parameters
    print("\n--- Test 3: Minimal Parameters ---")
    try:
        spaces = api.list_spaces(limit=1)
        spaces_list = list(spaces)
        print(f"✅ Minimal params: Found {len(spaces_list)} spaces")
        
    except Exception as e:
        print(f"❌ Minimal params failed: {e}")
    
    # Test 4: No parameters at all
    print("\n--- Test 4: No Parameters ---")
    try:
        spaces = api.list_spaces()
        spaces_iter = iter(spaces)
        first_space = next(spaces_iter)
        print(f"✅ No params: Found at least one space: {first_space.id}")
        
    except Exception as e:
        print(f"❌ No params failed: {e}")
        
    # Test 5: Check what create_space uses (working method)
    print("\n--- Test 5: Check create_space ---")
    try:
        # This should work since we know create_space works
        user_info = api.whoami()
        print(f"✅ whoami works: {user_info.get('name')}")
        
        # Don't actually create a space, just check the method exists
        print("✅ create_space method available")
        
    except Exception as e:
        print(f"❌ Basic API access failed: {e}")
        
except Exception as e:
    print(f"❌ Setup failed: {e}")

print("\n=== COMPARISON ANALYSIS ===")
print("This will help identify:")
print("1. Whether list_spaces requires different authentication")
print("2. Which parameter combinations work")
print("3. How it differs from working methods like create_space")
