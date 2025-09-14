"""
Web Scraping Module for Advanced MCP Server
Handles authenticated website scraping with rate limiting and error handling
"""

import os
import time
import logging
import requests
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple
import re

# Configure logging
logger = logging.getLogger(__name__)

class WebScraper:
    """Base web scraper with authentication and rate limiting"""
    
    def __init__(self, base_url: str, download_dir: str = "temp_downloads"):
        self.base_url = base_url
        self.download_dir = Path(download_dir)
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # Minimum seconds between requests
        
        # Create download directory
        self.download_dir.mkdir(exist_ok=True)
        
        # Set up user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logger.info(f"WebScraper initialized with base URL: {base_url}")
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def login(self, username: str, password: str, login_url: str = None) -> bool:
        """
        Generic login method - to be overridden by specific implementations
        """
        raise NotImplementedError("Login method must be implemented by subclass")
    
    def get_page(self, url: str) -> requests.Response:
        """Get a page with rate limiting and error handling"""
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def download_file(self, file_url: str, local_path: str = None, 
                     progress_callback=None) -> str:
        """Download a file with progress tracking"""
        self._rate_limit()
        
        try:
            response = self.session.get(file_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Determine filename if not provided
            if not local_path:
                filename = self._extract_filename(file_url, response)
                local_path = self.download_dir / filename
            else:
                local_path = Path(local_path)
            
            # Ensure directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, downloaded, total_size)
            
            logger.info(f"Downloaded: {file_url} -> {local_path}")
            return str(local_path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading {file_url}: {str(e)}")
            raise
    
    def _extract_filename(self, url: str, response: requests.Response) -> str:
        """Extract filename from URL or response headers"""
        # Try Content-Disposition header first
        if 'content-disposition' in response.headers:
            disposition = response.headers['content-disposition']
            filename_match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', disposition)
            if filename_match:
                return unquote(filename_match.group(1))
        
        # Fall back to URL path
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename in path, use timestamp
        if not filename or '.' not in filename:
            timestamp = int(time.time())
            extension = self._guess_extension(response.headers.get('content-type', ''))
            filename = f"download_{timestamp}{extension}"
        
        return filename
    
    def _guess_extension(self, content_type: str) -> str:
        """Guess file extension from content type"""
        extensions = {
            'video/mp4': '.mp4',
            'video/avi': '.avi',
            'video/quicktime': '.mov',
            'video/x-msvideo': '.avi',
            'application/pdf': '.pdf',
            'text/html': '.html',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'application/zip': '.zip',
            'application/json': '.json'
        }
        return extensions.get(content_type, '.bin')
    
    def get_download_stats(self) -> Dict:
        """Get statistics about downloaded files"""
        if not self.download_dir.exists():
            return {"total_files": 0, "total_size": 0, "files": []}
        
        files = []
        total_size = 0
        
        for file_path in self.download_dir.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": size,
                    "modified": file_path.stat().st_mtime
                })
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": files
        }
    
    def cleanup_downloads(self, older_than_hours: int = 24) -> Dict:
        """Clean up old downloaded files"""
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        deleted_files = []
        total_freed = 0
        
        if self.download_dir.exists():
            for file_path in self.download_dir.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        deleted_files.append(str(file_path))
                        total_freed += size
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")
        
        return {
            "deleted_files": len(deleted_files),
            "files": deleted_files,
            "total_freed_bytes": total_freed,
            "total_freed_mb": round(total_freed / (1024 * 1024), 2)
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("WebScraper session closed")

class ScrapingError(Exception):
    """Custom exception for scraping-related errors"""
    pass
