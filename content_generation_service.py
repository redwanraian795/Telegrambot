import json
import os
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from ai_services import ai_services
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

class ContentGenerationService:
    """Advanced AI content generation for memes, stories, plans, and creative content"""
    
    def __init__(self):
        self.meme_templates = self.load_meme_templates()
        self.story_genres = ["fantasy", "sci-fi", "mystery", "romance", "adventure", "horror", "comedy"]
        self.workout_types = ["strength", "cardio", "flexibility", "hiit", "yoga", "bodyweight"]
        self.cuisine_types = ["italian", "asian", "mediterranean", "mexican", "indian", "american"]
    
    def load_meme_templates(self) -> List[Dict[str, Any]]:
        """Load meme templates and formats"""
        return [
            {"name": "Drake", "format": "rejection_then_approval", "style": "two_panel"},
            {"name": "Distracted Boyfriend", "format": "choice_conflict", "style": "three_subject"},
            {"name": "Change My Mind", "format": "controversial_statement", "style": "single_panel"},
            {"name": "Two Buttons", "format": "difficult_choice", "style": "decision"},
            {"name": "Expanding Brain", "format": "progression", "style": "multi_level"},
            {"name": "This Is Fine", "format": "denial", "style": "situational"},
            {"name": "Woman Yelling at Cat", "format": "accusation_defense", "style": "split_panel"}
        ]
    
    def generate_custom_meme(self, user_prompt: str, template: str = None) -> Dict[str, Any]:
        """Generate custom meme content based on user prompt"""
        try:
            # Select template if not specified
            if not template:
                template = random.choice(self.meme_templates)["name"]
            
            # Find template details
            template_info = next((t for t in self.meme_templates if t["name"].lower() == template.lower()), None)
            if not template_info:
                template_info = random.choice(self.meme_templates)
            
            # Generate meme text using AI
            meme_prompt = f"""Create a funny meme using the "{template_info['name']}" template format ({template_info['format']}).
            
User's topic/prompt: {user_prompt}

Based on the template style "{template_info['style']}", generate appropriate text for this meme. 
Make it humorous, relatable, and fitting for the template format.

Provide:
1. Top text (if applicable)
2. Bottom text (if applicable) 
3. Alternative text options
4. Explanation of why this works for the template

Keep it appropriate and funny."""
            
            meme_content = ai_services.chat_with_ai(meme_prompt, "meme_generation")
            
            # Create simple text-based meme image
            meme_image_path = self._create_text_meme(meme_content, template_info)
            
            result = {
                'template_used': template_info['name'],
                'meme_content': meme_content,
                'image_path': meme_image_path,
                'format': template_info['format'],
                'user_prompt': user_prompt,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Meme generation failed: {str(e)}"}
    
    def _create_text_meme(self, content: str, template_info: Dict) -> Optional[str]:
        """Create a simple text-based meme image"""
        try:
            # Create image
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fall back to default if not available
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Extract key text from AI content
            lines = content.split('\n')
            top_text = ""
            bottom_text = ""
            
            for line in lines:
                if "top text" in line.lower() or "first panel" in line.lower():
                    top_text = line.split(':', 1)[-1].strip().strip('"')
                elif "bottom text" in line.lower() or "second panel" in line.lower():
                    bottom_text = line.split(':', 1)[-1].strip().strip('"')
            
            # If no specific text found, use first two meaningful lines
            if not top_text and not bottom_text:
                meaningful_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                if len(meaningful_lines) >= 2:
                    top_text = meaningful_lines[0]
                    bottom_text = meaningful_lines[1]
                elif len(meaningful_lines) == 1:
                    top_text = meaningful_lines[0]
            
            # Draw template name
            draw.text((20, 20), f"Template: {template_info['name']}", fill='black', font=font_medium)
            
            # Draw meme text
            if top_text:
                wrapped_top = textwrap.fill(top_text, width=40)
                draw.text((50, 100), wrapped_top, fill='black', font=font_large)
            
            if bottom_text:
                wrapped_bottom = textwrap.fill(bottom_text, width=40)
                draw.text((50, 400), wrapped_bottom, fill='black', font=font_large)
            
            # Save image
            meme_filename = f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            meme_path = os.path.join("downloads", meme_filename)
            
            # Ensure downloads directory exists
            os.makedirs("downloads", exist_ok=True)
            
            image.save(meme_path)
            return meme_path
            
        except Exception as e:
            print(f"Meme image creation failed: {e}")
            return None
    
    def generate_meme(self, user_id: str, prompt: str, template: str = None) -> Dict[str, Any]:
        """Generate meme for user (public method)"""
        return self.generate_custom_meme(prompt, template)
    
    def generate_story(self, prompt: str, genre: str = None, length: str = "medium") -> Dict[str, Any]:
        """Generate creative story - alias for generate_creative_story"""
        return self.generate_creative_story(prompt, genre, length)
    
    def generate_workout(self, user_profile: str, goals: str, duration: str = "4 weeks") -> Dict[str, Any]:
        """Generate workout plan - alias for generate_workout_plan"""
        return self.generate_workout_plan(user_profile, goals, duration)
    
    def generate_creative_story(self, prompt: str, genre: str = None, length: str = "medium") -> Dict[str, Any]:
        """Generate creative stories, poems, and writing"""
        try:
            if not genre:
                genre = random.choice(self.story_genres)
            
            # Determine length parameters
            length_params = {
                "short": "200-400 words, quick narrative",
                "medium": "600-1000 words, developed plot with characters",
                "long": "1200-2000 words, detailed story with multiple scenes"
            }
            
            length_spec = length_params.get(length, length_params["medium"])
            
            story_prompt = f"""Write a creative {genre} story based on this prompt: {prompt}

Requirements:
- Length: {length_spec}
- Genre: {genre}
- Include engaging characters, dialogue, and vivid descriptions
- Create a compelling plot with conflict and resolution
- Use creative and immersive writing style
- Make it entertaining and original

Write a complete story that captivates the reader."""
            
            story_content = ai_services.chat_with_ai(story_prompt, "story_generation")
            
            # Generate additional elements
            character_analysis = ai_services.chat_with_ai(f"Analyze the main characters in this story and describe their personalities, motivations, and relationships: {story_content[:500]}...", "character_analysis")
            
            themes_analysis = ai_services.chat_with_ai(f"Identify the main themes, literary elements, and message of this story: {story_content[:500]}...", "themes_analysis")
            
            result = {
                'story': story_content,
                'genre': genre,
                'length': length,
                'word_count': len(story_content.split()),
                'character_analysis': character_analysis,
                'themes': themes_analysis,
                'user_prompt': prompt,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Story generation failed: {str(e)}"}
    
    def generate_workout_plan(self, user_profile: str, goals: str, duration: str = "4 weeks") -> Dict[str, Any]:
        """Generate personalized workout plans"""
        try:
            workout_prompt = f"""Create a comprehensive {duration} workout plan for this person:

User Profile: {user_profile}
Goals: {goals}

Include:
1. Weekly schedule with specific days and exercises
2. Progressive difficulty over the time period
3. Warm-up and cool-down routines
4. Exercise descriptions and proper form tips
5. Nutrition guidelines to support the goals
6. Recovery and rest day recommendations
7. Progress tracking suggestions
8. Equipment needed (or bodyweight alternatives)

Make it practical, safe, and achievable for the user's profile."""
            
            workout_plan = ai_services.chat_with_ai(workout_prompt, "workout_planning")
            
            # Generate supplementary advice
            nutrition_tips = ai_services.chat_with_ai(f"Provide specific nutrition advice for someone with these goals: {goals}. Include meal timing, macro ratios, and supplement recommendations if appropriate.", "nutrition_advice")
            
            safety_tips = ai_services.chat_with_ai(f"Provide important safety tips and injury prevention advice for this workout plan: {workout_plan[:300]}...", "safety_advice")
            
            result = {
                'workout_plan': workout_plan,
                'nutrition_advice': nutrition_tips,
                'safety_tips': safety_tips,
                'duration': duration,
                'user_profile': user_profile,
                'goals': goals,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Workout plan generation failed: {str(e)}"}
    
    def generate_recipe(self, cuisine_type: str = None, dietary_restrictions: str = "", ingredients: str = "") -> Dict[str, Any]:
        """Generate custom recipes based on preferences"""
        try:
            if not cuisine_type:
                cuisine_type = random.choice(self.cuisine_types)
            
            recipe_prompt = f"""Create a delicious {cuisine_type} recipe with these specifications:

Dietary restrictions: {dietary_restrictions if dietary_restrictions else "None"}
Available ingredients: {ingredients if ingredients else "Use any appropriate ingredients"}

Provide:
1. Recipe name and brief description
2. Complete ingredients list with measurements
3. Step-by-step cooking instructions
4. Prep time and cooking time
5. Serving size
6. Difficulty level
7. Nutritional highlights
8. Chef's tips for best results
9. Possible variations or substitutions
10. Wine or beverage pairing suggestions

Make it detailed enough for a home cook to follow successfully."""
            
            recipe_content = ai_services.chat_with_ai(recipe_prompt, "recipe_generation")
            
            # Generate additional culinary content
            cooking_tips = ai_services.chat_with_ai(f"Provide advanced cooking techniques and professional tips for mastering this type of {cuisine_type} cuisine.", "cooking_tips")
            
            ingredient_info = ai_services.chat_with_ai(f"Explain the key ingredients in {cuisine_type} cooking, their origins, nutritional benefits, and how to select the best quality.", "ingredient_education")
            
            result = {
                'recipe': recipe_content,
                'cuisine_type': cuisine_type,
                'dietary_restrictions': dietary_restrictions,
                'cooking_tips': cooking_tips,
                'ingredient_info': ingredient_info,
                'available_ingredients': ingredients,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Recipe generation failed: {str(e)}"}
    
    def generate_poem(self, topic: str, style: str = "free verse", mood: str = "reflective") -> Dict[str, Any]:
        """Generate custom poetry in various styles"""
        try:
            poetry_styles = {
                "free verse": "no strict rhyme scheme, natural rhythm",
                "sonnet": "14 lines with traditional rhyme scheme",
                "haiku": "3 lines, 5-7-5 syllable pattern",
                "limerick": "5 lines, AABBA rhyme scheme, humorous",
                "ballad": "narrative poem with ABAB rhyme scheme",
                "acrostic": "first letters spell out the topic word"
            }
            
            style_description = poetry_styles.get(style, poetry_styles["free verse"])
            
            poem_prompt = f"""Write a beautiful {style} poem about: {topic}

Style requirements: {style_description}
Mood: {mood}

Create a poem that:
- Captures the essence and emotion of the topic
- Uses vivid imagery and metaphors
- Follows the {style} format correctly
- Conveys the {mood} mood throughout
- Is memorable and impactful

Write with artistic flair and emotional depth."""
            
            poem_content = ai_services.chat_with_ai(poem_prompt, "poetry_generation")
            
            # Analyze the poem
            poem_analysis = ai_services.chat_with_ai(f"Analyze this poem's literary devices, themes, and artistic techniques: {poem_content}", "poetry_analysis")
            
            result = {
                'poem': poem_content,
                'topic': topic,
                'style': style,
                'mood': mood,
                'literary_analysis': poem_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Poem generation failed: {str(e)}"}
    
    def generate_custom_stickers(self, theme: str, count: int = 8) -> Dict[str, Any]:
        """Generate custom sticker pack concepts"""
        try:
            sticker_prompt = f"""Design a custom sticker pack with the theme: {theme}

Create {count} unique sticker concepts that:
1. Are expressive and convey different emotions/reactions
2. Work well in chat conversations
3. Are visually appealing and memorable
4. Fit the theme cohesively
5. Include variety (happy, sad, excited, confused, etc.)

For each sticker, provide:
- Description of the visual design
- Emotion/message it conveys
- Suggested use cases in conversations
- Color scheme and style notes

Make them creative and fun for messaging apps."""
            
            sticker_concepts = ai_services.chat_with_ai(sticker_prompt, "sticker_design")
            
            # Create simple text-based sticker previews
            sticker_files = []
            lines = sticker_concepts.split('\n')
            sticker_descriptions = [line for line in lines if line.strip() and ('sticker' in line.lower() or 'design' in line.lower())]
            
            for i, desc in enumerate(sticker_descriptions[:count]):
                sticker_path = self._create_text_sticker(desc, i + 1, theme)
                if sticker_path:
                    sticker_files.append(sticker_path)
            
            result = {
                'theme': theme,
                'sticker_count': count,
                'concepts': sticker_concepts,
                'sticker_files': sticker_files,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Sticker generation failed: {str(e)}"}
    
    def _create_text_sticker(self, description: str, number: int, theme: str) -> Optional[str]:
        """Create simple text-based sticker preview"""
        try:
            # Create small square image for sticker
            size = 200
            image = Image.new('RGB', (size, size), color='lightblue')
            draw = ImageDraw.Draw(image)
            
            # Try to load font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw theme and number
            draw.text((10, 10), f"{theme} #{number}", fill='black', font=font)
            
            # Draw simplified description
            desc_short = description[:50] + "..." if len(description) > 50 else description
            wrapped_desc = textwrap.fill(desc_short, width=15)
            draw.text((10, 50), wrapped_desc, fill='darkblue', font=font)
            
            # Save sticker
            sticker_filename = f"sticker_{theme}_{number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            sticker_path = os.path.join("downloads", sticker_filename)
            
            os.makedirs("downloads", exist_ok=True)
            image.save(sticker_path)
            return sticker_path
            
        except Exception as e:
            print(f"Sticker creation failed: {e}")
            return None

# Global instance
content_service = ContentGenerationService()
content_generation_service = content_service