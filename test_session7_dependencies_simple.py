#!/usr/bin/env python3
"""
Simple dependencies validation test for Session 7
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test all required dependencies by importing"""
    logger.info("[STARTING] Dependencies validation test")
    
    test_imports = [
        ('aiohttp', 'aiohttp'),
        ('aiofiles', 'aiofiles'), 
        ('huggingface_hub', 'huggingface_hub'),
        ('openai', 'openai'),
        ('google.auth', 'google-auth'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('google.auth.transport.requests', 'google-auth-httplib2'),
        ('googleapiclient', 'google-api-python-client'),
        ('cryptography', 'cryptography'),
        ('keyring', 'keyring'),
        ('requests', 'requests'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    available_packages = []
    
    for import_name, package_name in test_imports:
        try:
            __import__(import_name)
            available_packages.append(package_name)
            logger.info(f"[FOUND] {package_name}")
        except ImportError as e:
            missing_packages.append(package_name)
            logger.error(f"[MISSING] {package_name}: {e}")
    
    logger.info(f"\nDependencies Summary:")
    logger.info(f"Available: {len(available_packages)}")
    logger.info(f"Missing: {len(missing_packages)}")
    
    if missing_packages:
        logger.error(f"[FAILURE] Missing dependencies: {missing_packages}")
        return False
    else:
        logger.info("[SUCCESS] All dependencies are available")
        return True

if __name__ == "__main__":
    success = test_dependencies()
    sys.exit(0 if success else 1)
