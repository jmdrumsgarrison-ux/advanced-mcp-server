#!/usr/bin/env python3
"""
Simple debug test for service account credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=== DEBUG: Service Account Credentials ===")

# Check environment variable
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(f"Environment variable: {credentials_path}")

# Check if file exists
if credentials_path:
    file_exists = os.path.exists(credentials_path)
    print(f"File exists: {file_exists}")
    
    if file_exists:
        file_size = os.path.getsize(credentials_path)
        print(f"File size: {file_size} bytes")
    else:
        print("File not found!")
else:
    print("Environment variable not set!")

# Try to import Google service account
try:
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    print("✅ Google service account import successful")
except ImportError as e:
    print(f"❌ Google service account import failed: {e}")

# Try to load credentials
if credentials_path and os.path.exists(credentials_path):
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )
        print("✅ Service account credentials loaded successfully")
        print(f"Service account email: {creds.service_account_email}")
    except Exception as e:
        print(f"❌ Failed to load service account credentials: {e}")

print("=== DEBUG COMPLETE ===")
