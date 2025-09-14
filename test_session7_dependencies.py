#!/usr/bin/env python3
"""
Dependencies validation test for Session 7
"""

import sys
import pkg_resources
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test all required dependencies"""
    logger.info("[STARTING] Dependencies validation test")
    
    required_packages = [
        'mcp',
        'aiohttp', 
        'aiofiles',
        'huggingface_hub',
        'openai',
        'google-auth',
        'google-auth-oauthlib', 
        'google-auth-httplib2',
        'google-api-python-client',
        'cryptography',
        'keyring',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    available_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            available_packages.append(package)
            logger.info(f"[FOUND] {package}")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            logger.error(f"[MISSING] {package}")
    
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
