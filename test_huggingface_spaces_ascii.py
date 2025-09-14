#!/usr/bin/env python3
"""
Test Hugging Face Spaces Integration - ASCII Version
Test the Hugging Face API integration in the Advanced MCP Server
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_huggingface_spaces():
    """Test Hugging Face Spaces listing through API Manager"""
    print("TESTING HUGGING FACE SPACES INTEGRATION")
    print("=" * 50)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for Hugging Face token
        hf_token = os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN')
        if not hf_token:
            print("ERROR: No Hugging Face API token found in environment")
            print("   Expected: HUGGINGFACE_TOKEN, HUGGINGFACE_API_KEY or HF_TOKEN")
            return False
        
        print(f"SUCCESS: Hugging Face token found: {hf_token[:8]}...")
        
        # Import the API manager
        from api_manager import APIManager
        
        # Create API manager instance
        api_manager = APIManager()
        print("SUCCESS: API Manager created")
        
        # Initialize APIs
        await api_manager.initialize()
        print("SUCCESS: APIs initialized")
        
        # Check if Hugging Face client is available
        if hasattr(api_manager, 'hf_api') and api_manager.hf_api:
            print("SUCCESS: Hugging Face client is available")
            
            # Try to make a direct API call to list spaces
            import requests
            
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            # Get current user info first
            print("\nGetting user information...")
            user_response = requests.get("https://huggingface.co/api/whoami", headers=headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                username = user_data.get('name', 'Unknown')
                print(f"SUCCESS: Authenticated as: {username}")
                
                # Now get spaces for this user
                print(f"\nGetting Spaces for user: {username}")
                spaces_url = f"https://huggingface.co/api/spaces"
                spaces_response = requests.get(spaces_url, headers=headers, params={
                    "author": username,
                    "limit": 100
                })
                
                if spaces_response.status_code == 200:
                    spaces_data = spaces_response.json()
                    
                    if spaces_data:
                        print(f"SUCCESS: Found {len(spaces_data)} Spaces:")
                        print("-" * 40)
                        
                        for i, space in enumerate(spaces_data, 1):
                            name = space.get('id', 'Unknown')
                            likes = space.get('likes', 0)
                            sdk = space.get('sdk', 'Unknown')
                            private = space.get('private', False)
                            status = "PRIVATE" if private else "PUBLIC"
                            
                            print(f"{i}. {name}")
                            print(f"   SDK: {sdk} | Likes: {likes} | {status}")
                            print(f"   URL: https://huggingface.co/spaces/{name}")
                            print()
                    else:
                        print("INFO: No Spaces found for your account")
                        print("   This could mean:")
                        print("   - You haven't created any Spaces yet")
                        print("   - All your Spaces are private and not returned by this endpoint")
                        print("   - API permissions issue")
                else:
                    print(f"ERROR: Failed to get Spaces: HTTP {spaces_response.status_code}")
                    print(f"Response: {spaces_response.text}")
            else:
                print(f"ERROR: Failed to authenticate: HTTP {user_response.status_code}")
                print(f"Response: {user_response.text}")
                return False
                
        else:
            print("ERROR: Hugging Face client not available in API Manager")
            return False
            
        print("\nSUCCESS: Hugging Face Spaces test completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing Hugging Face Spaces: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_huggingface_spaces())
    
    if result:
        print("\nSUCCESS: Hugging Face integration working!")
        sys.exit(0)
    else:
        print("\nFAILED: Hugging Face integration issues detected")
        sys.exit(1)
