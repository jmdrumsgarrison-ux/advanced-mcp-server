#!/usr/bin/env python3
"""
Test script for Web Scraping functionality
Tests the Great Learning course downloader and web scraper modules
"""

import sys
import json
import asyncio
import logging
from pathlib import Path

# Add the project directory to the path
sys.path.append(str(Path(__file__).parent))

from course_downloader import GreatLearningDownloader, ScrapingError
from web_scraper import WebScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_credentials():
    """Load credentials for testing"""
    try:
        keys_file = Path("G:/projects/keys.txt")
        if keys_file.exists():
            with open(keys_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract Great Learning credentials
            lines = content.split('\n')
            username = None
            password = None
            
            for i, line in enumerate(lines):
                if 'Great Learnings Password' in line or 'Great Learning' in line:
                    # Look for U: and P: lines after this
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].startswith('U:'):
                            username = lines[j].split(':', 1)[1].strip()
                        elif lines[j].startswith('P:'):
                            password = lines[j].split(':', 1)[1].strip()
            
            return username, password
        else:
            logger.error("Keys file not found")
            return None, None
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return None, None

def test_basic_functionality():
    """Test basic web scraper functionality"""
    print("\n=== TESTING BASIC WEB SCRAPER FUNCTIONALITY ===")
    
    # Test WebScraper initialization
    try:
        scraper = WebScraper("https://example.com", "test_downloads")
        print("✅ WebScraper initialization: PASSED")
        
        # Test download stats (should work even with empty directory)
        stats = scraper.get_download_stats()
        print(f"✅ Download stats: {stats}")
        
        scraper.close()
        print("✅ WebScraper cleanup: PASSED")
        
    except Exception as e:
        print(f"❌ WebScraper basic test: FAILED - {e}")

def test_great_learning_downloader():
    """Test Great Learning specific functionality"""
    print("\n=== TESTING GREAT LEARNING DOWNLOADER ===")
    
    try:
        # Initialize downloader
        downloader = GreatLearningDownloader("temp_downloads")
        print("✅ GreatLearningDownloader initialization: PASSED")
        
        # Test credentials loading
        username, password = load_test_credentials()
        if username and password:
            print(f"✅ Credentials loaded: {username[:5]}...")
            
            # Test login (this will actually attempt to login)
            print("🔄 Attempting login to Great Learning...")
            login_success = downloader.login(username, password)
            
            if login_success:
                print("✅ Login: PASSED")
                
                # Test getting available courses
                try:
                    print("🔄 Getting available courses...")
                    courses = downloader.get_available_courses()
                    print(f"✅ Available courses: Found {len(courses)} courses")
                    
                    if courses:
                        print("📋 Sample courses:")
                        for course in courses[:3]:  # Show first 3 courses
                            print(f"   - {course.get('title', 'Unknown')} (ID: {course.get('id', 'Unknown')})")
                    
                except Exception as e:
                    print(f"⚠️  Get available courses: {e}")
                
                # Test course info for specific course (18132)
                try:
                    print("🔄 Getting course info for course 18132...")
                    course_info = downloader.get_course_info("18132")
                    print(f"✅ Course info: {course_info['title']}")
                    print(f"   - Modules: {len(course_info['modules'])}")
                    print(f"   - Resources: {len(course_info['resources'])}")
                    
                except Exception as e:
                    print(f"⚠️  Get course info: {e}")
                
            else:
                print("❌ Login: FAILED")
        else:
            print("❌ Credentials not found - cannot test login")
        
        # Test download stats
        stats = downloader.get_download_stats()
        print(f"✅ Download stats: {stats['total_files']} files, {stats['total_size_mb']} MB")
        
        downloader.close()
        print("✅ GreatLearningDownloader cleanup: PASSED")
        
    except Exception as e:
        print(f"❌ GreatLearningDownloader test: FAILED - {e}")

def test_file_operations():
    """Test file operations and cleanup"""
    print("\n=== TESTING FILE OPERATIONS ===")
    
    try:
        downloader = GreatLearningDownloader("temp_downloads")
        
        # Test cleanup (should work even with no files)
        cleanup_results = downloader.cleanup_downloads(older_than_hours=1)
        print(f"✅ Cleanup test: {cleanup_results}")
        
        # Test download directory creation
        download_dir = Path("temp_downloads")
        if download_dir.exists():
            print("✅ Download directory exists")
        else:
            print("❌ Download directory not created")
        
        downloader.close()
        
    except Exception as e:
        print(f"❌ File operations test: FAILED - {e}")

def main():
    """Run all tests"""
    print("🚀 STARTING WEB SCRAPING MODULE TESTS")
    print("=" * 50)
    
    # Run tests
    test_basic_functionality()
    test_great_learning_downloader()
    test_file_operations()
    
    print("\n" + "=" * 50)
    print("✅ WEB SCRAPING TESTS COMPLETED")
    print("\nNote: Some tests may show warnings if login fails or content is not accessible.")
    print("This is normal during development and testing phases.")

if __name__ == "__main__":
    main()
