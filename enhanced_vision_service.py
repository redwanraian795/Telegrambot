import base64
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from ai_services import gemini_vision_analyze
from PIL import Image, ImageEnhance, ImageFilter
import requests

# Optional dependencies with fallback handling
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

class EnhancedVisionService:
    """Advanced image and video analysis with OCR, face recognition, and object detection"""
    
    def __init__(self):
        self.ocr_cache = {}
        self.face_cache = {}
        self.analysis_cache = {}
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract and analyze text from images using OCR"""
        try:
            if not os.path.exists(image_path):
                return {"error": "Image file not found"}
            
            # Check cache first
            cache_key = f"{image_path}_{os.path.getmtime(image_path)}"
            if cache_key in self.ocr_cache:
                return self.ocr_cache[cache_key]
            
            # Load and enhance image for better OCR
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image for better text recognition
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Apply filters to improve text clarity
            image = image.filter(ImageFilter.MedianFilter())
            
            # Extract text using pytesseract if available
            if PYTESSERACT_AVAILABLE:
                try:
                    extracted_text = pytesseract.image_to_string(image)
                    confidence_scores = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                    # Calculate average confidence
                    confidences = [int(conf) for conf in confidence_scores['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Extract word-level data
                    words_data = []
                    for i, word in enumerate(confidence_scores['text']):
                        if word.strip() and int(confidence_scores['conf'][i]) > 30:
                            words_data.append({
                                'text': word,
                                'confidence': int(confidence_scores['conf'][i]),
                                'bbox': {
                                    'x': confidence_scores['left'][i],
                                    'y': confidence_scores['top'][i],
                                    'width': confidence_scores['width'][i],
                                    'height': confidence_scores['height'][i]
                                }
                            })
                    
                    result = {
                        'text': extracted_text.strip(),
                        'confidence': avg_confidence,
                        'word_count': len(extracted_text.split()),
                        'words_data': words_data,
                        'languages_detected': self._detect_languages(extracted_text),
                        'text_regions': len([w for w in words_data if w['confidence'] > 50])
                    }
                except Exception as e:
                    result = {
                        'text': '',
                        'confidence': 0,
                        'word_count': 0,
                        'words_data': [],
                        'languages_detected': [],
                        'text_regions': 0,
                        'error': f'OCR processing failed: {str(e)}'
                    }
            else:
                # Fallback to Gemini Vision for text extraction
                try:
                    temp_path = f'/tmp/ocr_temp_{hash(image_path)}.jpg'
                    image.save(temp_path)
                    gemini_text = gemini_vision_analyze(temp_path, "Extract all text from this image. Only return the text content, no descriptions.")
                    os.remove(temp_path)
                    
                    result = {
                        'text': gemini_text.strip() if gemini_text else '',
                        'confidence': 85,  # Estimated confidence for Gemini
                        'word_count': len(gemini_text.split()) if gemini_text else 0,
                        'words_data': [],
                        'languages_detected': self._detect_languages(gemini_text) if gemini_text else [],
                        'text_regions': 1 if gemini_text else 0,
                        'method': 'gemini_vision_fallback'
                    }
                except Exception as gemini_error:
                    result = {
                        'text': '',
                        'confidence': 0,
                        'word_count': 0,
                        'words_data': [],
                        'languages_detected': [],
                        'text_regions': 0,
                        'error': f'OCR and fallback failed: {str(gemini_error)}'
                    }
                
            # Cache the result
            self.ocr_cache[cache_key] = result
            return result
                
        except Exception as e:
            return {"error": f"Image processing failed: {str(e)}"}
    
    def _detect_languages(self, text: str) -> List[str]:
        """Simple language detection for extracted text"""
        languages = []
        
        # Basic language patterns
        if any(ord(char) >= 0x4e00 and ord(char) <= 0x9fff for char in text):
            languages.append("Chinese")
        if any(ord(char) >= 0x0600 and ord(char) <= 0x06ff for char in text):
            languages.append("Arabic")
        if any(ord(char) >= 0x0400 and ord(char) <= 0x04ff for char in text):
            languages.append("Cyrillic")
        if any(char in "αβγδεζηθικλμνξοπρστυφχψω" for char in text.lower()):
            languages.append("Greek")
        
        # Default to Latin-based if no special scripts detected
        if not languages and any(char.isalpha() for char in text):
            languages.append("Latin-based")
        
        return languages or ["Unknown"]
    
    def analyze_faces_in_image(self, image_path: str) -> Dict[str, Any]:
        """Detect and analyze faces in images"""
        try:
            if not os.path.exists(image_path):
                return {"error": "Image file not found"}
            
            # Use face_recognition if available
            if FACE_RECOGNITION_AVAILABLE:
                try:
                    image = face_recognition.load_image_file(image_path)
                
                    # Find face locations
                    face_locations = face_recognition.face_locations(image)
                    face_encodings = face_recognition.face_encodings(image, face_locations)
                    
                    faces_data = []
                    for i, (top, right, bottom, left) in enumerate(face_locations):
                        face_info = {
                            'face_id': i + 1,
                            'location': {
                                'top': top,
                                'right': right, 
                                'bottom': bottom,
                                'left': left
                            },
                            'size': {
                                'width': right - left,
                                'height': bottom - top
                            },
                            'center': {
                                'x': (left + right) // 2,
                                'y': (top + bottom) // 2
                            }
                        }
                        faces_data.append(face_info)
                    
                    result = {
                        'face_count': len(face_locations),
                        'faces_detected': faces_data,
                        'has_faces': len(face_locations) > 0,
                        'analysis': self._analyze_face_composition(faces_data, (480, 640))  # Default shape
                    }
                    
                    return result
                    
                except Exception as face_error:
                    return {"error": f"Face detection failed: {str(face_error)}"}
            else:
                # Fallback to Gemini Vision for face analysis
                try:
                    analysis = gemini_vision_analyze(image_path, "Analyze this image for faces. Count the number of faces and describe their positions. Return information in a structured format.")
                    return {
                        'face_count': 0,
                        'faces_detected': [],
                        'has_faces': False,
                        'analysis': analysis,
                        'method': 'gemini_vision_fallback'
                    }
                except Exception as gemini_error:
                    return {"error": f"Face analysis failed: {str(gemini_error)}"}
                
        except Exception as e:
            return {"error": f"Face analysis failed: {str(e)}"}
    
    def _analyze_face_composition(self, faces_data: List[Dict], image_shape: Tuple) -> Dict[str, Any]:
        """Analyze face composition and positioning"""
        if not faces_data:
            return {"composition": "no_faces"}
        
        height, width = image_shape[:2]
        analysis = {
            "composition": "",
            "positioning": [],
            "size_analysis": ""
        }
        
        # Analyze positioning
        for face in faces_data:
            center_x = face['center']['x']
            center_y = face['center']['y']
            
            # Determine position
            h_pos = "center"
            if center_x < width * 0.33:
                h_pos = "left"
            elif center_x > width * 0.67:
                h_pos = "right"
            
            v_pos = "center"
            if center_y < height * 0.33:
                v_pos = "top"
            elif center_y > height * 0.67:
                v_pos = "bottom"
            
            analysis["positioning"].append(f"{v_pos}_{h_pos}")
        
        # Composition analysis
        if len(faces_data) == 1:
            analysis["composition"] = "portrait"
        elif len(faces_data) == 2:
            analysis["composition"] = "couple/duo"
        elif len(faces_data) <= 5:
            analysis["composition"] = "small_group"
        else:
            analysis["composition"] = "large_group"
        
        # Size analysis
        face_sizes = [face['size']['width'] * face['size']['height'] for face in faces_data]
        avg_face_size = sum(face_sizes) / len(face_sizes)
        image_size = width * height
        face_ratio = avg_face_size / image_size
        
        if face_ratio > 0.1:
            analysis["size_analysis"] = "close_up"
        elif face_ratio > 0.05:
            analysis["size_analysis"] = "medium_shot"
        else:
            analysis["size_analysis"] = "wide_shot"
        
        return analysis
    
    def count_objects_in_image(self, image_path: str, object_type: str = None) -> Dict[str, Any]:
        """Count and identify objects in images using AI analysis"""
        try:
            if not os.path.exists(image_path):
                return {"error": "Image file not found"}
            
            # Use Gemini Vision for object detection and counting
            if object_type:
                prompt = f"Count the number of {object_type} in this image. Provide an exact count and describe their locations. Also identify any other significant objects you can see."
            else:
                prompt = "Identify and count all significant objects in this image. Provide specific counts for each type of object you can clearly identify."
            
            analysis_result = gemini_vision_analyze(image_path, prompt)
            
            # Parse the response to extract object counts
            objects_found = self._parse_object_counts(analysis_result)
            
            result = {
                'analysis': analysis_result,
                'objects_detected': objects_found,
                'total_objects': sum(objects_found.values()) if objects_found else 0,
                'requested_object': object_type,
                'found_requested': object_type in objects_found if object_type else None
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Object counting failed: {str(e)}"}
    
    def _parse_object_counts(self, analysis_text: str) -> Dict[str, int]:
        """Extract object counts from AI analysis text"""
        objects = {}
        
        # Common number words to digits mapping
        number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
        }
        
        lines = analysis_text.lower().split('\n')
        for line in lines:
            # Look for patterns like "3 cars", "two people", "five bottles"
            words = line.split()
            for i, word in enumerate(words):
                # Check for digit followed by object
                if word.isdigit() and i + 1 < len(words):
                    count = int(word)
                    obj = words[i + 1].rstrip('.,!?')
                    objects[obj] = count
                
                # Check for number word followed by object
                elif word in number_words and i + 1 < len(words):
                    count = number_words[word]
                    obj = words[i + 1].rstrip('.,!?')
                    objects[obj] = count
        
        return objects
    
    def compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """Compare two images for similarities and differences"""
        try:
            if not os.path.exists(image1_path) or not os.path.exists(image2_path):
                return {"error": "One or both image files not found"}
            
            # Use Gemini Vision to compare images
            # Create a combined analysis prompt
            analysis1 = gemini_vision_analyze(image1_path, "Describe this image in detail, focusing on key objects, colors, composition, and notable features.")
            analysis2 = gemini_vision_analyze(image2_path, "Describe this image in detail, focusing on key objects, colors, composition, and notable features.")
            
            # Create comparison prompt for AI
            comparison_prompt = f"""Compare these two image descriptions and identify:
