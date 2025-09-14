"""
Modern Content Acquisition System
Uses open source tools: Crawl4AI + yt-dlp for educational content scraping
"""

import os
import json
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from urllib.parse import urljoin, urlparse
import tempfile

# Modern scraping imports
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai import JsonCssExtractionStrategy, LLMExtractionStrategy
    import yt_dlp
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import requests
except ImportError as e:
    print(f"Modern content acquisition dependencies not installed: {e}")
    print("Run: pip install -r requirements_modern.txt")

class ModernContentAcquisition:
    """
    Modern content acquisition using proven open source tools
    - Crawl4AI for web scraping
    - yt-dlp for video downloads
    - Extensible architecture for multiple platforms
    """
    
    def __init__(self, download_dir: str = None):
        """Initialize the modern content acquisition system"""
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloaded_content")
        self.logger = self._setup_logging()
        
        # Create download directory structure
        self.video_dir = os.path.join(self.download_dir, "videos")
        self.document_dir = os.path.join(self.download_dir, "documents") 
        self.metadata_dir = os.path.join(self.download_dir, "metadata")
        
        for directory in [self.video_dir, self.document_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize scrapers
        self.crawl4ai_config = None
        self.yt_dlp_config = None
        self._setup_tools()
        
        # Statistics
        self.stats = {
            'courses_processed': 0,
            'videos_downloaded': 0,
            'documents_downloaded': 0,
            'total_size_mb': 0,
            'errors': 0,
            'last_activity': None
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for content acquisition"""
        logger = logging.getLogger('ModernContentAcquisition')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_tools(self):
        """Setup Crawl4AI and yt-dlp configurations"""
        # Crawl4AI browser configuration (v0.7.4 compatible)
        self.crawl4ai_config = BrowserConfig(
            headless=True,  # Set to False for debugging
            viewport_width=1920,
            viewport_height=1080
            # Removed unsupported parameters:
            # wait_for_images (not supported in v0.7.4)
            # accept_downloads (not supported in v0.7.4)
            # user_agent (may need different syntax in v0.7.4)
        )
        
        # yt-dlp configuration
        self.yt_dlp_config = {
            'format': 'best[height<=720]',  # Good quality, reasonable size
            'outtmpl': os.path.join(self.video_dir, '%(title)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'ignoreerrors': True,
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': True,
            'writeinfojson': True,
        }
        
        self.logger.info("Modern content acquisition tools configured")
    
    async def scrape_great_learning_course(self, course_url: str, 
                                         credentials: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Scrape a Great Learning course using modern tools
        
        Args:
            course_url: URL of the course to scrape
            credentials: Login credentials {username, password}
            
        Returns:
            Dictionary containing course information and download results
        """
        try:
            self.logger.info(f"🎓 Starting Great Learning course scrape: {course_url}")
            start_time = time.time()
            
            results = {
                'course_url': course_url,
                'success': False,
                'course_info': {},
                'videos': [],
                'documents': [],
                'errors': []
            }
            
            # Step 1: Extract course structure using Crawl4AI
            self.logger.info("📊 Extracting course structure...")
            course_structure = await self._extract_course_structure(course_url, credentials)
            results['course_info'] = course_structure
            
            if not course_structure.get('success', False):
                results['errors'].append("Failed to extract course structure")
                return results
            
            # Step 2: Download videos using yt-dlp where possible
            self.logger.info("🎬 Downloading videos...")
            if course_structure.get('video_urls'):
                video_results = await self._download_videos(course_structure['video_urls'])
                results['videos'] = video_results
            
            # Step 3: Download documents and other resources
            self.logger.info("📄 Downloading documents...")
            if course_structure.get('document_urls'):
                doc_results = await self._download_documents(course_structure['document_urls'])
                results['documents'] = doc_results
            
            # Step 4: Save metadata
            self.logger.info("💾 Saving metadata...")
            metadata_file = os.path.join(self.metadata_dir, f"course_{int(time.time())}.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Update statistics
            processing_time = time.time() - start_time
            results['processing_time'] = processing_time
            results['success'] = True
            
            self.stats['courses_processed'] += 1
            self.stats['videos_downloaded'] += len(results['videos'])
            self.stats['documents_downloaded'] += len(results['documents'])
            self.stats['last_activity'] = time.time()
            
            self.logger.info(f"✅ Course scraping complete in {processing_time:.2f}s")
            return results
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"❌ Course scraping failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    async def _extract_course_structure(self, course_url: str, 
                                      credentials: Dict[str, str] = None) -> Dict[str, Any]:
        """Extract course structure using Crawl4AI"""
        try:
            # Create extraction strategy for Great Learning
            extraction_schema = {
                "name": "Great Learning Course",
                "baseSelector": "div",  # Will refine based on actual site structure
                "fields": [
                    {
                        "name": "course_title",
                        "selector": "h1, .course-title, .title",
                        "type": "text"
                    },
                    {
                        "name": "course_description", 
                        "selector": ".description, .course-description, .summary",
                        "type": "text"
                    },
                    {
                        "name": "video_links",
                        "selector": "a[href*='video'], iframe[src*='video'], video source",
                        "type": "attribute",
                        "attribute": "href"
                    },
                    {
                        "name": "document_links",
                        "selector": "a[href*='.pdf'], a[href*='.doc'], a[href*='.ppt']",
                        "type": "attribute", 
                        "attribute": "href"
                    },
                    {
                        "name": "modules",
                        "selector": ".module, .chapter, .lesson",
                        "type": "text"
                    }
                ]
            }
            
            extraction_strategy = JsonCssExtractionStrategy(extraction_schema, verbose=True)
            
            # Configure crawler with authentication if provided
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                js_code=self._get_auth_js_code(credentials) if credentials else None,
                wait_for="networkidle",
                page_timeout=30000,
                delay_before_return_html=3000
            )
            
            # Run crawl
            async with AsyncWebCrawler(config=self.crawl4ai_config) as crawler:
                result = await crawler.arun(
                    url=course_url,
                    config=run_config
                )
                
                if result.success:
                    # Parse extracted data
                    extracted_data = json.loads(result.extracted_content)
                    
                    # Process and clean the data
                    course_info = {
                        'success': True,
                        'title': extracted_data.get('course_title', 'Unknown Course'),
                        'description': extracted_data.get('course_description', ''),
                        'modules': extracted_data.get('modules', []),
                        'video_urls': self._clean_urls(extracted_data.get('video_links', []), course_url),
                        'document_urls': self._clean_urls(extracted_data.get('document_links', []), course_url),
                        'raw_html': result.html[:1000] if result.html else "",  # First 1000 chars for debugging
                        'extraction_time': time.time()
                    }
                    
                    self.logger.info(f"✅ Extracted course: {course_info['title']}")
                    return course_info
                else:
                    return {
                        'success': False,
                        'error': f"Crawl4AI failed: {result.error_message}",
                        'video_urls': [],
                        'document_urls': []
                    }
                    
        except Exception as e:
            self.logger.error(f"Course structure extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'video_urls': [],
                'document_urls': []
            }
    
    def _get_auth_js_code(self, credentials: Dict[str, str]) -> List[str]:
        """Generate JavaScript code for authentication"""
        if not credentials:
            return []
        
        # JavaScript to handle Great Learning login
        js_code = [
            """
            // Great Learning authentication
            (async () => {
                // Look for login form
                const emailInput = document.querySelector('input[type="email"], input[name="email"], input[placeholder*="email"]');
                const passwordInput = document.querySelector('input[type="password"], input[name="password"]');
                const loginButton = document.querySelector('button[type="submit"], input[type="submit"], .login-btn, .sign-in-btn');
                
                if (emailInput && passwordInput && loginButton) {
                    emailInput.value = '%s';
                    passwordInput.value = '%s';
                    
                    // Wait a bit then click login
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    loginButton.click();
                    
                    // Wait for login to complete
                    await new Promise(resolve => setTimeout(resolve, 5000));
                }
            })();
            """ % (credentials.get('username', ''), credentials.get('password', ''))
        ]
        
        return js_code
    
    def _clean_urls(self, urls: List[str], base_url: str) -> List[str]:
        """Clean and normalize URLs"""
        cleaned_urls = []
        base_domain = urlparse(base_url).netloc
        
        for url in urls:
            if not url:
                continue
                
            # Convert relative URLs to absolute
            if url.startswith('/'):
                url = urljoin(base_url, url)
            elif not url.startswith('http'):
                url = urljoin(base_url, url)
            
            # Filter out invalid URLs
            if url and len(url) > 10 and ('video' in url.lower() or 'stream' in url.lower() or base_domain in url):
                cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Remove duplicates
    
    async def _download_videos(self, video_urls: List[str]) -> List[Dict[str, Any]]:
        """Download videos using yt-dlp"""
        video_results = []
        
        for url in video_urls:
            try:
                self.logger.info(f"🎬 Downloading video: {url}")
                
                # Configure yt-dlp for this specific download
                ydl_opts = self.yt_dlp_config.copy()
                ydl_opts['outtmpl'] = os.path.join(
                    self.video_dir, 
                    f"video_{int(time.time())}_{len(video_results)}.%(ext)s"
                )
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract info first
                    info = ydl.extract_info(url, download=False)
                    
                    if info:
                        # Download the video
                        ydl.download([url])
                        
                        video_result = {
                            'url': url,
                            'title': info.get('title', 'Unknown'),
                            'duration': info.get('duration', 0),
                            'format': info.get('ext', 'unknown'),
                            'filesize': info.get('filesize', 0),
                            'success': True,
                            'download_time': time.time()
                        }
                        
                        video_results.append(video_result)
                        self.logger.info(f"✅ Video downloaded: {video_result['title']}")
                
            except Exception as e:
                self.logger.error(f"❌ Video download failed for {url}: {e}")
                video_results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return video_results
    
    async def _download_documents(self, document_urls: List[str]) -> List[Dict[str, Any]]:
        """Download documents using requests"""
        document_results = []
        
        for url in document_urls:
            try:
                self.logger.info(f"📄 Downloading document: {url}")
                
                # Make request with appropriate headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()
                
                # Determine filename
                filename = os.path.basename(urlparse(url).path)
                if not filename or '.' not in filename:
                    # Use content-disposition header if available
                    content_disposition = response.headers.get('content-disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"\'')
                    else:
                        filename = f"document_{int(time.time())}_{len(document_results)}.pdf"
                
                file_path = os.path.join(self.document_dir, filename)
                
                # Download file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(file_path)
                
                document_result = {
                    'url': url,
                    'filename': filename,
                    'file_path': file_path,
                    'size_bytes': file_size,
                    'success': True,
                    'download_time': time.time()
                }
                
                document_results.append(document_result)
                self.logger.info(f"✅ Document downloaded: {filename}")
                
            except Exception as e:
                self.logger.error(f"❌ Document download failed for {url}: {e}")
                document_results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return document_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get content acquisition statistics"""
        return {
            'courses_processed': self.stats['courses_processed'],
            'videos_downloaded': self.stats['videos_downloaded'],
            'documents_downloaded': self.stats['documents_downloaded'],
            'total_size_mb': self.stats['total_size_mb'],
            'errors': self.stats['errors'],
            'last_activity': self.stats['last_activity'],
            'download_directories': {
                'videos': self.video_dir,
                'documents': self.document_dir,
                'metadata': self.metadata_dir
            },
            'tools_status': {
                'crawl4ai_configured': self.crawl4ai_config is not None,
                'yt_dlp_configured': self.yt_dlp_config is not None
            }
        }
    
    def cleanup_old_downloads(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Clean up old downloaded files"""
        try:
            cutoff_time = time.time() - (older_than_hours * 3600)
            removed_files = []
            total_size_freed = 0
            
            for directory in [self.video_dir, self.document_dir, self.metadata_dir]:
                if os.path.exists(directory):
                    for file_path in Path(directory).rglob('*'):
                        if file_path.is_file():
                            try:
                                file_stat = file_path.stat()
                                if file_stat.st_mtime < cutoff_time:
                                    file_size = file_stat.st_size
                                    file_path.unlink()
                                    removed_files.append(str(file_path))
                                    total_size_freed += file_size
                            except Exception as e:
                                self.logger.warning(f"Could not remove file {file_path}: {e}")
            
            self.logger.info(f"Cleanup complete: {len(removed_files)} files removed")
            
            return {
                'files_removed': len(removed_files),
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2),
                'older_than_hours': older_than_hours,
                'removed_files': removed_files
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return {'error': str(e)}


# Example usage and testing
async def test_great_learning():
    """Test function for Great Learning course scraping"""
    # Initialize the system
    content_acquisition = ModernContentAcquisition("test_downloads")
    
    # Load credentials (same format as before)
    credentials = {
        'username': 'j@4morr.com',
        'password': 'Vault2011$'
    }
    
    # Test course URL (replace with actual course)
    test_course_url = "https://olympus.mygreatlearning.com/courses/some-course"
    
    # Scrape the course
    results = await content_acquisition.scrape_great_learning_course(
        test_course_url, 
        credentials
    )
    
    print("Content Acquisition Results:")
    print(json.dumps(results, indent=2))
    
    # Print statistics
    stats = content_acquisition.get_stats()
    print("\nStatistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_great_learning())
