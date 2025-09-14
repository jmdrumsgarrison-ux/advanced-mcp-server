"""
Great Learning Course Downloader
Specialized scraper for olympus.mygreatlearning.com platform
"""

import os
import re
import time
import logging
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import requests

from web_scraper import WebScraper, ScrapingError

logger = logging.getLogger(__name__)

class GreatLearningDownloader(WebScraper):
    """Specialized downloader for Great Learning courses"""
    
    def __init__(self, download_dir: str = "temp_downloads"):
        super().__init__("https://olympus.mygreatlearning.com", download_dir)
        self.course_data = {}
        self.is_authenticated = False
        
        # Great Learning specific endpoints
        self.login_url = "https://olympus.mygreatlearning.com/sign-in"
        self.courses_url = "https://olympus.mygreatlearning.com/courses"
        
        logger.info("GreatLearningDownloader initialized")
    
    def login(self, username: str, password: str) -> bool:
        """Login to Great Learning platform"""
        try:
            # Get login page to extract any CSRF tokens
            login_page = self.get_page(self.login_url)
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Look for CSRF token or other hidden fields
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'}) or soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Prepare login data
            login_data = {
                'email': username,
                'password': password
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Attempt login
            self._rate_limit()
            response = self.session.post(
                self.login_url,
                data=login_data,
                allow_redirects=True,
                timeout=30
            )
            
            # Check if login was successful
            if response.status_code == 200:
                # Look for signs of successful login
                if 'dashboard' in response.url.lower() or 'courses' in response.url.lower():
                    self.is_authenticated = True
                    logger.info("Successfully logged into Great Learning")
                    return True
                elif 'sign-in' in response.url.lower():
                    # Still on login page - likely failed
                    logger.error("Login failed - redirected back to sign-in page")
                    return False
            
            # Check response content for error messages
            soup = BeautifulSoup(response.content, 'html.parser')
            error_elements = soup.find_all(['div', 'span'], class_=re.compile(r'error|alert|warning', re.I))
            
            if error_elements:
                error_msg = ' '.join([elem.get_text().strip() for elem in error_elements])
                logger.error(f"Login error: {error_msg}")
                return False
            
            # If we get here, assume success if no obvious errors
            self.is_authenticated = True
            logger.info("Login appears successful")
            return True
            
        except Exception as e:
            logger.error(f"Login failed with exception: {str(e)}")
            return False
    
    def get_course_info(self, course_id: str) -> Dict:
        """Get detailed information about a specific course"""
        if not self.is_authenticated:
            raise ScrapingError("Must be logged in to access course information")
        
        course_url = f"{self.courses_url}?pb_id={course_id}"
        
        try:
            response = self.get_page(course_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract course information
            course_info = {
                'id': course_id,
                'url': course_url,
                'title': self._extract_course_title(soup),
                'description': self._extract_course_description(soup),
                'modules': self._extract_course_modules(soup),
                'resources': self._extract_course_resources(soup)
            }
            
            self.course_data[course_id] = course_info
            logger.info(f"Extracted info for course {course_id}: {course_info['title']}")
            
            return course_info
            
        except Exception as e:
            logger.error(f"Error getting course info for {course_id}: {str(e)}")
            raise ScrapingError(f"Failed to get course information: {str(e)}")
    
    def _extract_course_title(self, soup: BeautifulSoup) -> str:
        """Extract course title from page"""
        # Try various selectors for course title
        selectors = [
            'h1.course-title',
            'h1.title',
            '.course-header h1',
            'h1',
            '.page-title'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        return "Unknown Course"
    
    def _extract_course_description(self, soup: BeautifulSoup) -> str:
        """Extract course description"""
        selectors = [
            '.course-description',
            '.description',
            '.course-overview',
            '.summary'
        ]
        
        for selector in selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()
        
        return ""
    
    def _extract_course_modules(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract course modules/sections"""
        modules = []
        
        # Look for module containers
        module_selectors = [
            '.module',
            '.chapter',
            '.section',
            '.lesson-group',
            '.curriculum-section'
        ]
        
        for selector in module_selectors:
            module_elements = soup.select(selector)
            if module_elements:
                for i, module_elem in enumerate(module_elements):
                    module_info = {
                        'index': i,
                        'title': self._extract_module_title(module_elem),
                        'lessons': self._extract_module_lessons(module_elem)
                    }
                    modules.append(module_info)
                break
        
        return modules
    
    def _extract_module_title(self, module_elem) -> str:
        """Extract module title"""
        title_selectors = [
            '.module-title',
            '.chapter-title',
            '.section-title',
            'h2', 'h3', 'h4'
        ]
        
        for selector in title_selectors:
            title_elem = module_elem.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        return f"Module {module_elem}"
    
    def _extract_module_lessons(self, module_elem) -> List[Dict]:
        """Extract lessons from a module"""
        lessons = []
        
        lesson_selectors = [
            '.lesson',
            '.video',
            '.content-item',
            '.curriculum-item'
        ]
        
        for selector in lesson_selectors:
            lesson_elements = module_elem.select(selector)
            if lesson_elements:
                for i, lesson_elem in enumerate(lesson_elements):
                    lesson_info = {
                        'index': i,
                        'title': self._extract_lesson_title(lesson_elem),
                        'type': self._extract_lesson_type(lesson_elem),
                        'url': self._extract_lesson_url(lesson_elem)
                    }
                    lessons.append(lesson_info)
                break
        
        return lessons
    
    def _extract_lesson_title(self, lesson_elem) -> str:
        """Extract lesson title"""
        title_selectors = [
            '.lesson-title',
            '.video-title',
            '.title',
            'a',
            'span'
        ]
        
        for selector in title_selectors:
            title_elem = lesson_elem.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        return "Unknown Lesson"
    
    def _extract_lesson_type(self, lesson_elem) -> str:
        """Determine lesson type (video, pdf, etc.)"""
        # Look for type indicators
        if lesson_elem.select('.video, .mp4, [data-type="video"]'):
            return 'video'
        elif lesson_elem.select('.pdf, [data-type="pdf"]'):
            return 'pdf'
        elif lesson_elem.select('.quiz, [data-type="quiz"]'):
            return 'quiz'
        else:
            return 'unknown'
    
    def _extract_lesson_url(self, lesson_elem) -> str:
        """Extract lesson URL"""
        link_elem = lesson_elem.select_one('a[href]')
        if link_elem:
            href = link_elem.get('href')
            if href:
                return urljoin(self.base_url, href)
        return ""
    
    def _extract_course_resources(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract downloadable resources"""
        resources = []
        
        # Look for download links
        download_selectors = [
            'a[href*=".pdf"]',
            'a[href*=".mp4"]',
            'a[href*=".avi"]',
            'a[href*=".mov"]',
            'a[href*="download"]',
            '.download-link',
            '.resource-link'
        ]
        
        for selector in download_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    resource_info = {
                        'title': link.get_text().strip() or link.get('title', 'Resource'),
                        'url': urljoin(self.base_url, href),
                        'type': self._guess_resource_type(href)
                    }
                    resources.append(resource_info)
        
        return resources
    
    def _guess_resource_type(self, url: str) -> str:
        """Guess resource type from URL"""
        url_lower = url.lower()
        if '.pdf' in url_lower:
            return 'pdf'
        elif any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.wmv']):
            return 'video'
        elif any(ext in url_lower for ext in ['.jpg', '.png', '.gif']):
            return 'image'
        elif '.zip' in url_lower:
            return 'archive'
        else:
            return 'unknown'
    
    def download_course(self, course_id: str, include_videos: bool = True, 
                       include_pdfs: bool = True) -> Dict:
        """Download all content from a course"""
        if not self.is_authenticated:
            raise ScrapingError("Must be logged in to download course content")
        
        # Get course information first
        course_info = self.get_course_info(course_id)
        
        # Create course directory
        course_dir = self.download_dir / f"course_{course_id}"
        course_dir.mkdir(exist_ok=True)
        
        download_results = {
            'course_id': course_id,
            'course_title': course_info['title'],
            'downloaded_files': [],
            'failed_downloads': [],
            'total_size': 0
        }
        
        # Download resources
        for resource in course_info['resources']:
            if not include_videos and resource['type'] == 'video':
                continue
            if not include_pdfs and resource['type'] == 'pdf':
                continue
            
            try:
                filename = self._sanitize_filename(resource['title'])
                local_path = course_dir / filename
                
                downloaded_path = self.download_file(resource['url'], local_path)
                file_size = Path(downloaded_path).stat().st_size
                
                download_results['downloaded_files'].append({
                    'title': resource['title'],
                    'url': resource['url'],
                    'local_path': downloaded_path,
                    'size': file_size
                })
                download_results['total_size'] += file_size
                
                logger.info(f"Downloaded: {resource['title']}")
                
            except Exception as e:
                error_info = {
                    'title': resource['title'],
                    'url': resource['url'],
                    'error': str(e)
                }
                download_results['failed_downloads'].append(error_info)
                logger.error(f"Failed to download {resource['title']}: {str(e)}")
        
        # Save course metadata
        metadata_file = course_dir / "course_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'course_info': course_info,
                'download_results': download_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Course download completed: {len(download_results['downloaded_files'])} files, "
                   f"{download_results['total_size']} bytes")
        
        return download_results
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows filesystem"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()
    
    def get_available_courses(self) -> List[Dict]:
        """Get list of available courses for the user"""
        if not self.is_authenticated:
            raise ScrapingError("Must be logged in to get available courses")
        
        try:
            response = self.get_page(self.courses_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            courses = []
            
            # Look for course cards/links
            course_selectors = [
                '.course-card',
                '.course-item',
                'a[href*="courses?pb_id="]',
                'a[href*="course"]'
            ]
            
            for selector in course_selectors:
                course_elements = soup.select(selector)
                if course_elements:
                    for course_elem in course_elements:
                        course_info = self._extract_course_card_info(course_elem)
                        if course_info:
                            courses.append(course_info)
                    break
            
            logger.info(f"Found {len(courses)} available courses")
            return courses
            
        except Exception as e:
            logger.error(f"Error getting available courses: {str(e)}")
            raise ScrapingError(f"Failed to get available courses: {str(e)}")
    
    def _extract_course_card_info(self, course_elem) -> Optional[Dict]:
        """Extract course information from course card element"""
        # Try to extract course ID from href
        link_elem = course_elem.select_one('a[href]') or course_elem
        if not link_elem or not link_elem.get('href'):
            return None
        
        href = link_elem.get('href')
        course_id_match = re.search(r'pb_id=(\d+)', href)
        if not course_id_match:
            return None
        
        course_id = course_id_match.group(1)
        
        # Extract title
        title_elem = course_elem.select_one('.title, .course-title, h3, h4') or link_elem
        title = title_elem.get_text().strip() if title_elem else f"Course {course_id}"
        
        return {
            'id': course_id,
            'title': title,
            'url': urljoin(self.base_url, href)
        }