1. Key similarities between the images
2. Major differences
3. Common objects or themes
4. Different styles or compositions
5. Overall similarity score (1-10)

Image 1 Analysis: {analysis1}

Image 2 Analysis: {analysis2}

Provide a detailed comparison."""
            
            # Get AI comparison (using regular chat since we're comparing text descriptions)
            from ai_services import ai_services
            comparison_result = ai_services.chat_with_ai(comparison_prompt, "image_comparison")
            
            result = {
                'image1_analysis': analysis1,
                'image2_analysis': analysis2,
                'comparison': comparison_result,
                'images_compared': [image1_path, image2_path]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Image comparison failed: {str(e)}"}
    
    def enhanced_scene_analysis(self, image_path: str) -> Dict[str, Any]:
        """Comprehensive scene analysis including mood, setting, and context"""
        try:
            if not os.path.exists(image_path):
                return {"error": "Image file not found"}
            
            # Multi-aspect analysis using Gemini Vision
            analyses = {}
            
            # Scene composition analysis
            analyses['composition'] = gemini_vision_analyze(
                image_path, 
                "Analyze the composition of this image: describe the rule of thirds, leading lines, symmetry, balance, focal points, and overall visual structure."
            )
            
            # Mood and atmosphere analysis
            analyses['mood'] = gemini_vision_analyze(
                image_path,
                "Analyze the mood and atmosphere of this image: describe the emotional tone, lighting mood, color psychology, and feelings it evokes."
            )
            
            # Setting and context analysis
            analyses['setting'] = gemini_vision_analyze(
                image_path,
                "Identify the setting and context: where was this taken (indoor/outdoor, specific location type), time of day, season, cultural context, and purpose."
            )
            
            # Technical analysis
            analyses['technical'] = gemini_vision_analyze(
                image_path,
                "Analyze technical aspects: lighting quality, color palette, contrast, saturation, apparent camera angle, depth of field, and image quality."
            )
            
            # Combine all analyses
            result = {
                'comprehensive_analysis': {
                    'composition': analyses['composition'],
                    'mood_atmosphere': analyses['mood'],
                    'setting_context': analyses['setting'],
                    'technical_aspects': analyses['technical']
                },
                'summary': self._create_analysis_summary(analyses)
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Scene analysis failed: {str(e)}"}
    
    def _create_analysis_summary(self, analyses: Dict[str, str]) -> str:
        """Create a concise summary of all analyses"""
        summary_prompt = f"""Create a concise summary of this comprehensive image analysis:

