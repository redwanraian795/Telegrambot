import base64
import io
import json
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)

class ImageAnalysisService:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        
    def analyze_image_with_openai(self, image_path: str) -> Optional[str]:
        """Analyze image using OpenAI Vision API"""
        try:
            if not self.openai_api_key:
                return None
                
            # Convert image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image in detail. Describe what you see, identify objects, people, activities, emotions, colors, composition, and any notable aspects. Be comprehensive and engaging in your description."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI image analysis error: {e}")
            return None
    
    def analyze_image_with_gemini(self, image_path: str) -> Optional[str]:
        """Analyze image using Google Gemini Vision API"""
        try:
            if not self.gemini_api_key:
                return None
            
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Open and prepare image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
            
            prompt = """Analyze this image comprehensively. Describe:
            - Main subjects and objects
            - Activities or scenes taking place
            - Colors, lighting, and composition
            - Emotions or mood conveyed
            - Notable details or interesting aspects
            - Context or setting
            
            Be detailed, engaging, and provide insights about what makes this image interesting or significant."""
            
            response = model.generate_content([prompt, image_parts[0]])
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini image analysis error: {e}")
            return None
    
    def analyze_image(self, image_path: str) -> str:
        """Analyze image using available AI services"""
        # Try Gemini first (no cost), then OpenAI
        result = self.analyze_image_with_gemini(image_path)
        
        if not result:
            result = self.analyze_image_with_openai(image_path)
        
        if result:
            return f"🔍 **Image Analysis:**\n\n{result}"
        else:
            return "❌ Unable to analyze image. Please ensure AI services are properly configured."
    
    def create_meme(self, top_text: str = "", bottom_text: str = "", template: str = "drake") -> Optional[str]:
        """Create meme with text overlays"""
        try:
            # Create meme templates
            templates = {
                "drake": self._create_drake_meme,
                "distracted": self._create_distracted_boyfriend_meme,
                "expanding": self._create_expanding_brain_meme,
                "classic": self._create_classic_meme,
                "success": self._create_success_kid_meme
            }
            
            if template.lower() in templates:
                return templates[template.lower()](top_text, bottom_text)
            else:
                return self._create_classic_meme(top_text, bottom_text)
                
        except Exception as e:
            logger.error(f"Meme creation error: {e}")
            return None
    
    def _create_classic_meme(self, top_text: str, bottom_text: str) -> str:
        """Create classic meme format"""
        # Create image with white background
        img = Image.new('RGB', (500, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a larger font
            font_size = 30
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Add top text
        if top_text:
            bbox = draw.textbbox((0, 0), top_text.upper(), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (500 - text_width) // 2
            y = 20
            
            # Add black outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x+adj, y+adj2), top_text.upper(), font=font, fill='black')
            draw.text((x, y), top_text.upper(), font=font, fill='white')
        
        # Add bottom text
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text.upper(), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (500 - text_width) // 2
            y = 350 - text_height
            
            # Add black outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x+adj, y+adj2), bottom_text.upper(), font=font, fill='black')
            draw.text((x, y), bottom_text.upper(), font=font, fill='white')
        
        # Add meme placeholder
        draw.rectangle([50, 100, 450, 300], outline='black', width=3)
        draw.text((200, 200), "MEME IMAGE", font=font, fill='gray')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        return temp_file.name
    
    def _create_drake_meme(self, reject_text: str, approve_text: str) -> str:
        """Create Drake pointing meme format"""
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Draw Drake template boxes
        draw.rectangle([0, 0, 300, 200], fill='lightgray', outline='black')
        draw.rectangle([0, 200, 300, 400], fill='lightblue', outline='black')
        draw.rectangle([300, 0, 600, 200], fill='white', outline='black')
        draw.rectangle([300, 200, 600, 400], fill='white', outline='black')
        
        # Add Drake representations
        draw.text((150, 90), "🙅‍♂️", font=font, fill='black', anchor='mm')
        draw.text((150, 290), "👍", font=font, fill='black', anchor='mm')
        
        # Add text
        if reject_text:
            draw.text((450, 100), reject_text, font=font, fill='black', anchor='mm')
        if approve_text:
            draw.text((450, 300), approve_text, font=font, fill='black', anchor='mm')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        return temp_file.name
    
    def _create_distracted_boyfriend_meme(self, boyfriend_text: str, girlfriend_text: str) -> str:
        """Create distracted boyfriend meme format"""
        img = Image.new('RGB', (600, 400), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw characters
        draw.text((100, 200), "👫", font=font, fill='black', anchor='mm')
        draw.text((300, 150), "👀", font=font, fill='black', anchor='mm')
        draw.text((500, 180), "👩", font=font, fill='red', anchor='mm')
        
        # Add labels
        if boyfriend_text:
            draw.text((300, 120), boyfriend_text, font=font, fill='black', anchor='mm')
        if girlfriend_text:
            draw.text((100, 150), girlfriend_text, font=font, fill='black', anchor='mm')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        return temp_file.name
    
    def _create_expanding_brain_meme(self, text1: str, text2: str) -> str:
        """Create expanding brain meme format"""
        img = Image.new('RGB', (500, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        # Draw brain levels
        colors = ['gray', 'blue', 'yellow', 'rainbow']
        brains = ['🧠', '🧠', '🧠', '🌟']
        
        for i in range(2):
            y_pos = 50 + i * 250
            draw.rectangle([50, y_pos, 450, y_pos + 200], fill=colors[i], outline='black')
            draw.text((100, y_pos + 20), brains[i], font=font, fill='black')
            
            text = text1 if i == 0 else text2
            if text:
                draw.text((250, y_pos + 100), text, font=font, fill='white' if i == 0 else 'black', anchor='mm')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        return temp_file.name
    
    def _create_success_kid_meme(self, top_text: str, bottom_text: str) -> str:
        """Create success kid meme format"""
        img = Image.new('RGB', (400, 400), color='lightgreen')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        except:
            font = ImageFont.load_default()
        
        # Draw success kid
        draw.text((200, 200), "💪👶", font=font, fill='black', anchor='mm')
        
        # Add text
        if top_text:
            draw.text((200, 50), top_text.upper(), font=font, fill='white', anchor='mm')
        if bottom_text:
            draw.text((200, 350), bottom_text.upper(), font=font, fill='white', anchor='mm')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        return temp_file.name
    
    def get_meme_templates(self) -> str:
        """Get list of available meme templates"""
        templates = {
            "classic": "Classic top/bottom text meme",
            "drake": "Drake pointing meme (reject/approve)",
            "distracted": "Distracted boyfriend meme",
            "expanding": "Expanding brain meme",
            "success": "Success kid meme"
        }
        
        result = "🎭 **Available Meme Templates:**\n\n"
        for template, description in templates.items():
            result += f"• `{template}` - {description}\n"
        
        result += "\n**Usage:**\n"
        result += "`/meme [template] [text1] | [text2]`\n"
        result += "Example: `/meme drake studying | playing games`"
        
        return result