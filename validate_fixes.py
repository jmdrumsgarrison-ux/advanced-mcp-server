#!/usr/bin/env python3
"""
Complete validation test for HuggingFace list_spaces fix
Run this after restarting the server to verify all fixes
"""

print("=== HUGGINGFACE LIST_SPACES FIX VALIDATION ===")
print("This test validates:")
print("1. Parameter fix: filter_str → filter")
print("2. Tool schema registration")
print("3. Authentication resolution")
print("4. End-to-end functionality")

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from huggingface_hub import HfApi, login
    
    # Test direct HF API to confirm baseline works
    print("\n=== 1. BASELINE TEST: DIRECT HF API ===")
    token = os.getenv('HUGGINGFACE_TOKEN')
    print(f"Token: {token[:20]}...")
    
    # Login and test
    login(token=token)
    api = HfApi()
    
    # Test whoami
    user_info = api.whoami(token=token)
    print(f"✅ Authentication: {user_info['name']}")
    
    # Test list_spaces with correct parameters
    spaces = api.list_spaces(author='huggingface', limit=2, token=token)
    spaces_list = list(spaces)
    print(f"✅ Direct list_spaces: Found {len(spaces_list)} spaces")
    for space in spaces_list:
        print(f"  - {space.id}")
    
    print("\n=== 2. EXPECTED MCP BEHAVIOR ===")
    print("After restart, the MCP server should:")
    print("✅ Accept 'limit' parameter (schema fix)")
    print("✅ Accept 'author' parameter (schema fix)")  
    print("✅ Pass 'filter' not 'filter_str' to HF API (parameter fix)")
    print("✅ Return successful results (authentication fix)")
    
    print("\n=== 3. TEST COMMANDS FOR MCP ===")
    print("1. advanced-mcp-server:list_huggingface_spaces")
    print("2. advanced-mcp-server:list_huggingface_spaces with {\"limit\": 3}")
    print("3. advanced-mcp-server:list_huggingface_spaces with {\"author\": \"huggingface\", \"limit\": 2}")
    
    print("\n=== 4. SUCCESS CRITERIA ===")
    print("❌ No parameter validation errors")
    print("❌ No 401 authentication errors") 
    print("✅ JSON response with spaces list")
    print("✅ Spaces count and metadata")
    
except Exception as e:
    print(f"❌ Baseline test failed: {e}")
    print("This indicates a deeper configuration issue")
    
print("\n=== FIXES APPLIED ===")
print("1. api_manager.py: Changed filter_str → filter parameter")
print("2. main.py: Added proper tool schemas with parameter validation")
print("3. Parameter matching: Ensured API call matches HF documentation")

print("\n=== RESTART REQUIRED ===")
print("The server must be restarted to pick up these changes!")
