import os
from typing import Dict, Any

# Bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "5683837805:AAE8JpJvbunlXodMI1St60jilCe3XDC5pBQ")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA30LMlEY6HyksF7SoWhMpnOk4THZWjCOc")

# Admin configuration
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "5878958993"))

# Rate limiting configuration - ALL UNLIMITED
RATE_LIMIT_MESSAGES = 999999  # unlimited messages
RATE_LIMIT_MEDIA_DOWNLOADS = 999999  # unlimited downloads
RATE_LIMIT_BROADCASTS = 999999  # unlimited broadcasts

# File paths
USER_DATABASE_FILE = "user_database.json"
ADMIN_MESSAGES_FILE = "admin_messages.json"
DOWNLOADS_DIR = "downloads"

# Command descriptions
COMMANDS = {
    "start": "Start the bot and see welcome message",
    "help": "Show this help message with all available commands",
    "chat": "Chat with Gemini AI - unlimited conversations",
    "wiki": "Search Wikipedia for information",
    "study": "Ask educational questions (textbook level)",
    "download": "Unlimited downloads - videos/music from all platforms",
    "translate": "Translate text between languages",
    "accessibility": "Toggle accessibility mode (high-contrast, text-to-speech)",
    "speak": "Convert text to speech audio message",
    "broadcast": "Send messages to multiple users (admin only)",
    "contact": "Contact the bot administrator",
    "stats": "Show bot usage statistics (admin only)"
}

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
    'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi',
    'tr': 'Turkish', 'nl': 'Dutch', 'sv': 'Swedish', 'pl': 'Polish'
}
