import os
import speech_recognition as sr
from gtts import gTTS
import tempfile
from pydub import AudioSegment
import io
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
    
    def transcribe_voice_message(self, audio_file_path: str, language: str = 'en') -> Optional[str]:
        """Convert voice message to text"""
        try:
            # Convert audio to WAV format if needed
            audio = AudioSegment.from_file(audio_file_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                audio.export(temp_wav.name, format='wav')
                
                # Transcribe audio
                with sr.AudioFile(temp_wav.name) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language=language)
                
                # Clean up temp file
                os.unlink(temp_wav.name)
                
                return text
                
        except Exception as e:
            logger.error(f"Voice transcription error: {e}")
            return None
    
    def create_voice_response(self, text: str, language: str = 'en', accent: str = None) -> Optional[str]:
        """Generate voice response with different accents"""
        try:
            # Language mapping for accents
            accent_mapping = {
                'en': ['com', 'co.uk', 'com.au', 'ca'],  # US, UK, AU, CA
                'es': ['es', 'com.mx'],  # Spain, Mexico
                'fr': ['fr', 'ca'],  # France, Canada
                'pt': ['com.br', 'pt']  # Brazil, Portugal
            }
            
            # Select TLD based on accent preference
            tld = 'com'  # Default
            if accent and language in accent_mapping:
                accent_options = accent_mapping[language]
                if accent.lower() in ['uk', 'british'] and 'co.uk' in accent_options:
                    tld = 'co.uk'
                elif accent.lower() in ['au', 'australian'] and 'com.au' in accent_options:
                    tld = 'com.au'
                elif accent.lower() in ['ca', 'canadian'] and 'ca' in accent_options:
                    tld = 'ca'
                elif accent.lower() in ['mx', 'mexican'] and 'com.mx' in accent_options:
                    tld = 'com.mx'
                elif accent.lower() in ['br', 'brazilian'] and 'com.br' in accent_options:
                    tld = 'com.br'
            
            # Generate TTS
            tts = gTTS(text=text, lang=language, tld=tld, slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Voice generation error: {e}")
            return None
    
    def get_supported_languages(self) -> str:
        """Get formatted list of supported languages"""
        lang_list = []
        for code, name in self.supported_languages.items():
            lang_list.append(f"• {name} ({code})")
        
        return "🎤 **Supported Voice Languages:**\n" + "\n".join(lang_list)
    
    def get_accent_options(self, language: str) -> str:
        """Get available accent options for a language"""
        accent_info = {
            'en': "🇺🇸 US (default), 🇬🇧 UK, 🇦🇺 AU, 🇨🇦 CA",
            'es': "🇪🇸 Spain (default), 🇲🇽 Mexico", 
            'fr': "🇫🇷 France (default), 🇨🇦 Canada",
            'pt': "🇵🇹 Portugal (default), 🇧🇷 Brazil"
        }
        
        return accent_info.get(language, "Default accent only")
    
    def cleanup_temp_files(self):
        """Clean up temporary voice files"""
        try:
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.endswith(('.mp3', '.wav')) and file.startswith('tmp'):
                    file_path = os.path.join(temp_dir, file)
                    # Remove files older than 1 hour
                    if os.path.getctime(file_path) < (time.time() - 3600):
                        os.remove(file_path)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")