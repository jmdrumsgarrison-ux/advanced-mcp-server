"""
Modern Video Processor using Open Source Video-to-Code Tools
Integrates LLaVA-Video, Video-LLaVA, and other proven solutions
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import tempfile
import subprocess
import requests

# Modern video processing imports
try:
    from transformers import (
        AutoProcessor, 
        AutoTokenizer,
        LlavaNextVideoForConditionalGeneration,
        pipeline
    )
    import torch
    import cv2
    import whisper
    import moviepy.editor as mp
    from PIL import Image
    import numpy as np
    
    # Check if CUDA is available
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")
    
except ImportError as e:
    print(f"Modern video processing dependencies not installed: {e}")
    print("Run: pip install transformers torch opencv-python whisper-openai moviepy pillow")
    DEVICE = "cpu"

class ModernVideoProcessor:
    """
    Modern video processor using state-of-the-art open source tools:
    - LLaVA-Video for video instruction understanding
    - Video-LLaVA for unified video/image processing  
    - Whisper for audio transcription
    - HuggingFace Transformers for easy integration
    """
    
    def __init__(self, temp_dir: str = None):
        """Initialize with modern video processing models"""
        self.temp_dir = temp_dir or os.path.join(os.getcwd(), "temp_video_processing")
        self.logger = self._setup_logging()
        
        # Create temp directory
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize models
        self.models = {}
        self.processors = {}
        self._initialize_models()
        
        # Statistics
        self.stats = {
            'videos_processed': 0,
            'instructions_extracted': 0,
            'transcriptions_completed': 0,
            'code_generated': 0,
            'errors': 0,
            'last_processing_time': None
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('ModernVideoProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_models(self):
        """Initialize the state-of-the-art models"""
        self.logger.info("Initializing modern video processing models...")
        
        try:
            # Initialize Whisper for transcription
            self.logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self.logger.info("✅ Whisper model loaded")
            
            # Initialize Video-LLaVA for video understanding
            # Using smaller model first to test, can upgrade to larger models
            model_names = {
                "video_llava": "LanguageBind/Video-LLaVA-7B-hf",  # Video understanding
                "llava_next": "llava-hf/llava-v1.6-mistral-7b-hf"  # General visual understanding
            }
            
            for model_key, model_name in model_names.items():
                try:
                    self.logger.info(f"Loading {model_key}: {model_name}")
                    
                    # Load processor and model
                    processor = AutoProcessor.from_pretrained(model_name)
                    # For now, use CPU to avoid GPU memory issues during testing
                    model = LlavaNextVideoForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                        device_map="auto" if DEVICE == "cuda" else None,
                        low_cpu_mem_usage=True
                    )
                    
                    self.processors[model_key] = processor
                    self.models[model_key] = model
                    self.logger.info(f"✅ {model_key} loaded successfully")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_key}: {e}")
                    # Continue without this model
                    
            # Initialize code generation pipeline
            try:
                self.logger.info("Loading code generation pipeline...")
                self.code_pipeline = pipeline(
                    "text-generation",
                    model="deepseek-ai/deepseek-coder-6.7b-instruct",
                    device=0 if DEVICE == "cuda" else -1,
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                self.logger.info("✅ Code generation pipeline loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load code generation pipeline: {e}")
                self.code_pipeline = None
                
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            # Continue with limited functionality
    
    def process_video_for_instructions(self, video_path: str, 
                                     extract_audio: bool = True,
                                     generate_code: bool = True) -> Dict[str, Any]:
        """
        Complete video-to-code pipeline using modern tools
        
        Args:
            video_path: Path to video file
            extract_audio: Whether to extract and transcribe audio
            generate_code: Whether to generate code from instructions
            
        Returns:
            Complete processing results
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.logger.info(f"🎬 Processing video: {video_path}")
            start_time = time.time()
            
            results = {
                'video_path': video_path,
                'video_name': os.path.basename(video_path),
                'processing_start': start_time,
                'success': False
            }
            
            # Step 1: Basic video analysis
            self.logger.info("📊 Analyzing video properties...")
            video_info = self._analyze_video_properties(video_path)
            results['video_info'] = video_info
            
            # Step 2: Extract and transcribe audio
            if extract_audio:
                self.logger.info("🎵 Extracting and transcribing audio...")
                transcription = self._transcribe_video_audio(video_path)
                results['transcription'] = transcription
            
            # Step 3: Extract visual instructions using Video-LLaVA
            self.logger.info("👁️ Extracting visual instructions...")
            visual_instructions = self._extract_visual_instructions(video_path)
            results['visual_instructions'] = visual_instructions
            
            # Step 4: Combine audio and visual instructions
            self.logger.info("🔄 Combining audio and visual instructions...")
            combined_instructions = self._combine_instructions(
                results.get('transcription', {}),
                visual_instructions
            )
            results['combined_instructions'] = combined_instructions
            
            # Step 5: Generate code if requested
            if generate_code and combined_instructions.get('instruction_count', 0) > 0:
                self.logger.info("💻 Generating code from instructions...")
                generated_code = self._generate_code_from_instructions(combined_instructions)
                results['generated_code'] = generated_code
            
            # Update statistics
            processing_time = time.time() - start_time
            results['processing_time'] = processing_time
            results['success'] = True
            
            self.stats['videos_processed'] += 1
            self.stats['last_processing_time'] = time.time()
            if results.get('transcription'):
                self.stats['transcriptions_completed'] += 1
            if results.get('combined_instructions', {}).get('instruction_count', 0) > 0:
                self.stats['instructions_extracted'] += 1
            if results.get('generated_code'):
                self.stats['code_generated'] += 1
            
            self.logger.info(f"✅ Video processing complete in {processing_time:.2f}s")
            return results
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"❌ Video processing failed: {e}")
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def _analyze_video_properties(self, video_path: str) -> Dict[str, Any]:
        """Analyze basic video properties using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            return {
                'duration_seconds': round(duration, 2),
                'fps': round(fps, 2),
                'frame_count': frame_count,
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'suitable_for_processing': duration > 0 and duration < 600  # Max 10 minutes
            }
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {e}")
            return {'error': str(e)}
    
    def _transcribe_video_audio(self, video_path: str) -> Dict[str, Any]:
        """Extract and transcribe audio using Whisper"""
        try:
            if not hasattr(self, 'whisper_model') or self.whisper_model is None:
                return {'success': False, 'error': 'Whisper model not available'}
            
            # Extract audio using moviepy
            video_name = Path(video_path).stem
            audio_path = os.path.join(self.temp_dir, f"{video_name}_audio.wav")
            
            clip = mp.VideoFileClip(video_path)
            if clip.audio is None:
                return {'success': False, 'error': 'Video has no audio track'}
            
            clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
            clip.close()
            
            # Transcribe using Whisper
            result = self.whisper_model.transcribe(audio_path)
            
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return {
                'success': True,
                'text': result.get('text', ''),
                'segments': result.get('segments', []),
                'language': result.get('language', 'unknown'),
                'confidence': self._calculate_whisper_confidence(result.get('segments', []))
            }
            
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_visual_instructions(self, video_path: str) -> Dict[str, Any]:
        """Extract instructions from video using Video-LLaVA"""
        try:
            # Check if we have a video understanding model
            if 'video_llava' not in self.models and 'llava_next' not in self.models:
                return {
                    'success': False, 
                    'error': 'No video understanding model available',
                    'instructions': []
                }
            
            # Sample frames from video
            frames = self._sample_video_frames(video_path, max_frames=8)
            if not frames:
                return {'success': False, 'error': 'Could not extract frames'}
            
            # Prepare instruction prompts for different types of content
            prompts = [
                "What programming instructions or coding tasks are shown in this video?",
                "List any step-by-step instructions for building or creating something shown in this video.",
                "What actions or commands would someone need to follow to recreate what's shown in this video?",
                "Describe any technical processes or development steps demonstrated in this video."
            ]
            
            all_instructions = []
            
            # Use available model
            model_key = 'video_llava' if 'video_llava' in self.models else 'llava_next'
            processor = self.processors[model_key]
            model = self.models[model_key]
            
            for prompt in prompts:
                try:
                    # Prepare inputs
                    if model_key == 'video_llava':
                        # Video-LLaVA format
                        inputs = processor(
                            text=f"USER: {prompt} ASSISTANT:",
                            videos=[frames],
                            return_tensors="pt"
                        )
                    else:
                        # LLaVA-Next format (image-based)
                        inputs = processor(
                            text=prompt,
                            images=frames[:4],  # Use first 4 frames
                            return_tensors="pt"
                        )
                    
                    # Generate response
                    with torch.no_grad():
                        outputs = model.generate(
                            **inputs,
                            max_new_tokens=200,
                            do_sample=True,
                            temperature=0.7
                        )
                    
                    # Decode response
                    response = processor.decode(outputs[0], skip_special_tokens=True)
                    
                    # Extract instruction content
                    if response and len(response.strip()) > 20:
                        all_instructions.append({
                            'prompt': prompt,
                            'response': response,
                            'confidence': 0.8  # Default confidence
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Instruction extraction failed for prompt: {e}")
                    continue
            
            return {
                'success': True,
                'instructions': all_instructions,
                'instruction_count': len(all_instructions),
                'frames_processed': len(frames),
                'model_used': model_key
            }
            
        except Exception as e:
            self.logger.error(f"Visual instruction extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _sample_video_frames(self, video_path: str, max_frames: int = 8) -> List[Image.Image]:
        """Sample frames from video for processing"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_count == 0:
                return []
            
            # Calculate frame indices to sample
            step = max(1, frame_count // max_frames)
            indices = list(range(0, frame_count, step))[:max_frames]
            
            frames = []
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    frames.append(pil_image)
            
            cap.release()
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame sampling failed: {e}")
            return []
    
    def _calculate_whisper_confidence(self, segments: List[Dict]) -> float:
        """Calculate confidence from Whisper segments"""
        if not segments:
            return 0.0
        
        total_confidence = 0
        total_length = 0
        
        for segment in segments:
            if 'avg_logprob' in segment:
                # Convert log probability to confidence
                confidence = np.exp(segment['avg_logprob'])
                duration = segment.get('end', 0) - segment.get('start', 0)
                total_confidence += confidence * duration
                total_length += duration
        
        return total_confidence / total_length if total_length > 0 else 0.0
    
    def _combine_instructions(self, transcription: Dict, visual_instructions: Dict) -> Dict[str, Any]:
        """Combine audio transcription and visual instructions"""
        combined = {
            'audio_instructions': [],
            'visual_instructions': [],
            'instruction_count': 0,
            'confidence': 0,
            'sources': []
        }
        
        # Process audio transcription
        if transcription.get('success') and transcription.get('text'):
            audio_text = transcription['text']
            # Extract instructional sentences from transcription
            sentences = self._extract_instruction_sentences(audio_text)
            combined['audio_instructions'] = sentences
            combined['sources'].append('audio')
        
        # Process visual instructions
        if visual_instructions.get('success') and visual_instructions.get('instructions'):
            combined['visual_instructions'] = visual_instructions['instructions']
            combined['sources'].append('visual')
        
        # Calculate totals
        combined['instruction_count'] = (
            len(combined['audio_instructions']) + 
            len(combined['visual_instructions'])
        )
        
        # Calculate combined confidence
        audio_conf = transcription.get('confidence', 0) if transcription.get('success') else 0
        visual_conf = 0.8 if visual_instructions.get('success') else 0  # Default visual confidence
        
        if combined['sources']:
            combined['confidence'] = (audio_conf + visual_conf) / len(combined['sources'])
        
        return combined
    
    def _extract_instruction_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Extract instructional sentences from transcription text"""
        if not text:
            return []
        
        # Simple instruction detection keywords
        instruction_keywords = [
            'create', 'build', 'make', 'develop', 'code', 'write', 'implement',
            'add', 'install', 'setup', 'configure', 'run', 'execute', 'test',
            'import', 'define', 'function', 'class', 'variable', 'method'
        ]
        
        sentences = text.split('.')
        instructions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            sentence_lower = sentence.lower()
            keyword_count = sum(1 for keyword in instruction_keywords if keyword in sentence_lower)
            
            if keyword_count >= 2:  # Require at least 2 instruction keywords
                instructions.append({
                    'text': sentence,
                    'keyword_count': keyword_count,
                    'confidence': min(keyword_count * 0.3, 1.0)
                })
        
        return instructions
    
    def _generate_code_from_instructions(self, instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code from combined instructions"""
        try:
            if not self.code_pipeline:
                return {
                    'success': False, 
                    'error': 'Code generation pipeline not available',
                    'code': ''
                }
            
            # Combine all instruction text
            all_instructions = []
            
            # Add audio instructions
            for inst in instructions.get('audio_instructions', []):
                all_instructions.append(inst['text'])
            
            # Add visual instructions
            for inst in instructions.get('visual_instructions', []):
                all_instructions.append(inst['response'])
            
            if not all_instructions:
                return {'success': False, 'error': 'No instructions to process'}
            
            # Create code generation prompt
            instruction_text = ' '.join(all_instructions)
            prompt = f"""Based on these instructions from a video tutorial, write Python code to implement the described functionality:

Instructions: {instruction_text}

Python code:"""
            
            # Generate code
            response = self.code_pipeline(
                prompt,
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.code_pipeline.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            
            # Extract code part (after "Python code:")
            if "Python code:" in generated_text:
                code = generated_text.split("Python code:")[1].strip()
            else:
                code = generated_text.strip()
            
            return {
                'success': True,
                'code': code,
                'prompt': prompt,
                'instruction_count': len(all_instructions),
                'model_used': 'deepseek-coder'
            }
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'videos_processed': self.stats['videos_processed'],
            'instructions_extracted': self.stats['instructions_extracted'],
            'transcriptions_completed': self.stats['transcriptions_completed'],
            'code_generated': self.stats['code_generated'],
            'errors': self.stats['errors'],
            'last_processing_time': self.stats['last_processing_time'],
            'models_available': list(self.models.keys()),
            'whisper_available': hasattr(self, 'whisper_model') and self.whisper_model is not None,
            'code_pipeline_available': self.code_pipeline is not None,
            'device': DEVICE
        }
    
    def find_video