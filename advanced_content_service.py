import json
import os
import asyncio
import aiohttp
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from ai_services import ai_services

class AdvancedContentService:
    """Advanced content creation with video, music, web apps, and animations"""
    
    def __init__(self):
        self.video_apis = {
            "pexels": "https://api.pexels.com/videos/search",
            "pixabay": "https://pixabay.com/api/videos/",
            "coverr": "https://api.coverr.co/videos"
        }
        self.music_apis = {
            "freesound": "https://freesound.org/apiv2/search/text/",
            "jamendo": "https://api.jamendo.com/v3.0/tracks/",
            "ccmixter": "http://ccmixter.org/api/query"
        }
        self.web_frameworks = ["react", "vue", "angular", "svelte", "vanilla"]
        self.animation_types = ["css", "javascript", "svg", "canvas", "webgl"]
    
    async def generate_video_concept(self, description: str, duration: int = 30) -> Dict[str, Any]:
        """Generate video concept and storyboard"""
        try:
            video_prompt = f"""Create a comprehensive video concept for: {description}

Duration: {duration} seconds

Provide detailed video production plan including:
1. Creative concept and theme
2. Detailed storyboard (scene by scene)
3. Shot list with camera angles
4. Visual style and color palette
5. Music and audio requirements
6. Text overlays and graphics
7. Transition effects
8. Production timeline
9. Technical specifications
10. Equipment needed

Format as professional video production document."""
            
            concept = ai_services.chat_with_ai(video_prompt, "video_concept")
            
            # Generate scene breakdown
            scenes = self._extract_scenes_from_concept(concept)
            
            return {
                'success': True,
                'description': description,
                'duration': duration,
                'concept': concept,
                'scenes': scenes,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Video concept generation failed: {str(e)}"}
    
    def _extract_scenes_from_concept(self, concept: str) -> List[Dict[str, Any]]:
        """Extract individual scenes from video concept"""
        scenes = []
        lines = concept.split('\n')
        
        scene_count = 1
        for line in lines:
            if 'scene' in line.lower() or 'shot' in line.lower():
                scenes.append({
                    'scene_number': scene_count,
                    'description': line.strip(),
                    'duration': random.randint(3, 8),
                    'camera_angle': random.choice(['wide', 'close-up', 'medium', 'overhead', 'low-angle'])
                })
                scene_count += 1
                if scene_count > 8:  # Limit scenes
                    break
        
        return scenes
    
    async def compose_music(self, style: str, mood: str, instruments: List[str] = None) -> Dict[str, Any]:
        """Generate music composition"""
        try:
            if not instruments:
                instruments = ["piano", "guitar", "drums", "bass", "strings"]
            
            music_prompt = f"""Compose original music with these specifications:

Style: {style}
Mood: {mood}
Instruments: {', '.join(instruments)}

Provide comprehensive composition including:
1. Song structure (verse, chorus, bridge, etc.)
2. Chord progressions for each section
3. Melody lines and harmonies
4. Rhythm patterns and time signature
5. Instrument arrangements
6. Dynamics and tempo changes
7. Production notes and effects
8. Lyrical themes (if applicable)
9. Audio engineering suggestions
10. Similar artist references

Create professional music notation and arrangement details."""
            
            composition = ai_services.chat_with_ai(music_prompt, "music_composition")
            
            # Generate MIDI-like representation
            midi_data = self._generate_midi_representation(style, mood, instruments)
            
            return {
                'success': True,
                'style': style,
                'mood': mood,
                'instruments': instruments,
                'composition': composition,
                'midi_representation': midi_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Music composition failed: {str(e)}"}
    
    def _generate_midi_representation(self, style: str, mood: str, instruments: List[str]) -> Dict[str, Any]:
        """Generate simplified MIDI-like data structure"""
        chord_progressions = {
            "pop": ["C", "Am", "F", "G"],
            "rock": ["E", "A", "B", "E"],
            "jazz": ["Dm7", "G7", "CMaj7", "Am7"],
            "classical": ["C", "F", "G", "C"],
            "electronic": ["Am", "F", "C", "G"]
        }
        
        tempo_map = {
            "energetic": 140,
            "calm": 80,
            "dramatic": 120,
            "upbeat": 130,
            "melancholic": 70
        }
        
        chords = chord_progressions.get(style.lower(), ["C", "F", "G", "Am"])
        tempo = tempo_map.get(mood.lower(), 120)
        
        return {
            "tempo": tempo,
            "time_signature": "4/4",
            "key": "C major",
            "chord_progression": chords,
            "structure": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
            "instruments": instruments
        }
    
    async def create_web_app(self, description: str, framework: str = "react") -> Dict[str, Any]:
        """Generate complete web application"""
        try:
            if framework not in self.web_frameworks:
                framework = "react"
            
            webapp_prompt = f"""Create a complete {framework} web application for: {description}

Generate production-ready code including:
1. Project structure and file organization
2. Main application component
3. Sub-components and modules
4. Styling (CSS/SCSS)
5. State management
6. API integration patterns
7. Routing configuration
8. Package.json with dependencies
9. Build configuration
10. Deployment instructions

Provide clean, modern, and functional code following best practices."""
            
            app_code = ai_services.chat_with_ai(webapp_prompt, "webapp_generation")
            
            # Generate file structure
            file_structure = self._create_app_file_structure(framework, description)
            
            # Save main files
            app_files = self._extract_code_files(app_code, framework)
            
            return {
                'success': True,
                'description': description,
                'framework': framework,
                'generated_code': app_code,
                'file_structure': file_structure,
                'app_files': app_files,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Web app generation failed: {str(e)}"}
    
    def _create_app_file_structure(self, framework: str, description: str) -> Dict[str, List[str]]:
        """Create typical file structure for web framework"""
        structures = {
            "react": {
                "src": ["App.js", "index.js", "App.css", "index.css"],
                "components": ["Header.js", "Footer.js", "MainContent.js"],
                "pages": ["Home.js", "About.js", "Contact.js"],
                "utils": ["api.js", "helpers.js"],
                "public": ["index.html", "favicon.ico"]
            },
            "vue": {
                "src": ["App.vue", "main.js"],
                "components": ["HelloWorld.vue", "Header.vue"],
                "views": ["Home.vue", "About.vue"],
                "router": ["index.js"],
                "store": ["index.js"]
            },
            "vanilla": {
                "": ["index.html", "style.css", "script.js"],
                "js": ["main.js", "utils.js"],
                "css": ["components.css", "responsive.css"]
            }
        }
        
        return structures.get(framework, structures["react"])
    
    def _extract_code_files(self, code: str, framework: str) -> Dict[str, str]:
        """Extract individual code files from generated code"""
        files = {}
        
        # Simple extraction based on common patterns
        if "```html" in code:
            html_start = code.find("```html") + 7
            html_end = code.find("```", html_start)
            if html_end > html_start:
                files["index.html"] = code[html_start:html_end].strip()
        
        if "```css" in code:
            css_start = code.find("```css") + 6
            css_end = code.find("```", css_start)
            if css_end > css_start:
                files["style.css"] = code[css_start:css_end].strip()
        
        if "```javascript" in code:
            js_start = code.find("```javascript") + 13
            js_end = code.find("```", js_start)
            if js_end > js_start:
                files["script.js"] = code[js_start:js_end].strip()
        
        return files
    
    async def create_animation(self, animation_type: str, description: str) -> Dict[str, Any]:
        """Generate animations in various formats"""
        try:
            if animation_type not in self.animation_types:
                animation_type = "css"
            
            animation_prompt = f"""Create a {animation_type} animation for: {description}

Generate complete animation including:
1. Animation code (CSS/JS/SVG)
2. HTML structure if needed
3. Keyframes and timing functions
4. Interactive elements
5. Performance optimizations
6. Browser compatibility
7. Customization options
8. Implementation instructions
9. Alternative variations
10. Mobile responsiveness

Provide production-ready animation code."""
            
            animation_code = ai_services.chat_with_ai(animation_prompt, "animation_generation")
            
            # Generate animation specifications
            specs = self._create_animation_specs(animation_type, description)
            
            return {
                'success': True,
                'animation_type': animation_type,
                'description': description,
                'animation_code': animation_code,
                'specifications': specs,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Animation creation failed: {str(e)}"}
    
    def _create_animation_specs(self, animation_type: str, description: str) -> Dict[str, Any]:
        """Create animation specifications"""
        return {
            "type": animation_type,
            "duration": random.choice(["0.5s", "1s", "2s", "3s"]),
            "easing": random.choice(["ease", "ease-in", "ease-out", "ease-in-out"]),
            "iterations": random.choice(["1", "2", "3", "infinite"]),
            "direction": random.choice(["normal", "reverse", "alternate"]),
            "fill_mode": random.choice(["none", "forwards", "backwards", "both"]),
            "trigger": random.choice(["hover", "click", "scroll", "load"])
        }
    
    async def generate_podcast_script(self, topic: str, duration: int = 20, hosts: int = 1) -> Dict[str, Any]:
        """Generate podcast episode script"""
        try:
            podcast_prompt = f"""Create a comprehensive podcast script for:

Topic: {topic}
Duration: {duration} minutes
Number of hosts: {hosts}

Include:
1. Episode introduction and hook
2. Host introductions and banter
3. Main content segments with timestamps
4. Transition phrases and cues
5. Interview questions (if applicable)
6. Sponsor/ad placement suggestions
7. Audience engagement moments
8. Call-to-action segments
9. Episode conclusion and next episode teaser
10. Production notes for editing

Format as professional radio/podcast script with speaker cues."""
            
            script = ai_services.chat_with_ai(podcast_prompt, "podcast_script")
            
            # Generate episode metadata
            metadata = self._create_podcast_metadata(topic, duration, hosts)
            
            return {
                'success': True,
                'topic': topic,
                'duration': duration,
                'hosts': hosts,
                'script': script,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Podcast script generation failed: {str(e)}"}
    
    def _create_podcast_metadata(self, topic: str, duration: int, hosts: int) -> Dict[str, Any]:
        """Create podcast episode metadata"""
        return {
            "episode_title": f"Deep Dive: {topic}",
            "description": f"In this {duration}-minute episode, we explore {topic}",
            "tags": topic.split()[:5],
            "category": "Education",
            "language": "en",
            "explicit": False,
            "season": 1,
            "episode_number": random.randint(1, 50),
            "publish_date": datetime.now().isoformat()
        }
    
    async def create_presentation(self, topic: str, slides: int = 10, style: str = "professional") -> Dict[str, Any]:
        """Generate complete presentation with slides"""
        try:
            presentation_prompt = f"""Create a comprehensive presentation on: {topic}

Style: {style}
Number of slides: {slides}

Generate complete presentation including:
1. Title slide with compelling headline
2. Agenda/outline slide
3. Introduction and problem statement
4. Main content slides with key points
5. Supporting data and statistics
6. Visual design suggestions
7. Slide transitions and animations
8. Speaker notes for each slide
9. Conclusion and call-to-action
10. Q&A preparation points

Format as detailed slide-by-slide breakdown with content and design notes."""
            
            presentation = ai_services.chat_with_ai(presentation_prompt, "presentation_creation")
            
            # Generate slide structure
            slide_structure = self._create_slide_structure(slides, topic)
            
            return {
                'success': True,
                'topic': topic,
                'slide_count': slides,
                'style': style,
                'presentation_content': presentation,
                'slide_structure': slide_structure,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Presentation creation failed: {str(e)}"}
    
    def _create_slide_structure(self, slide_count: int, topic: str) -> List[Dict[str, Any]]:
        """Create structured slide breakdown"""
        slides = []
        slide_types = ["title", "agenda", "content", "data", "image", "quote", "conclusion"]
        
        for i in range(slide_count):
            slide_type = slide_types[min(i, len(slide_types) - 1)]
            slides.append({
                "slide_number": i + 1,
                "type": slide_type,
                "title": f"Slide {i + 1}: {topic} - Section {i + 1}",
                "layout": random.choice(["title_content", "two_column", "image_caption", "bullet_points"]),
                "animation": random.choice(["fade", "slide", "zoom", "none"])
            })
        
        return slides

# Global instance
advanced_content_service = AdvancedContentService()