#!/usr/bin/env python3
"""
Google API Discovery Tool
Uses the Google Discovery API to check available services and APIs
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime

# Add project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_google_apis():
    """Discover available Google APIs using the Discovery service"""
    try:
        from google.oauth2.service_account import Credentials as ServiceAccountCredentials
        from googleapiclient.discovery import build
        
        logger.info("[STARTING] Google API Discovery")
        
        # Get service account credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
            logger.error("Service account credentials not found")
            return False
        
        # Create credentials with broad scope for discovery
        creds = ServiceAccountCredentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Build Discovery service
        discovery = build('discovery', 'v1', credentials=creds)
        
        # Get list of available APIs
        logger.info("Fetching available Google APIs...")
        apis = discovery.apis().list().execute()
        
        if 'items' not in apis:
            logger.warning("No APIs discovered")
            return False
        
        # Organize APIs by category
        api_categories = {}
        total_apis = 0
        
        for api in apis['items']:
            name = api.get('name', 'unknown')
            version = api.get('version', 'unknown')
            title = api.get('title', name)
            description = api.get('description', 'No description')
            category = api.get('category', 'Other')
            
            if category not in api_categories:
                api_categories[category] = []
            
            api_categories[category].append({
                'name': name,
                'version': version,
                'title': title,
                'description': description,
                'discovery_url': api.get('discoveryRestUrl', ''),
                'documentation': api.get('documentationLink', '')
            })
            total_apis += 1
        
        # Display results
        logger.info(f"[SUCCESS] Discovered {total_apis} Google APIs")
        logger.info("=" * 80)
        logger.info("GOOGLE API DISCOVERY RESULTS")
        logger.info("=" * 80)
        
        # Show categories and APIs
        for category, api_list in sorted(api_categories.items()):
            logger.info(f"\n[CATEGORY] {category} ({len(api_list)} APIs)")
            logger.info("-" * 60)
            
            for api in sorted(api_list, key=lambda x: x['name']):
                logger.info(f"  [API] {api['name']} v{api['version']}")
                logger.info(f"        Title: {api['title']}")
                if len(api['description']) < 100:
                    logger.info(f"        Description: {api['description']}")
                else:
                    logger.info(f"        Description: {api['description'][:97]}...")
        
        # Show our currently implemented services
        logger.info("\n" + "=" * 80)
        logger.info("CURRENTLY IMPLEMENTED IN MCP SERVER")
        logger.info("=" * 80)
        
        implemented_services = [
            {'name': 'drive', 'version': 'v3', 'status': 'ACTIVE'},
            {'name': 'sheets', 'version': 'v4', 'status': 'ACTIVE'},
            {'name': 'docs', 'version': 'v1', 'status': 'ACTIVE'},
            {'name': 'calendar', 'version': 'v3', 'status': 'ACTIVE'},
            {'name': 'customsearch', 'version': 'v1', 'status': 'ACTIVE (API Key)'},
        ]
        
        for service in implemented_services:
            logger.info(f"  [IMPLEMENTED] {service['name']} v{service['version']} - {service['status']}")
        
        # Suggest interesting APIs for potential integration
        logger.info("\n" + "=" * 80)
        logger.info("INTERESTING APIS FOR POTENTIAL INTEGRATION")
        logger.info("=" * 80)
        
        interesting_apis = [
            'gmail', 'youtube', 'translate', 'storage', 'bigquery', 
            'cloudresourcemanager', 'iam', 'monitoring', 'logging',
            'pubsub', 'vision', 'speech', 'language', 'maps'
        ]
        
        found_interesting = []
        for api in apis['items']:
            if api.get('name') in interesting_apis:
                found_interesting.append({
                    'name': api.get('name'),
                    'version': api.get('version'),
                    'title': api.get('title'),
                    'description': api.get('description', '')[:100] + '...' if len(api.get('description', '')) > 100 else api.get('description', '')
                })
        
        for api in sorted(found_interesting, key=lambda x: x['name']):
            logger.info(f"  [POTENTIAL] {api['name']} v{api['version']}")
            logger.info(f"              {api['title']}")
            logger.info(f"              {api['description']}")
            logger.info("")
        
        logger.info(f"[SUMMARY] Total APIs available: {total_apis}")
        logger.info(f"[SUMMARY] Currently implemented: {len(implemented_services)}")
        logger.info(f"[SUMMARY] Interesting for integration: {len(found_interesting)}")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAILURE] API Discovery failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False

def check_specific_api_access():
    """Check access to specific APIs we might want to use"""
    try:
        from google.oauth2.service_account import Credentials as ServiceAccountCredentials
        from googleapiclient.discovery import build
        
        logger.info("\n[TESTING] Checking specific API access...")
        
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        creds = ServiceAccountCredentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Test APIs that might be useful
        test_apis = [
            ('gmail', 'v1'),
            ('youtube', 'v3'),
            ('translate', 'v3'),
            ('storage', 'v1'),
            ('cloudresourcemanager', 'v1'),
            ('iam', 'v1'),
            ('vision', 'v1'),
            ('speech', 'v1')
        ]
        
        logger.info("\nAPI ACCESS TEST RESULTS:")
        logger.info("-" * 40)
        
        for api_name, version in test_apis:
            try:
                service = build(api_name, version, credentials=creds)
                logger.info(f"  [ACCESSIBLE] {api_name} v{version}")
            except Exception as e:
                logger.info(f"  [NOT ACCESSIBLE] {api_name} v{version} - {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAILURE] API access check failed: {e}")
        return False

def main():
    """Run Google API discovery"""
    logger.info("=" * 80)
    logger.info("GOOGLE API DISCOVERY AND SERVICE ANALYSIS")
    logger.info("=" * 80)
    
    # Test 1: Discover available APIs
    discovery_success = discover_google_apis()
    
    # Test 2: Check specific API access
    access_success = check_specific_api_access()
    
    if discovery_success and access_success:
        logger.info("\n[SUCCESS] Google API discovery completed successfully!")
        return 0
    else:
        logger.error("\n[FAILURE] Some discovery tests failed!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Discovery execution failed: {e}")
        sys.exit(1)
