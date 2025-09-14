"""
Video Processor Module for Advanced MCP Server
Handles video analysis, content extraction, and instruction parsing
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess
import tempfile
import shutil

# Video processing imports will be installed
try:
    import cv2
    import moviepy.editor as mp
    from moviepy.video.io.VideoFileClip import VideoFileClip
    import speech_recognition as sr
    import whisper
    import numpy as np
except ImportError as e:
    print(f"Video processing dependencies not installed: {e}")
    print("Run: pip install opencv-python moviepy SpeechRecognition whisper-openai")

class VideoProcessor:
    """
    Base class for video processing operations including:
    - Video file analysis and metadata extraction
    - Audio extraction and transcription
    - Frame analysis and content detection
    - Instruction identification and parsing
    """
    
    def __init__(self, temp_dir: str = None, cleanup_older_than_hours: int = 24):
        """Initialize VideoProcessor with configuration"""
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp_video_processing")
        self.cleanup_older_than_hours = cleanup_older_than_hours
        self.logger = self._setup_logging()
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize Whisper model for transcription
        try:
            self.whisper_model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Statistics
        self.stats = {
            'videos_processed': 0,
            'total_duration_seconds': 0,
            'instructions_extracted': 0,
            'errors': 0,
            'last_processing_time': None
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for video processing operations"""
        logger = logging.getLogger('VideoProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def analyze_video_file(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze a video file and extract comprehensive metadata
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video analysis results
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.logger.info(f"Analyzing video: {video_path}")
            
            # Get basic file information
            file_stats = os.stat(video_path)
            file_size_mb = file_stats.st_size / (1024 * 1024)
            
            analysis_result = {
                'file_path': video_path,
                'file_name': os.path.basename(video_path),
                'file_size_mb': round(file_size_mb, 2),
                'created_time': time.ctime(file_stats.st_ctime),
                'modified_time': time.ctime(file_stats.st_mtime),
                'processing_time': time.time()
            }
            
            # Use OpenCV for video analysis
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Could not open video file with OpenCV")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_seconds = frame_count / fps if fps > 0 else 0
            
            analysis_result.update({
                'duration_seconds': round(duration_seconds, 2),
                'duration_formatted': self._format_duration(duration_seconds),
                'fps': round(fps, 2),
                'frame_count': frame_count,
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height,
                'aspect_ratio': round(width / height, 2) if height > 0 else 0
            })
            
            # Sample frames for content analysis
            frame_samples = self._sample_frames(cap, num_samples=5)
            analysis_result['frame_samples'] = len(frame_samples)
            
            cap.release()
            
            # Try to get additional metadata with moviepy
            try:
                clip = VideoFileClip(video_path)
                analysis_result.update({
                    'has_audio': clip.audio is not None,
                    'audio_duration': clip.audio.duration if clip.audio else 0,
                    'video_codec': getattr(clip, 'codec', 'unknown'),
                })
                clip.close()
            except Exception as e:
                self.logger.warning(f"MoviePy analysis failed: {e}")
                analysis_result['has_audio'] = False
            
            # Update statistics
            self.stats['videos_processed'] += 1
            self.stats['total_duration_seconds'] += duration_seconds
            self.stats['last_processing_time'] = time.time()
            
            self.logger.info(f"Video analysis complete: {duration_seconds:.2f}s duration")
            return analysis_result
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Video analysis failed: {e}")
            raise
    
    def extract_audio_and_transcribe(self, video_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Extract audio from video and generate transcription
        
        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted audio (optional)
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.logger.info(f"Extracting audio and transcribing: {video_path}")
            
            # Prepare output directory
            if output_dir is None:
                output_dir = self.temp_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate audio file path
            video_name = Path(video_path).stem
            audio_path = os.path.join(output_dir, f"{video_name}_audio.wav")
            
            # Extract audio using moviepy
            try:
                clip = VideoFileClip(video_path)
                if clip.audio is None:
                    return {
                        'success': False,
                        'error': 'Video has no audio track',
                        'transcription': '',
                        'audio_path': None
                    }
                
                # Extract audio
                clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                clip.close()
                
                self.logger.info(f"Audio extracted to: {audio_path}")
                
            except Exception as e:
                self.logger.error(f"Audio extraction failed: {e}")
                return {
                    'success': False,
                    'error': f'Audio extraction failed: {str(e)}',
                    'transcription': '',
                    'audio_path': None
                }
            
            # Transcribe using Whisper
            transcription_result = self._transcribe_audio(audio_path)
            
            # Combine results
            result = {
                'success': True,
                'audio_path': audio_path,
                'video_path': video_path,
                'transcription': transcription_result.get('text', ''),
                'transcription_segments': transcription_result.get('segments', []),
                'language': transcription_result.get('language', 'unknown'),
                'confidence': transcription_result.get('confidence', 0),
                'processing_time': time.time()
            }
            
            self.logger.info(f"Transcription complete: {len(result['transcription'])} characters")
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Audio extraction and transcription failed: {e}")
            raise
    
    def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        try:
            if self.whisper_model is None:
                raise ValueError("Whisper model not available")
            
            self.logger.info(f"Transcribing audio: {audio_path}")
            
            # Use Whisper for transcription
            result = self.whisper_model.transcribe(audio_path)
            
            return {
                'text': result.get('text', ''),
                'segments': result.get('segments', []),
                'language': result.get('language', 'unknown'),
                'confidence': self._calculate_confidence(result.get('segments', []))
            }
            
        except Exception as e:
            self.logger.warning(f"Whisper transcription failed, trying speech_recognition: {e}")
            
            # Fallback to speech_recognition
            try:
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio)
                    
                return {
                    'text': text,
                    'segments': [],
                    'language': 'unknown',
                    'confidence': 0.5  # Default confidence for Google API
                }
            except Exception as fallback_error:
                self.logger.error(f"All transcription methods failed: {fallback_error}")
                return {
                    'text': '',
                    'segments': [],
                    'language': 'unknown',
                    'confidence': 0
                }
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """Calculate average confidence from Whisper segments"""
        if not segments:
            return 0
        
        confidences = []
        for segment in segments:
            if 'avg_logprob' in segment:
                # Convert log probability to confidence score
                confidence = np.exp(segment['avg_logprob'])
                confidences.append(confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0
    
    def _sample_frames(self, cap, num_samples: int = 5) -> List[np.ndarray]:
        """Sample frames from video for content analysis"""
        frames = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if frame_count == 0:
            return frames
        
        # Calculate frame indices to sample
        indices = [int(i * frame_count / num_samples) for i in range(num_samples)]
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        return frames
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def find_video_files(self, directory: str, extensions: List[str] = None) -> List[str]:
        """
        Find all video files in a directory and subdirectories
        
        Args:
            directory: Directory to search
            extensions: List of video file extensions to look for
            
        Returns:
            List of video file paths
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        
        video_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        video_files.append(os.path.join(root, file))
            
            self.logger.info(f"Found {len(video_files)} video files in {directory}")
            return video_files
            
        except Exception as e:
            self.logger.error(f"Error finding video files: {e}")
            return []
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            'videos_processed': self.stats['videos_processed'],
            'total_duration_seconds': self.stats['total_duration_seconds'],
            'total_duration_formatted': self._format_duration(self.stats['total_duration_seconds']),
            'instructions_extracted': self.stats['instructions_extracted'],
            'errors': self.stats['errors'],
            'last_processing_time': self.stats['last_processing_time'],
            'temp_directory': self.temp_dir,
            'whisper_available': self.whisper_model is not None
        }
    
    def cleanup_temp_files(self, older_than_hours: int = None) -> Dict[str, Any]:
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Remove files older than this many hours
            
        Returns:
            Dictionary with cleanup results
        """
        if older_than_hours is None:
            older_than_hours = self.cleanup_older_than_hours
        
        try:
            cutoff_time = time.time() - (older_than_hours * 3600)
            removed_files = []
            total_size_freed = 0
            
            if os.path.exists(self.temp_dir):
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_stat = os.stat(file_path)
                            if file_stat.st_mtime < cutoff_time:
                                file_size = file_stat.st_size
                                os.remove(file_path)
                                removed_files.append(file)
                                total_size_freed += file_size
                        except Exception as e:
                            self.logger.warning(f"Could not remove file {file_path}: {e}")
            
            self.logger.info(f"Cleanup complete: {len(removed_files)} files removed")
            
            return {
                'files_removed': len(removed_files),
                'files_list': removed_files,
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2),
                'older_than_hours': older_than_hours,
                'temp_directory': self.temp_dir
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            raise


class InstructionExtractor:
    """
    Specialized class for extracting actionable instructions from video transcriptions
    """
    
    def __init__(self):
        self.logger = logging.getLogger('InstructionExtractor')
        
        # Keywords that indicate instructional content
        self.instruction_keywords = [
            'create', 'build', 'make', 'develop', 'implement', 'code', 'write',
            'add', 'install', 'setup', 'configure', 'initialize', 'define',
            'import', 'export', 'save', 'load', 'run', 'execute', 'test',
            'debug', 'fix', 'update', 'modify', 'change', 'edit', 'delete',
            'copy', 'paste', 'move', 'rename', 'organize', 'structure',
            'function', 'class', 'method', 'variable', 'parameter', 'return',
            'if', 'else', 'for', 'while', 'try', 'except', 'with', 'import'
        ]
        
        # Patterns for code-related instructions
        self.code_patterns = [
            r'def\s+\w+\s*\(',
            r'class\s+\w+\s*:',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'pip\s+install',
            r'npm\s+install',
            r'git\s+\w+',
            r'docker\s+\w+',
        ]
    
    def extract_instructions(self, transcription: str, video_info: Dict = None) -> Dict[str, Any]:
        """
        Extract actionable instructions from video transcription
        
        Args:
            transcription: Text transcription of the video
            video_info: Optional video metadata for context
            
        Returns:
            Dictionary containing extracted instructions and analysis
        """
        try:
            if not transcription.strip():
                return {
                    'instructions': [],
                    'instruction_count': 0,
                    'confidence': 0,
                    'categories': [],
                    'code_snippets': [],
                    'error': 'Empty transcription'
                }
            
            self.logger.info("Extracting instructions from transcription")
            
            # Split transcription into sentences
            sentences = self._split_into_sentences(transcription)
            
            # Identify instructional sentences
            instructions = []
            code_snippets = []
            categories = set()
            
            for sentence in sentences:
                instruction_info = self._analyze_sentence(sentence)
                if instruction_info['is_instruction']:
                    instructions.append(instruction_info)
                    categories.update(instruction_info['categories'])
                
                # Extract code snippets
                code_in_sentence = self._extract_code_snippets(sentence)
                code_snippets.extend(code_in_sentence)
            
            # Calculate overall confidence
            confidence = self._calculate_instruction_confidence(instructions)
            
            result = {
                'instructions': instructions,
                'instruction_count': len(instructions),
                'confidence': confidence,
                'categories': list(categories),
                'code_snippets': code_snippets,
                'total_sentences': len(sentences),
                'instructional_ratio': len(instructions) / len(sentences) if sentences else 0,
                'video_info': video_info or {},
                'processing_time': time.time()
            }
            
            self.logger.info(f"Extracted {len(instructions)} instructions with {confidence:.2f} confidence")
            return result
            
        except Exception as e:
            self.logger.error(f"Instruction extraction failed: {e}")
            raise
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze a sentence to determine if it contains instructions"""
        sentence_lower = sentence.lower()
        
        # Check for instruction keywords
        keyword_count = sum(1 for keyword in self.instruction_keywords 
                          if keyword in sentence_lower)
        
        # Check for imperative mood (starts with action verb)
        starts_with_action = any(sentence_lower.strip().startswith(keyword) 
                               for keyword in self.instruction_keywords)
        
        # Determine categories
        categories = []
        if any(word in sentence_lower for word in ['code', 'programming', 'function', 'class']):
            categories.append('coding')
        if any(word in sentence_lower for word in ['install', 'setup', 'configure']):
            categories.append('setup')
        if any(word in sentence_lower for word in ['test', 'debug', 'fix']):
            categories.append('testing')
        if any(word in sentence_lower for word in ['create', 'build', 'make']):
            categories.append('creation')
        
        # Calculate instruction probability
        is_instruction = (keyword_count >= 2 or starts_with_action) and len(sentence.split()) >= 5
        confidence = min((keyword_count * 0.3 + (1 if starts_with_action else 0) * 0.4), 1.0)
        
        return {
            'text': sentence,
            'is_instruction': is_instruction,
            'confidence': confidence,
            'keyword_count': keyword_count,
            'starts_with_action': starts_with_action,
            'categories': categories,
            'word_count': len(sentence.split())
        }
    
    def _extract_code_snippets(self, text: str) -> List[Dict[str, Any]]:
        """Extract code snippets from text"""
        import re
        
        code_snippets = []
        
        # Look for code patterns
        for pattern in self.code_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                code_snippets.append({
                    'snippet': match.group(),
                    'pattern': pattern,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_snippets
    
    def _calculate_instruction_confidence(self, instructions: List[Dict]) -> float:
        """Calculate overall confidence in instruction extraction"""
        if not instructions:
            return 0
        
        # Average individual confidences
        individual_confidences = [inst['confidence'] for inst in instructions]
        avg_confidence = sum(individual_confidences) / len(individual_confidences)
        
        # Boost confidence based on instruction density
        density_boost = min(len(instructions) * 0.1, 0.3)
        
        return min(avg_confidence + density_boost, 1.0)


# Example usage and testing functions
def test_video_processor():
    """Test function for video processor functionality"""
    processor = VideoProcessor()
    
    # Test finding video files
    video_files = processor.find_video_files("./temp_downloads")
    print(f"Found {len(video_files)} video files")
    
    if video_files:
        # Test video analysis
        for video_file in video_files[:1]:  # Test first video only
            try:
                analysis = processor.analyze_video_file(video_file)
                print(f"Video analysis: {analysis}")
                
                # Test transcription
                transcription = processor.extract_audio_and_transcribe(video_file)
                print(f"Transcription: {transcription}")
                
                # Test instruction extraction
                if transcription['success']:
                    extractor = InstructionExtractor()
                    instructions = extractor.extract_instructions(
                        transcription['transcription'], 
                        analysis
                    )
                    print(f"Instructions: {instructions}")
                
            except Exception as e:
                print(f"Error processing {video_file}: {e}")
    
    # Print statistics
    stats = processor.get_processing_stats()
    print(f"Processing stats: {stats}")


if __name__ == "__main__":
    test_video_processor()
