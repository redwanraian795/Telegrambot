import os
import io
import logging
from typing import Optional, Dict, Any
from gtts import gTTS
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

class AccessibilityService:
    def __init__(self):
        self.user_preferences = {}  # Store accessibility preferences per user
        self.temp_dir = tempfile.gettempdir()
        
    def toggle_accessibility_mode(self, user_id: str) -> Dict[str, Any]:
        """Toggle accessibility mode for a user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'accessibility_enabled': False,
                'high_contrast': False,
                'auto_tts': False,
                'tts_language': 'en',
                'font_size': 'normal'
            }
        
        # Toggle accessibility mode
        current_mode = self.user_preferences[user_id]['accessibility_enabled']
        self.user_preferences[user_id]['accessibility_enabled'] = not current_mode
        
        if self.user_preferences[user_id]['accessibility_enabled']:
            # Enable default accessibility features
            self.user_preferences[user_id]['high_contrast'] = True
            self.user_preferences[user_id]['auto_tts'] = True
            status = "enabled"
        else:
            # Disable accessibility features
            self.user_preferences[user_id]['high_contrast'] = False
            self.user_preferences[user_id]['auto_tts'] = False
            status = "disabled"
        
        return {
            'status': status,
            'preferences': self.user_preferences[user_id]
        }
    
    def text_to_speech(self, text: str, language: str = 'en') -> Optional[str]:
        """Convert text to speech and return audio file path"""
        try:
            # Clean and prepare text
            clean_text = self._clean_text_for_tts(text)
            if not clean_text:
                return None
            
            # Create TTS object
            tts = gTTS(text=clean_text, lang=language, slow=False)
            
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, f"tts_{hash(text)}.mp3")
            tts.save(temp_file)
            
            # Convert to voice message format (optimize for Telegram)
            audio = AudioSegment.from_mp3(temp_file)
            
            # Optimize audio for voice messages
            audio = audio.set_frame_rate(16000)  # Standard voice quality
            audio = audio.set_channels(1)  # Mono
            
            # Save optimized version
            optimized_file = os.path.join(self.temp_dir, f"voice_{hash(text)}.ogg")
            audio.export(optimized_file, format="ogg", codec="libopus")
            
            # Clean up original temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return optimized_file
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return None
    
    def format_accessible_text(self, text: str, user_id: str) -> str:
        """Format text for accessibility (high contrast, clear structure)"""
        if user_id not in self.user_preferences or not self.user_preferences[user_id].get('high_contrast', False):
            return text
        
        # Apply high-contrast formatting
        formatted_text = self._apply_high_contrast_formatting(text)
        return formatted_text
    
    def _apply_high_contrast_formatting(self, text: str) -> str:
        """Apply high-contrast formatting to text"""
        # Use bold and clear separators for better visibility
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # Make headers and important text bold
                if line.startswith('#') or line.isupper() or ':' in line:
                    formatted_lines.append(f"**{line.strip()}**")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        # Add clear section separators
        formatted_text = '\n'.join(formatted_lines)
        
        # Add accessibility markers
        formatted_text = f"🔹 **ACCESSIBLE MODE** 🔹\n\n{formatted_text}\n\n━━━━━━━━━━━━━━━━━━━━"
        
        return formatted_text
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for text-to-speech conversion"""
        # Remove markdown formatting
        cleaned = text.replace('**', '').replace('*', '').replace('_', '')
        cleaned = cleaned.replace('`', '').replace('#', '')
        
        # Remove emoji and special characters that don't speak well
        import re
        cleaned = re.sub(r'[^\w\s\.,!?;:()-]', ' ', cleaned)
        
        # Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Limit length for TTS (gTTS has character limits)
        if len(cleaned) > 500:
            cleaned = cleaned[:497] + "..."
        
        return cleaned
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get accessibility preferences for a user"""
        return self.user_preferences.get(user_id, {
            'accessibility_enabled': False,
            'high_contrast': False,
            'auto_tts': False,
            'tts_language': 'en',
            'font_size': 'normal'
        })
    
    def update_user_preference(self, user_id: str, preference: str, value: Any) -> bool:
        """Update a specific accessibility preference for a user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = self.get_user_preferences(user_id)
        
        if preference in self.user_preferences[user_id]:
            self.user_preferences[user_id][preference] = value
            return True
        return False
    
    def should_auto_tts(self, user_id: str) -> bool:
        """Check if automatic TTS is enabled for user"""
        prefs = self.get_user_preferences(user_id)
        return prefs.get('accessibility_enabled', False) and prefs.get('auto_tts', False)
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        try:
            for filename in os.listdir(self.temp_dir):
                if filename.startswith(('tts_', 'voice_')) and filename.endswith(('.mp3', '.ogg')):
                    filepath = os.path.join(self.temp_dir, filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def get_accessibility_status(self, user_id: str) -> str:
        """Get formatted accessibility status for user"""
        prefs = self.get_user_preferences(user_id)
        
        if not prefs.get('accessibility_enabled', False):
            return "🔹 **Accessibility Mode: DISABLED**\n\nUse /accessibility to enable accessibility features"
        
        status_text = "🔹 **Accessibility Mode: ENABLED** 🔹\n\n"
        status_text += "**Active Features:**\n"
        
        if prefs.get('high_contrast', False):
            status_text += "• High-contrast text formatting\n"
        
        if prefs.get('auto_tts', False):
            status_text += f"• Automatic text-to-speech ({prefs.get('tts_language', 'en')})\n"
        
        status_text += f"• Font size: {prefs.get('font_size', 'normal')}\n"
        status_text += "\n**Commands:**\n"
        status_text += "• /accessibility - Toggle mode on/off\n"
        status_text += "• /speak [text] - Convert specific text to speech\n"
        
        return status_text

# Create global instance for import
accessibility_service = AccessibilityService()