Composition: {analyses['composition']}
Mood: {analyses['mood']}
Setting: {analyses['setting']}
Technical: {analyses['technical']}

Provide a 2-3 sentence summary highlighting the most important insights."""
        
        from ai_services import ai_services
        return ai_services.chat_with_ai(summary_prompt, "analysis_summary")

    def analyze_image_content(self, image_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze image content with specified analysis type"""
        try:
            if not os.path.exists(image_path):
                return {"error": "Image file not found"}
            
            if analysis_type == "comprehensive":
                return self.enhanced_scene_analysis(image_path)
            elif analysis_type == "objects":
                return self.count_objects_in_image(image_path)
            elif analysis_type == "text":
                return self.extract_text_from_image(image_path)
            elif analysis_type == "faces":
                return self.detect_faces_in_image(image_path)
            else:
                # Default comprehensive analysis
                prompt = f"Analyze this image for {analysis_type}. Provide detailed insights."
                analysis = gemini_vision_analyze(image_path, prompt)
                return {"analysis": analysis, "type": analysis_type}
                
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}
    
    def detect_faces(self, image_path: str) -> Dict[str, Any]:
        """Detect faces in image - alias for detect_faces_in_image"""
        return self.detect_faces_in_image(image_path)

# Global instance
enhanced_vision_service = EnhancedVisionService()