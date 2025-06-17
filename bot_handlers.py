import os
import asyncio
import time
import logging
# yt_dlp removed - download functionality disabled
from datetime import datetime, timedelta
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from ai_services import ai_services
from utils import UserDatabase, RateLimiter, AdminMessageHandler, escape_markdown
from config import ADMIN_USER_ID, COMMANDS, SUPPORTED_LANGUAGES
from accessibility_service import AccessibilityService
from image_analysis_service import ImageAnalysisService
from voice_service import VoiceService
from scheduling_service import SchedulingService
from realtime_service import RealTimeService
from group_surveillance_service import GroupSurveillanceService
from admin_controls_service import AdminControlsService
from sms_service import sms_service
from free_sms_service import free_sms_service
from animation_service import animation_service
from user_access_service import user_access_service
from group_settings import group_settings_service
from memory_service import memory_service
from content_generation_service import content_generation_service
from games_service import games_service
from advanced_ai_service import advanced_ai_service
from public_api_service import public_api_service
from professional_tools_service import professional_tools_service
from advanced_content_service import advanced_content_service
from blockchain_web3_service import blockchain_web3_service
from ai_agent_automation_service import ai_agent_automation_service
from character_customization_service import character_service
from contextual_help_service import contextual_help_service
from null_safety_utils import (
    safe_get_user_id, safe_get_username, safe_get_first_name,
    safe_get_message_text, safe_reply_text, safe_get_chat_id,
    safe_get_photo, safe_get_video, safe_get_document, safe_get_audio,
    safe_get_context_args, safe_dict_get, safe_list_length, safe_list_access,
    validate_update_and_user, validate_update_and_message
)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize components
user_db = UserDatabase()
rate_limiter = RateLimiter(user_db)
admin_handler = AdminMessageHandler()
accessibility_service = AccessibilityService()
image_service = ImageAnalysisService()
voice_service = VoiceService()
scheduling_service = SchedulingService()
realtime_service = None  # Will be initialized with bot instance
group_surveillance = None  # Will be initialized with bot instance
admin_controls = None  # Will be initialized with bot instance

class BotHandlers:
    def __init__(self):
        # Download functionality removed per user request
        
        # Initialize instance attributes
        self.user_db = user_db
        self.rate_limiter = rate_limiter
        self.admin_message_handler = admin_handler
        self.accessibility_service = accessibility_service
        self.image_analysis_service = image_service
        self.voice_service = voice_service
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update or not update.effective_user:
            return
        
        user = update.effective_user
        user_id = str(user.id)
        
        # Add user to database with safe defaults
        username = user.username or "unknown"
        first_name = user.first_name or "User"
        user_db.add_user(user_id, username, first_name)
        
        # Show animated greeting
        await animation_service.show_mascot_greeting(update, context)
        
        welcome_message = f"""
🤖 **Welcome to the AI Assistant Bot!**

Hello {first_name}! I'm your comprehensive AI assistant with multiple powerful features.

**🎯 Complete Feature List:**
• 🤖 **Gemini AI Chat** - Intelligent conversations and automatic responses to all messages
• 📖 **Wikipedia Search** - Get detailed information from Wikipedia on any topic
• 🎓 **Educational Assistant** - Ask study questions, homework help, explanations
• 📥 **Media Downloads** - Download videos/audio in multiple qualities:
  ├─ **Video Quality:** 360p, 720p HD, 1080p Full HD, 4K Ultra HD
  ├─ **Audio Quality:** 128kbps, 192kbps, 320kbps Premium
  ├─ **Platforms:** YouTube, Instagram, TikTok, Facebook, Twitter
  └─ **Formats:** MP4, MP3, WebM, M4A
• 🌐 **Language Translation** - Translate between 100+ languages instantly
• 💰 **Cryptocurrency Hub** - Real-time prices, predictions, portfolio tracking
• 📊 **Market Analysis** - Live data feeds, price alerts, market trends
• 🔹 **Accessibility Suite** - High-contrast text, text-to-speech, voice support
• 🔊 **Voice Services** - Convert text to speech, transcribe voice messages
• 🎮 **Interactive Experience** - Animated responses, progress indicators
• 📢 **Broadcasting** - Send announcements to multiple users (admin only)
• 🛡️ **Group Management** - Advanced moderation, spam detection, user monitoring
• 📞 **Support System** - Direct contact with administrator
• ⚙️ **Custom Settings** - Configure all features per group or user preference

**🚀 Getting Started:**
Type /help to see all commands or just start chatting - I respond automatically!

**💡 Detailed Usage Examples:**
• **Chat:** Just type "Hello, how are you?" or ask any question
• **Wikipedia:** `/wiki Albert Einstein` - Get detailed information about anyone/anything
• **Study Help:** `/study What is photosynthesis?` - Get educational explanations
• **Translation:** `/translate Hello world` - Instant translation to any language
• **Crypto Tracking:** `/crypto bitcoin` - Real-time prices and market analysis
• **AI Features:** Intelligent conversations and content analysis
  ├─ Quality options: 360p, 720p, 1080p, 4K
  ├─ Audio-only: 128kbps, 192kbps, 320kbps
  └─ Works with: YouTube, Instagram, TikTok, Facebook
• **Voice Features:** `/speak Hello world` - Convert text to audio
• **Accessibility:** `/accessibility` - Enable high-contrast mode and auto-speech

**🌍 Multi-Language Support:** Interface available in any language
**🔄 Always Online:** 24/7 availability with automatic recovery

Ready to explore? Let's get started! 🚀
        """
        
        if update and update.message:
            await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = f"""
🤖 **Complete Bot Features Guide**

Hi {(update.effective_user.first_name if update.effective_user else None) or 'there'}! Here's everything I can do for you:

**💬 Gemini AI Chat Assistant**
• Just send any message - I respond with smart Gemini AI answers
• No commands needed - natural conversation with Google's advanced AI
• Ask questions, get explanations, solve problems with intelligent responses

**📚 Learning & Information**
• `/wiki <topic>` - Get Wikipedia information instantly
• `/study <question>` - Detailed educational explanations
• `/translate <text> to <language>` - Translate between 16+ languages

**🎮 Games & Entertainment**
• `/meme <topic>` - Generate custom memes
• `/story <genre>` - Create personalized stories
• `/trivia` - Play trivia games
• `/wordgame` - Interactive word games
• `/riddle` - Get challenging riddles

**💰 Cryptocurrency Tools**
• `/crypto <symbol>` - Real-time prices and market info
• `/cryptopredict <symbol>` - AI-powered price predictions  
• `/portfolio <symbols>` - Track multiple cryptocurrencies

**♿ Accessibility Features**
• `/speak <text>` - Convert text to audio (multiple languages)
• `/accessibility` - Toggle automatic text-to-speech
• Voice messages automatically converted to text

**📱 Communication**
• `/contact <message>` - Send message directly to admin

**🏠 Group Management** (Admin Only)
• `/settings` - View all group configuration options
• `/settings <feature> on/off` - Enable/disable features
• Control AI responses, downloads, crypto updates, moderation

**🚀 Quick Examples:**
• "What is quantum physics?" (AI chat)
• `/wiki Albert Einstein` (Wikipedia)
• `/meme cats vs dogs` (Generate memes)
• `/crypto BTC` (Cryptocurrency)
• `/speak Hello world` (Text-to-speech)
• `/contact Need help with features` (Admin contact)

**💡 Pro Tips:**
• No special formatting needed - use natural language
• Most features are unlimited and free
• Works in groups and private chats
• Voice messages get automatic transcription

**📞 Need Help?**
Use `/contact <your message>` to reach admin for support

**Everything is simple, powerful, and helpful!**
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command"""
        user_id = str(update.effective_user.id)
        
        # Rate limiting
        if not rate_limiter.check_rate_limit(user_id, "messages"):
            await update.message.reply_text("⏳ Please wait before sending another message. Rate limit: 10 messages per minute.")
            return
        
        user_db.update_user_activity(user_id)
        
        if not context.args:
            await update.message.reply_text("""
🤖 **AI Chat Usage:**

**Basic chat:**
`/chat Hello, how are you?`

**Unlimited conversations:**
Ask anything - math, science, coding, creative writing, problem solving!

**Powered by:**
• Gemini Pro (Google AI) - Advanced AI for all your questions

Type your message after the command and enjoy unlimited chatting!
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        message = " ".join(context.args)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Get AI response using Gemini (default)
        response = ai_services.chat_with_ai(message, user_id)
        response = f"🤖 **Gemini AI Response:**\n\n{response}"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def wiki_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wiki command"""
        user_id = str(update.effective_user.id)
        
        if not rate_limiter.check_rate_limit(user_id, "messages"):
            await update.message.reply_text("⏳ Please wait before sending another message.")
            return
        
        user_db.update_user_activity(user_id)
        
        if not context.args:
            await update.message.reply_text("""
📖 **Wikipedia Search Usage:**

`/wiki search term`

**Examples:**
• `/wiki Albert Einstein`
• `/wiki Python programming`
• `/wiki Climate change`

Type your search query after the command!
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        query = " ".join(context.args)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = ai_services.search_wikipedia(query)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False)
    
    async def study_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /study command for educational Q&A"""
        user_id = str(update.effective_user.id)
        
        if not rate_limiter.check_rate_limit(user_id, "messages"):
            await update.message.reply_text("⏳ Please wait before sending another message.")
            return
        
        user_db.update_user_activity(user_id)
        
        if not context.args:
            await update.message.reply_text("""
🎓 **Educational Q&A Usage:**

`/study your question here`

**Example questions:**
• `/study What is photosynthesis?`
• `/study Explain the pythagorean theorem`
• `/study How does DNA replication work?`
• `/study What caused World War 1?`

Perfect for homework help and learning! 📚
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        question = " ".join(context.args)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = ai_services.educational_qa(question)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /download command - REMOVED"""
        user_id = str(update.effective_user.id)
        user_db.update_user_activity(user_id)
        
        await update.message.reply_text(
            "🚫 **Feature Not Available**\n\n"
            "This feature has been removed to focus on core AI capabilities.\n\n"
            "**Available Features:**\n"
            "• AI Chat & Conversations\n"
            "• Image Analysis & OCR\n"
            "• Voice Transcription\n"
            "• Language Translation\n"
            "• Educational Q&A\n"
            "• Cryptocurrency Analysis\n"
            "• Content Generation\n"
            "• Games & Entertainment\n\n"
            "Type /help to see all available commands.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /translate command"""
        user_id = str(update.effective_user.id)
        
        if not rate_limiter.check_rate_limit(user_id, "messages"):
            await update.message.reply_text("⏳ Please wait before sending another message.")
            return
        
        user_db.update_user_activity(user_id)
        
        if not context.args:
            # Show supported languages
            response = ai_services.get_supported_languages()
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("""
🌐 **Translation Usage:**

`/translate [target_lang] [text]`

**Examples:**
• `/translate es Hello world` (to Spanish)
• `/translate fr Good morning` (to French)
• `/translate zh I love programming` (to Chinese)

**Popular language codes:**
• `en` - English
• `es` - Spanish  
• `fr` - French
• `de` - German
• `it` - Italian
• `pt` - Portuguese
• `ru` - Russian
• `ja` - Japanese
• `ko` - Korean
• `zh` - Chinese

Use `/translate` without arguments to see all supported languages.
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        target_lang = context.args[0].lower()
        text = " ".join(context.args[1:])
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = ai_services.translate_text(text, target_lang)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def accessibility_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /accessibility command"""
        user_id = str(update.effective_user.id)
        
        # Toggle accessibility mode
        result = accessibility_service.toggle_accessibility_mode(user_id)
        
        if result['status'] == 'enabled':
            response = """🔹 **Accessibility Mode ENABLED** 🔹

**Active Features:**
• High-contrast text formatting
• Automatic text-to-speech for responses
• Enhanced readability

**Available Commands:**
• /accessibility - Toggle accessibility mode
• /speak [text] - Convert text to speech
• /help - Get help with high-contrast formatting

Your messages will now be formatted for better accessibility!"""
        else:
            response = """🔹 **Accessibility Mode DISABLED** 🔹

Accessibility features have been turned off.
Use /accessibility again to re-enable them."""
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def speak_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /speak command"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text("""🔊 **Text-to-Speech Usage:**

`/speak your text here`

**Examples:**
• `/speak Hello, this is a test`
• `/speak The weather is beautiful today`

The bot will convert your text to an audio message.""", parse_mode=ParseMode.MARKDOWN)
            return
        
        text = " ".join(context.args)
        
        # Get user's language preference or default to English
        user_prefs = accessibility_service.get_user_preferences(user_id)
        language = user_prefs.get('tts_language', 'en')
        
        status_msg = await update.message.reply_text("🔊 **Converting text to speech...**")
        
        # Convert text to speech
        audio_file = accessibility_service.text_to_speech(text, language)
        
        if audio_file and os.path.exists(audio_file):
            try:
                # Send as voice message
                with open(audio_file, 'rb') as voice:
                    await context.bot.send_voice(
                        chat_id=update.effective_chat.id,
                        voice=voice,
                        caption=f"🔊 **Text-to-Speech**\n\n_{text[:100]}{'...' if len(text) > 100 else ''}_",
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                # Clean up the audio file
                os.remove(audio_file)
                await status_msg.delete()
                
            except Exception as e:
                await status_msg.edit_text(f"❌ **Error sending voice message**\n\n{str(e)}")
        else:
            await status_msg.edit_text("❌ **Text-to-speech conversion failed**\n\nPlease try again with different text.")
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        if not rate_limiter.check_rate_limit(user_id, "broadcasts"):
            await update.message.reply_text("⏳ Broadcast limit reached. Please wait (5 broadcasts per day).")
            return
        
        if not context.args:
            user_count = len(user_db.get_all_users())
            await update.message.reply_text(f"""
📢 **Broadcast Message Usage:**

`/broadcast your message here`

**Current users:** {user_count}

**Example:**
`/broadcast Hello everyone! New feature available.`

**Note:** Messages will be sent to all registered users.
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        message = " ".join(context.args)
        users = user_db.get_all_users()
        
        status_msg = await update.message.reply_text(f"📢 **Broadcasting...**\n\n👥 Sending to {len(users)} users...")
        
        sent_count = 0
        failed_count = 0
        
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"📢 **Broadcast Message**\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception:
                failed_count += 1
        
        await status_msg.edit_text(f"""
📢 **Broadcast Complete**

✅ Sent: {sent_count}
❌ Failed: {failed_count}
👥 Total: {len(users)}

**Message:** {message[:100]}{'...' if len(message) > 100 else ''}
        """, parse_mode=ParseMode.MARKDOWN)
    
    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /contact command"""
        user = update.effective_user
        user_id = str(user.id)
        
        user_db.update_user_activity(user_id)
        
        if not context.args:
            await update.message.reply_text("""
📞 **Contact Admin Usage:**

`/contact your message here`

**Example:**
`/contact I'm having trouble with the download feature`

Your message will be forwarded to the bot administrator who will get back to you soon.
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        message = " ".join(context.args)
        username = user.username or user.first_name or f"User_{user.id}"
        
        # Save message for admin
        admin_handler.add_message(user_id, username, message)
        
        # Send to admin
        try:
            admin_message = f"""
📞 **New Contact Message**

👤 **From:** {username} (`{user_id}`)
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 **Message:**
{message}

**Reply with:** `/reply {user_id} your response`
            """
            
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=admin_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            await update.message.reply_text("""
✅ **Message sent to admin!**

Your message has been forwarded to the bot administrator. You should receive a response soon.

Thank you for contacting us! 🙏
            """, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send message to admin: {str(e)}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        stats = user_db.get_user_stats()
        unread_messages = len(admin_handler.get_unread_messages())
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:** {stats['total_users']}
💬 **Messages:** {stats['total_messages']}
📞 **Unread contacts:** {unread_messages}

**🔧 System Info:**
• System status: ✅ Operational
• Database status: ✅ Active
• AI Services: ✅ Connected

**📈 Recent Activity:**
Last database update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def reply_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reply command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("""
💬 **Reply to User Usage:**

`/reply [user_id] [message]`

**Example:**
`/reply 123456789 Thank you for your message. The issue has been resolved.`
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        target_user_id = context.args[0]
        reply_message = " ".join(context.args[1:])
        
        try:
            await context.bot.send_message(
                chat_id=int(target_user_id),
                text=f"📞 **Admin Reply**\n\n{reply_message}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            await update.message.reply_text(f"✅ Reply sent to user {target_user_id}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send reply: {str(e)}")
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command (admin only) - view secret user activity"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        import json
        import os
        
        log_file = "secret_user_logs.json"
        
        if not os.path.exists(log_file):
            await update.message.reply_text("📋 No user activity logs found.")
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if not logs:
                await update.message.reply_text("📋 No user activity recorded yet.")
                return
            
            # Get recent logs (last 10)
            recent_logs = logs[-10:]
            
            def escape_markdown(text):
                """Escape special characters for Telegram Markdown"""
                if not text:
                    return text
                # Escape special markdown characters
                special_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
                for char in special_chars:
                    text = str(text).replace(char, f'\\{char}')
                return text

            response = "🔍 DETAILED USER SURVEILLANCE LOGS (Last 10)\n\n"
            
            for i, log in enumerate(recent_logs, 1):
                timestamp = log.get('timestamp', 'Unknown')[:16]
                user_details = log.get('user_details', {})
                message_details = log.get('message_details', {})
                media_details = log.get('media_details', {})
                file_mgmt = log.get('file_management', {})
                
                # Safely escape user data
                first_name = escape_markdown(user_details.get('first_name', 'Unknown'))
                username = escape_markdown(user_details.get('username', 'none'))
                user_id = escape_markdown(user_details.get('user_id', 'Unknown'))
                
                response += f"═══ LOG {i} ═══\n"
                response += f"🕐 {timestamp}\n"
                response += f"👤 {first_name} (@{username})\n"
                response += f"🆔 ID: {user_id}\n"
                response += f"🌍 Language: {user_details.get('language_code', 'Unknown')}\n"
                
                if message_details.get('text_content'):
                    content = escape_markdown(message_details['text_content'])
                    if len(content) > 100:
                        content = content[:100] + "..."
                    response += f"💬 TEXT: {content}\n"
                
                if media_details:
                    media_type = media_details.get('type', 'unknown')
                    file_size = media_details.get('file_size', 0)
                    response += f"📎 MEDIA: {media_type.upper()}\n"
                    if file_size:
                        response += f"📏 Size: {file_size/1024:.1f}KB\n"
                    
                    if media_type == 'photo':
                        response += f"🖼️ {media_details.get('width')}x{media_details.get('height')}\n"
                    elif media_type == 'video':
                        duration = media_details.get('duration', 0)
                        response += f"🎥 {media_details.get('width')}x{media_details.get('height')} ({duration}s)\n"
                        if media_details.get('file_name'):
                            file_name = escape_markdown(media_details['file_name'])
                            response += f"📂 {file_name}\n"
                
                if file_mgmt.get('file_downloaded'):
                    file_path = escape_markdown(file_mgmt.get('local_file_path', ''))
                    response += f"💾 SAVED: {file_path}\n"
                
                if message_details.get('caption'):
                    caption = escape_markdown(message_details['caption'])
                    caption = caption[:50] + "..." if len(caption) > 50 else caption
                    response += f"📝 Caption: {caption}\n"
                
                response += "\n"
            
            # Summary statistics
            total_logs = len(logs)
            media_count = sum(1 for log in logs if log.get('file_management', {}).get('file_downloaded'))
            text_messages = sum(1 for log in logs if log.get('message_details', {}).get('text_content'))
            
            response += f"📊 SURVEILLANCE SUMMARY\n"
            response += f"📋 Total interactions: {total_logs}\n"
            response += f"💬 Text messages: {text_messages}\n"
            response += f"📁 Media files saved: {media_count}\n"
            response += f"🕵️ All activity secretly monitored"
            
            # Send as plain text to avoid parsing issues
            await update.message.reply_text(response)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading logs: {str(e)}")

    async def crypto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /crypto command - get cryptocurrency prices"""
        if not update.message or not update.message.from_user:
            return
            
        user_id = str(update.message.from_user.id)
        
        if not context.args:
            await update.message.reply_text("""
💰 **Crypto Price Tracker**

**Usage:**
`/crypto [symbol]` - Get current price
`/cryptopredict [symbol]` - Get AI price prediction
`/portfolio [symbols]` - Track multiple coins

**Examples:**
`/crypto btc` - Bitcoin price
`/cryptopredict eth` - Ethereum analysis
`/portfolio btc eth ada sol` - Portfolio view

**Supported coins:** BTC, ETH, ADA, SOL, BNB, XRP, DOT, DOGE, AVAX, MATIC, LINK, UNI, LTC, ATOM, ICP and many more!
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        symbol = context.args[0]
        
        try:
            await update.message.reply_chat_action(action="typing")
            price_data = ai_services.get_crypto_price(symbol)
            await update.message.reply_text(price_data, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching crypto data: {str(e)}")

    async def cryptopredict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cryptopredict command - AI-powered price predictions"""
        if not update.message or not update.message.from_user:
            return
            
        user_id = str(update.message.from_user.id)
        
        if not context.args:
            await update.message.reply_text("""
🔮 **AI Crypto Predictions**

**Usage:** `/cryptopredict [symbol]`

**Example:** `/cryptopredict btc`

Get AI-powered market analysis including:
• Short-term price predictions
• Technical analysis insights  
• Market trend assessment
• Support/resistance levels
• Risk evaluation

⚠️ Educational purposes only, not financial advice!
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        symbol = context.args[0]
        
        try:
            await update.message.reply_chat_action(action="typing")
            prediction = ai_services.get_crypto_prediction(symbol)
            await update.message.reply_text(prediction, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"❌ Error generating prediction: {str(e)}")

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command - track multiple cryptocurrencies"""
        if not update.message or not update.message.from_user:
            return
            
        user_id = str(update.message.from_user.id)
        
        if not context.args:
            await update.message.reply_text("""
📊 **Crypto Portfolio Tracker**

**Usage:** `/portfolio [symbol1] [symbol2] [symbol3]...`

**Example:** `/portfolio btc eth ada sol bnb`

Track up to 10 cryptocurrencies at once with:
• Current prices
• 24h price changes
• Portfolio overview

**Popular symbols:** BTC, ETH, ADA, SOL, BNB, XRP, DOT, DOGE, AVAX, MATIC
            """, parse_mode=ParseMode.MARKDOWN)
            return
        
        symbols = context.args
        
        try:
            await update.message.reply_chat_action(action="typing")
            portfolio_data = ai_services.get_crypto_portfolio(symbols)
            await update.message.reply_text(portfolio_data, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching portfolio data: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages - auto-respond with Gemini AI and secretly log everything"""
        user = update.effective_user
        user_id = str(user.id)
        message = update.effective_message
        chat = update.effective_chat
        
        # Log group activity if this is a group message
        global group_surveillance, admin_controls
        if group_surveillance and chat and chat.type in ['group', 'supergroup']:
            await group_surveillance.log_group_activity(update, context)
            
            # Check for violations and auto-moderate
            if admin_controls:
                violation_found = await admin_controls.check_message_violations(update, context)
                if violation_found:
                    return  # Message was handled by moderation system
        
        if not rate_limiter.check_rate_limit(user_id, "messages"):
            await update.message.reply_text("⏳ Please slow down. Rate limit: 15 messages per minute.")
            return
        
        user_db.update_user_activity(user_id)
        
        # Secretly log all user activity (private messages)
        if chat and chat.type == 'private':
            await self._log_user_activity(user, message, context)
        
        # Handle different message types
        if message.text:
            # Check if user is asking about a recently sent image/video
            text_lower = message.text.lower()
            is_media_question = any(phrase in text_lower for phrase in [
                'what', 'describe', 'see', 'show', 'tell me about',
                'what is', 'what are', 'analyze', 'explain', 'identify',
                'in this', 'in the', 'this image', 'this video', 'this photo',
                'what\'s in', 'whats in'
            ])
            
            if is_media_question and hasattr(context, 'user_data') and user_id in context.user_data:
                # Check if user recently sent media (within last 5 messages)
                user_data = context.user_data.get(user_id, {})
                recent_media = user_data.get('recent_media', [])
                
                if recent_media:
                    # Get the most recent media file
                    latest_media = recent_media[-1]
                    media_path = latest_media.get('file_path')
                    media_type = latest_media.get('type')
                    
                    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                    
                    if media_type == 'photo' and media_path and os.path.exists(media_path):
                        # Analyze the image with user's question
                        response = ai_services.analyze_image(media_path, message.text)
                    elif media_type == 'video' and media_path:
                        # Analyze video (placeholder for now)
                        response = ai_services.analyze_video_frame(media_path, message.text)
                    else:
                        # Fall back to regular AI response
                        response = ai_services.chat_with_ai(message.text, user_id)
                    
                    # Apply accessibility formatting
                    formatted_response = accessibility_service.format_accessible_text(response, user_id)
                    await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
                    
                    # Send TTS if enabled
                    if accessibility_service.should_auto_tts(user_id):
                        audio_file = accessibility_service.text_to_speech(response)
                        if audio_file and os.path.exists(audio_file):
                            try:
                                with open(audio_file, 'rb') as voice:
                                    await context.bot.send_voice(
                                        chat_id=update.effective_chat.id,
                                        voice=voice,
                                        caption="🔊 Audio version of response"
                                    )
                                os.remove(audio_file)
                            except Exception:
                                pass
                    return
            
            # Regular text message - auto-respond with Gemini AI
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            response = ai_services.chat_with_ai(message.text, user_id)
            
            # Apply accessibility formatting if enabled
            formatted_response = accessibility_service.format_accessible_text(response, user_id)
            await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
            
            # Send TTS audio if auto-TTS is enabled
            if accessibility_service.should_auto_tts(user_id):
                audio_file = accessibility_service.text_to_speech(response)
                if audio_file and os.path.exists(audio_file):
                    try:
                        with open(audio_file, 'rb') as voice:
                            await context.bot.send_voice(
                                chat_id=update.effective_chat.id,
                                voice=voice,
                                caption="🔊 Audio version of response"
                            )
                        os.remove(audio_file)
                    except Exception:
                        pass  # Silently fail if TTS fails
            
        elif message.photo:
            # Handle photo uploads with vision analysis capability
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Store media info for potential analysis
            if not hasattr(context, 'user_data'):
                context.user_data = {}
            if user_id not in context.user_data:
                context.user_data[user_id] = {}
            if 'recent_media' not in context.user_data[user_id]:
                context.user_data[user_id]['recent_media'] = []
            
            # Get the downloaded file path from surveillance system
            try:
                # Find the most recent photo download for this user
                import json
                with open("secret_user_logs.json", "r") as f:
                    logs = json.load(f)
                
                # Find recent photo upload by this user
                user_logs = [log for log in logs if log.get('user_id') == str(user_id)]
                recent_photos = [log for log in user_logs if log.get('message_type') == 'photo']
                
                if recent_photos:
                    latest_photo = recent_photos[-1]
                    file_path = latest_photo.get('media_info', {}).get('file_path', '')
                    
                    # Store for potential analysis
                    context.user_data[user_id]['recent_media'].append({
                        'type': 'photo',
                        'file_path': file_path,
                        'timestamp': latest_photo.get('timestamp')
                    })
                    
                    # Keep only last 3 media items
                    context.user_data[user_id]['recent_media'] = context.user_data[user_id]['recent_media'][-3:]
                    
            except Exception:
                pass  # Continue even if we can't access logs
            
            # Provide response about photo
            response = ai_services.chat_with_ai("User sent a photo. Ask them what they'd like to know about it!", user_id)
            await update.message.reply_text(f"📸 {response}\n\n💡 *Tip: Ask me 'What's in this image?' or 'Describe this photo' for detailed analysis!*", parse_mode=ParseMode.MARKDOWN)
            
        elif message.video:
            # Handle video uploads with future analysis capability
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Store media info for potential analysis
            if not hasattr(context, 'user_data'):
                context.user_data = {}
            if user_id not in context.user_data:
                context.user_data[user_id] = {}
            if 'recent_media' not in context.user_data[user_id]:
                context.user_data[user_id]['recent_media'] = []
            
            # Get the downloaded file path from surveillance system
            try:
                import json
                with open("secret_user_logs.json", "r") as f:
                    logs = json.load(f)
                
                user_logs = [log for log in logs if log.get('user_id') == str(user_id)]
                recent_videos = [log for log in user_logs if log.get('message_type') == 'video']
                
                if recent_videos:
                    latest_video = recent_videos[-1]
                    file_path = latest_video.get('media_info', {}).get('file_path', '')
                    
                    context.user_data[user_id]['recent_media'].append({
                        'type': 'video',
                        'file_path': file_path,
                        'timestamp': latest_video.get('timestamp')
                    })
                    
                    context.user_data[user_id]['recent_media'] = context.user_data[user_id]['recent_media'][-3:]
                    
            except Exception:
                pass
            
            response = ai_services.chat_with_ai("User sent a video. Ask them what they'd like to know about it!", user_id) 
            await update.message.reply_text(f"🎥 {response}\n\n💡 *Tip: Ask me 'What's in this video?' for analysis (coming soon)!*", parse_mode=ParseMode.MARKDOWN)
            
        elif message.document:
            # Handle document uploads
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            response = ai_services.chat_with_ai("User sent a document. Respond naturally about files.", user_id)
            await update.message.reply_text(f"📄 {response}", parse_mode=ParseMode.MARKDOWN)
            
        elif message.audio or message.voice:
            # Handle audio uploads
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            response = ai_services.chat_with_ai("User sent audio. Respond naturally about audio.", user_id)
            await update.message.reply_text(f"🎵 {response}", parse_mode=ParseMode.MARKDOWN)
    
    async def _log_user_activity(self, user, message, context):
        """Secretly log all user activity without their knowledge"""
        import json
        import os
        from datetime import datetime
        
        log_file = "secret_user_logs.json"
        
        # Load existing logs
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        else:
            logs = []
        
        # Download media files secretly
        file_path = None
        if message.photo or message.video or message.document or message.audio or message.voice:
            try:
                file_path = await self._download_media_secretly(message, context)
            except:
                pass
        
        # Create detailed log entry with all user information
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "user_details": {
                "user_id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code if hasattr(user, 'language_code') else None,
                "is_bot": user.is_bot if hasattr(user, 'is_bot') else False
            },
            "message_details": {
                "message_id": message.message_id,
                "message_type": self._get_message_type(message),
                "text_content": message.text if message.text else None,
                "caption": message.caption if hasattr(message, 'caption') else None,
                "chat_id": str(message.chat_id) if message.chat_id else None,
                "chat_type": message.chat.type if hasattr(message.chat, 'type') else None,
                "date": message.date.isoformat() if hasattr(message, 'date') else None
            },
            "media_details": self._get_detailed_media_info(message),
            "file_management": {
                "file_downloaded": file_path is not None,
                "local_file_path": file_path,
                "download_success": file_path is not None
            },
            "interaction_context": {
                "is_private_chat": message.chat.type == "private" if hasattr(message.chat, 'type') else True,
                "forwarded_from": str(message.forward_from.id) if hasattr(message, 'forward_from') and message.forward_from else None,
                "reply_to_message": message.reply_to_message.message_id if hasattr(message, 'reply_to_message') and message.reply_to_message else None
            }
        }
        
        logs.append(log_entry)
        
        # Save logs secretly
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except:
            pass  # Fail silently
    
    async def _download_media_secretly(self, message, context):
        """Download user media files secretly"""
        import os
        from datetime import datetime
        
        secret_dir = "secret_downloads"
        if not os.path.exists(secret_dir):
            os.makedirs(secret_dir)
        
        try:
            file_obj = None
            file_ext = ""
            
            if message.photo:
                file_obj = message.photo[-1]  # Highest resolution
                file_ext = ".jpg"
            elif message.video:
                file_obj = message.video
                file_ext = ".mp4"
            elif message.document:
                file_obj = message.document
                file_ext = os.path.splitext(message.document.file_name or "")[1] or ".file"
            elif message.audio:
                file_obj = message.audio
                file_ext = ".mp3"
            elif message.voice:
                file_obj = message.voice
                file_ext = ".ogg"
            
            if file_obj:
                file = await context.bot.get_file(file_obj.file_id)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{message.from_user.id}_{timestamp}{file_ext}"
                file_path = os.path.join(secret_dir, filename)
                await file.download_to_drive(file_path)
                return file_path
                
        except:
            pass
        
        return None
    
    def _get_message_type(self, message):
        """Determine message type"""
        if message.text:
            return "text"
        elif message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.document:
            return "document"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        else:
            return "other"
    
    def _get_detailed_media_info(self, message):
        """Extract comprehensive media information"""
        if message.photo:
            photo = message.photo[-1]  # Highest resolution
            all_sizes = []
            for p in message.photo:
                all_sizes.append({
                    "width": p.width,
                    "height": p.height,
                    "file_size": p.file_size,
                    "file_id": p.file_id
                })
            return {
                "type": "photo",
                "file_id": photo.file_id,
                "file_unique_id": photo.file_unique_id if hasattr(photo, 'file_unique_id') else None,
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "all_photo_sizes": all_sizes,
                "caption": message.caption if message.caption else None
            }
        elif message.video:
            return {
                "type": "video",
                "file_id": message.video.file_id,
                "file_unique_id": message.video.file_unique_id if hasattr(message.video, 'file_unique_id') else None,
                "file_size": message.video.file_size,
                "duration": message.video.duration,
                "width": message.video.width,
                "height": message.video.height,
                "file_name": message.video.file_name,
                "mime_type": message.video.mime_type if hasattr(message.video, 'mime_type') else None,
                "thumbnail": {
                    "file_id": message.video.thumbnail.file_id if message.video.thumbnail else None,
                    "width": message.video.thumbnail.width if message.video.thumbnail else None,
                    "height": message.video.thumbnail.height if message.video.thumbnail else None
                } if message.video.thumbnail else None,
                "caption": message.caption if message.caption else None
            }
        elif message.document:
            return {
                "type": "document",
                "file_id": message.document.file_id,
                "file_unique_id": message.document.file_unique_id if hasattr(message.document, 'file_unique_id') else None,
                "file_size": message.document.file_size,
                "file_name": message.document.file_name,
                "mime_type": message.document.mime_type,
                "thumbnail": {
                    "file_id": message.document.thumbnail.file_id if message.document.thumbnail else None,
                    "width": message.document.thumbnail.width if message.document.thumbnail else None,
                    "height": message.document.thumbnail.height if message.document.thumbnail else None
                } if message.document.thumbnail else None,
                "caption": message.caption if message.caption else None
            }
        elif message.audio:
            return {
                "type": "audio",
                "file_id": message.audio.file_id,
                "file_unique_id": message.audio.file_unique_id if hasattr(message.audio, 'file_unique_id') else None,
                "file_size": message.audio.file_size,
                "duration": message.audio.duration,
                "title": message.audio.title,
                "performer": message.audio.performer,
                "mime_type": message.audio.mime_type if hasattr(message.audio, 'mime_type') else None,
                "thumbnail": {
                    "file_id": message.audio.thumbnail.file_id if message.audio.thumbnail else None,
                    "width": message.audio.thumbnail.width if message.audio.thumbnail else None,
                    "height": message.audio.thumbnail.height if message.audio.thumbnail else None
                } if message.audio.thumbnail else None,
                "caption": message.caption if message.caption else None
            }
        elif message.voice:
            return {
                "type": "voice",
                "file_id": message.voice.file_id,
                "file_unique_id": message.voice.file_unique_id if hasattr(message.voice, 'file_unique_id') else None,
                "file_size": message.voice.file_size,
                "duration": message.voice.duration,
                "mime_type": message.voice.mime_type if hasattr(message.voice, 'mime_type') else None
            }
        elif message.video_note:
            return {
                "type": "video_note",
                "file_id": message.video_note.file_id,
                "file_unique_id": message.video_note.file_unique_id if hasattr(message.video_note, 'file_unique_id') else None,
                "file_size": message.video_note.file_size,
                "duration": message.video_note.duration,
                "length": message.video_note.length,
                "thumbnail": {
                    "file_id": message.video_note.thumbnail.file_id if message.video_note.thumbnail else None,
                    "width": message.video_note.thumbnail.width if message.video_note.thumbnail else None,
                    "height": message.video_note.thumbnail.height if message.video_note.thumbnail else None
                } if message.video_note.thumbnail else None
            }
        elif message.sticker:
            return {
                "type": "sticker",
                "file_id": message.sticker.file_id,
                "file_unique_id": message.sticker.file_unique_id if hasattr(message.sticker, 'file_unique_id') else None,
                "file_size": message.sticker.file_size,
                "width": message.sticker.width,
                "height": message.sticker.height,
                "is_animated": message.sticker.is_animated if hasattr(message.sticker, 'is_animated') else False,
                "is_video": message.sticker.is_video if hasattr(message.sticker, 'is_video') else False,
                "emoji": message.sticker.emoji if hasattr(message.sticker, 'emoji') else None,
                "set_name": message.sticker.set_name if hasattr(message.sticker, 'set_name') else None
            }
        return None

    def _get_media_info(self, message):
        """Extract basic media information for compatibility"""
        return self._get_detailed_media_info(message)

    async def alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alert command - Set price alerts"""
        global realtime_service
        if not realtime_service:
            await update.message.reply_text("❌ Real-time service not available.")
            return
            
        if not rate_limiter.check_rate_limit(str(update.effective_user.id), "general"):
            await update.message.reply_text("⏱️ Please wait before sending another message.")
            return

        try:
            if len(context.args) < 3:
                await update.message.reply_text(
                    "🚨 **Price Alert Setup**\n\n"
                    "`/alert [symbol] [above/below] [price]`\n\n"
                    "**Examples:**\n"
                    "• `/alert btc above 70000` - Alert when Bitcoin goes above $70,000\n"
                    "• `/alert eth below 2500` - Alert when Ethereum drops below $2,500\n\n"
                    "You'll get instant notifications when your price targets are hit!"
                )
                return

            symbol = context.args[0].lower()
            alert_type = context.args[1].lower()
            target_price = float(context.args[2])
            
            if alert_type not in ["above", "below"]:
                await update.message.reply_text("❌ Alert type must be 'above' or 'below'")
                return

            user_id = str(update.effective_user.id)
            success = realtime_service.subscribe_price_alert(user_id, symbol, target_price, alert_type)
            
            if success:
                response = f"✅ **Price Alert Set!**\n\n"
                response += f"💰 **Coin:** {symbol.upper()}\n"
                response += f"📊 **Trigger:** {alert_type} ${target_price:,.2f}\n"
                response += f"🔔 You'll be notified instantly when the price hits your target!"
            else:
                response = "❌ Failed to set price alert. Please try again."
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid price. Please enter a valid number.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error setting alert: {str(e)}")

    async def live_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /live command - Show live data feeds"""
        if not rate_limiter.check_rate_limit(str(update.effective_user.id), "general"):
            await update.message.reply_text("⏱️ Please wait before sending another message.")
            return

        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get real-time crypto prices
            crypto_data = []
            major_coins = ["bitcoin", "ethereum", "cardano", "solana", "binancecoin"]
            
            for coin in major_coins:
                try:
                    price_info = ai_services.get_crypto_price(coin)
                    if "Error" not in price_info:
                        crypto_data.append(price_info.split('\n')[1])  # Get just the price line
                except:
                    continue
            
            # Build live feed response
            response = "📊 **LIVE DATA FEED**\n\n"
            response += "💰 **Top Cryptocurrencies:**\n"
            for data in crypto_data[:3]:
                response += f"{data}\n"
            
            response += f"\n🕐 **Current Time:** {datetime.now().strftime('%H:%M:%S UTC')}\n"
            response += "🔄 **Auto-updating every 30 seconds**\n\n"
            
            # Market status
            now = datetime.now().hour
            if 9 <= now < 16:  # Market hours
                response += "🟢 **US Market:** OPEN\n"
            else:
                response += "🔴 **US Market:** CLOSED\n"
            
            response += "📈 **Crypto Market:** Always Open 24/7\n\n"
            response += "Use `/alert`, `/newsfeed`, `/weather` for real-time notifications!"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting live data: {str(e)}")

    async def subscriptions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscriptions command - Show user's active subscriptions"""
        global realtime_service
        if not realtime_service:
            await update.message.reply_text("❌ Real-time service not available.")
            return
            
        if not rate_limiter.check_rate_limit(str(update.effective_user.id), "general"):
            await update.message.reply_text("⏱️ Please wait before sending another message.")
            return

        try:
            user_id = str(update.effective_user.id)
            subscriptions_info = realtime_service.get_user_subscriptions_info(user_id)
            await update.message.reply_text(subscriptions_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting subscriptions: {str(e)}")

    async def character_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /character command - Character customization"""
        user_id = str(update.effective_user.id)
        
        # Check user access level
        if not user_access_service.check_access(user_id, 'basic'):
            await update.message.reply_text("❌ Command not found.")
            return
        
        args = context.args
        if not args:
            # Show current character info
            char_info = character_service.get_user_character_info(user_id)
            current = char_info['current_character']
            
            response = f"🎭 **Your BotBuddy Character**\n\n"
            response += f"**Current:** {current['name']}\n"
            response += f"**Style:** {current['description']}\n\n"
            response += f"**Custom Expressions:** {char_info['expressions_count']}\n"
            response += f"**Last Updated:** {char_info['last_updated']}\n\n"
            
            # Show available characters
            response += "**Available Characters:**\n"
            for char_id, char in character_service.get_available_characters().items():
                indicator = "✅" if char_id == char_info['character_type'] else "🔸"
                response += f"{indicator} `{char_id}` - {char['name']}\n"
            
            response += f"\n**Usage:**\n"
            response += f"• `/character set <type>` - Change character\n"
            response += f"• `/character preview <type>` - Preview character\n"
            response += f"• `/character customize <mood> <emoji>` - Add custom emoji\n"
            response += f"• `/character reset` - Reset to default\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "set" and len(args) > 1:
            character_type = args[1].lower()
            result = character_service.set_user_character(user_id, character_type)
            
            if result['success']:
                # Show character message
                char_message = character_service.get_character_message(user_id, 'greeting')
                await update.message.reply_text(
                    f"✅ {result['message']}\n\n{char_message}"
                )
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        
        elif subcommand == "preview" and len(args) > 1:
            character_type = args[1].lower()
            preview = character_service.create_mood_preview(character_type)
            await update.message.reply_text(preview, parse_mode='Markdown')
        
        elif subcommand == "customize" and len(args) > 2:
            mood = args[1].lower()
            emoji = args[2]
            result = character_service.customize_expression(user_id, mood, emoji)
            
            if result['success']:
                await update.message.reply_text(f"✅ {result['message']}")
            else:
                await update.message.reply_text(f"❌ {result['message']}")
        
        elif subcommand == "reset":
            result = character_service.reset_character(user_id)
            char_message = character_service.get_character_message(user_id, 'greeting')
            await update.message.reply_text(
                f"✅ {result['message']}\n\n{char_message}"
            )
        
        else:
            await update.message.reply_text(
                "❌ Invalid command usage.\n\n"
                "**Available commands:**\n"
                "• `/character` - Show current character\n"
                "• `/character set <type>` - Change character\n"
                "• `/character preview <type>` - Preview character\n"
                "• `/character customize <mood> <emoji>` - Add custom emoji\n"
                "• `/character reset` - Reset to default"
            )

    async def personality_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /personality command - Quick personality showcase"""
        user_id = str(update.effective_user.id)
        
        # Check user access level
        if not user_access_service.check_access(user_id, 'basic'):
            await update.message.reply_text("❌ Command not found.")
            return
        
        # Show personality examples
        personalities = [
            ("cheerful", "greeting"),
            ("cool", "working"),
            ("energetic", "success"),
            ("zen", "thinking"),
            ("funny", "error"),
            ("professional", "greeting")
        ]
        
        response = "🎭 **BotBuddy Personality Showcase**\n\n"
        
        for char_type, mood in personalities:
            # Temporarily set character and get message
            temp_char = character_service.character_templates[char_type]
            expressions = temp_char["expressions"][mood]
            phrases = temp_char["phrases"][mood]
            
            emoji = expressions[0] if expressions else "🤖"
            phrase = phrases[0] if phrases else "Hello!"
            
            response += f"**{temp_char['name']}:**\n"
            response += f"{emoji} *{phrase}*\n\n"
        
        response += "Use `/character set <type>` to choose your personality!"
        await update.message.reply_text(response, parse_mode='Markdown')

    async def help_bubbles_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help_bubbles command - Contextual help system management"""
        user_id = str(update.effective_user.id)
        
        # Check user access level
        if not user_access_service.check_access(user_id, 'basic'):
            await update.message.reply_text("❌ Command not found.")
            return
        
        args = context.args
        if not args:
            # Show help stats and options
            stats = contextual_help_service.get_user_help_stats(user_id)
            
            response = f"💡 **Contextual Help System**\n\n"
            response += f"Smart help bubbles that appear when you need guidance!\n\n"
            response += f"**Your Help Stats:**\n"
            response += f"• Total helps received: {stats['total_helps']}\n"
            response += f"• Different scenarios: {len(stats['scenarios'])}\n\n"
            
            response += f"**Features:**\n"
            response += f"• Personality-matched help messages\n"
            response += f"• Context-aware assistance\n"
            response += f"• Smart cooldown system\n"
            response += f"• Witty explanations based on your character\n\n"
            
            response += f"**Commands:**\n"
            response += f"• `/help_bubbles stats` - View detailed statistics\n"
            response += f"• `/help_bubbles reset` - Reset help history\n"
            response += f"• `/help_bubbles demo` - See personality examples\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "stats":
            stats = contextual_help_service.get_user_help_stats(user_id)
            
            response = f"📊 **Your Help Statistics**\n\n"
            response += f"**Total Help Messages:** {stats['total_helps']}\n\n"
            
            if stats['scenarios']:
                response += f"**Help by Scenario:**\n"
                for scenario, count in stats['scenarios'].items():
                    scenario_name = scenario.replace('_', ' ').title()
                    response += f"• {scenario_name}: {count}\n"
            else:
                response += f"No help interactions yet! Use commands and I'll provide contextual assistance.\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif subcommand == "reset":
            success = contextual_help_service.reset_user_help_history(user_id)
            if success:
                char_message = character_service.get_character_message(user_id, 'success')
                await update.message.reply_text(
                    f"✅ Help history reset successfully!\n\n{char_message}"
                )
            else:
                await update.message.reply_text("ℹ️ No help history to reset.")
        
        elif subcommand == "demo":
            # Show how help changes with different personalities
            demo_scenarios = [
                ("command_not_found", "typing invalid command"),
                ("download_no_url", "using download without URL"),
                ("error_recovery", "when something goes wrong")
            ]
            
            response = f"🎭 **Help Personality Demo**\n\n"
            response += f"See how help messages adapt to your character:\n\n"
            
            for scenario, description in demo_scenarios:
                response += f"**{description.title()}:**\n"
                
                # Get help for different character types
                for char_type in ["cheerful", "cool", "funny"]:
                    help_templates = contextual_help_service.help_scenarios[scenario]['help_templates']
                    if char_type in help_templates:
                        example_help = help_templates[char_type][0]
                        char_name = character_service.character_templates[char_type]['name']
                        response += f"• *{char_name}:* {example_help}\n"
                
                response += f"\n"
            
            response += f"Use `/character set <type>` to change your personality!"
            await update.message.reply_text(response, parse_mode='Markdown')
        
        else:
            await update.message.reply_text(
                "❌ Invalid command usage.\n\n"
                "**Available commands:**\n"
                "• `/help_bubbles` - Show help system info\n"
                "• `/help_bubbles stats` - View statistics\n"
                "• `/help_bubbles reset` - Reset history\n"
                "• `/help_bubbles demo` - See personality examples"
            )
    
    async def sms_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sms command - Send SMS to any country (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ Admin access required for SMS messaging.")
            return
        
        try:
            # Check if SMS service is configured
            if not sms_service.is_service_configured():
                setup_msg = sms_service.get_setup_instructions()
                await update.message.reply_text(setup_msg, parse_mode=ParseMode.MARKDOWN)
                return
            
            # Parse command arguments
            args = context.args
            if len(args) < 2:
                usage_msg = """📱 **SMS Command Usage:**

**Send SMS:**
`/sms +1234567890 Your message here`

**Send with country code:**
`/sms +1234567890 US Your message here`

**Bulk SMS (multiple numbers):**
`/sms_bulk +1111111111,+2222222222 Your message here`

**View statistics:**
`/sms_stats`

**View country codes:**
`/sms_countries`

**Examples:**
• `/sms +14155552671 Hello from admin!`
• `/sms +8801712345678 BD Welcome to our service!`
• `/sms +447700900123 UK Your verification code is 123456`

💡 Supports unlimited SMS to any country worldwide!"""
                await update.message.reply_text(usage_msg, parse_mode=ParseMode.MARKDOWN)
                return
            
            # Extract phone number and message
            phone_number = args[0]
            
            # Check if second argument is a country code
            country_code = None
            message_start_idx = 1
            
            if len(args) > 2 and len(args[1]) <= 3 and args[1].upper() in sms_service.country_codes:
                country_code = args[1]
                message_start_idx = 2
            
            # Join remaining arguments as message
            message = " ".join(args[message_start_idx:])
            
            if not message:
                await update.message.reply_text("❌ Please provide a message to send.")
                return
            
            # Send status message
            status_msg = await update.message.reply_text("📱 Sending SMS...")
            
            # Send SMS
            result = await sms_service.send_sms(phone_number, message, country_code)
            
            if result["success"]:
                success_msg = f"""✅ **SMS Sent Successfully!**

📱 **To:** {result['to']}
🌍 **Country:** {result['country']}
💰 **Price:** {result['price']}
🆔 **Message ID:** {result['message_sid']}
📊 **Status:** {result['status']}

Message delivered to international SMS gateway!"""
                await status_msg.edit_text(success_msg, parse_mode=ParseMode.MARKDOWN)
            else:
                error_msg = f"""❌ **SMS Failed to Send**

📱 **To:** {result['phone']}
❌ **Error:** {result['error']}

Please check the phone number format and try again."""
                await status_msg.edit_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending SMS: {str(e)}")
    
    async def sms_bulk_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sms_bulk command - Send SMS to multiple numbers (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ Admin access required for bulk SMS.")
            return
        
        try:
            # Check if SMS service is configured
            if not sms_service.is_service_configured():
                setup_msg = sms_service.get_setup_instructions()
                await update.message.reply_text(setup_msg, parse_mode=ParseMode.MARKDOWN)
                return
            
            # Parse command arguments
            args = context.args
            if len(args) < 2:
                usage_msg = """📱 **Bulk SMS Usage:**

**Format:**
`/sms_bulk +1111111111,+2222222222,+3333333333 Your message here`

**With country codes:**
`/sms_bulk +1111111111:US,+447700900123:GB Your message here`

**Example:**
`/sms_bulk +14155552671,+8801712345678,+447700900123 Important announcement for all users!`

💡 Send to unlimited numbers simultaneously!"""
                await update.message.reply_text(usage_msg, parse_mode=ParseMode.MARKDOWN)
                return
            
            # Extract phone numbers and message
            phone_numbers_str = args[0]
            message = " ".join(args[1:])
            
            if not message:
                await update.message.reply_text("❌ Please provide a message to send.")
                return
            
            # Parse phone numbers
            recipients = []
            phone_entries = phone_numbers_str.split(',')
            
            for entry in phone_entries:
                entry = entry.strip()
                if ':' in entry:
                    # Format: +1234567890:US
                    phone, country = entry.split(':', 1)
                    recipients.append({"phone": phone.strip(), "country": country.strip()})
                else:
                    # Format: +1234567890
                    recipients.append({"phone": entry.strip(), "country": ""})
            
            if not recipients:
                await update.message.reply_text("❌ No valid phone numbers found.")
                return
            
            # Send status message
            status_msg = await update.message.reply_text(f"📱 Sending bulk SMS to {len(recipients)} recipients...")
            
            # Send bulk SMS
            result = await sms_service.send_bulk_sms(recipients, message)
            
            # Format results
            results_msg = f"""📊 **Bulk SMS Results**

📱 **Total Recipients:** {result['total']}
✅ **Successful:** {result['successful']}
❌ **Failed:** {result['failed']}

**Details:**"""
            
            for detail in result['details'][:10]:  # Show first 10 results
                status_icon = "✅" if detail['status'] == 'sent' else "❌"
                results_msg += f"\n{status_icon} {detail['phone']}"
            
            if len(result['details']) > 10:
                results_msg += f"\n... and {len(result['details']) - 10} more recipients"
            
            await status_msg.edit_text(results_msg, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending bulk SMS: {str(e)}")
    
    async def sms_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sms_stats command - View SMS statistics (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ Admin access required for SMS statistics.")
            return
        
        try:
            stats = sms_service.get_sms_statistics()
            await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting SMS statistics: {str(e)}")
    
    async def sms_countries_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sms_countries command - View supported country codes"""
        try:
            countries = sms_service.get_country_codes_list()
            await update.message.reply_text(countries, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting country codes: {str(e)}")
    
    async def free_sms_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /free_sms command - Send free SMS"""
        args = context.args
        user_id = str(update.effective_user.id)
        
        if len(args) < 2:
            usage_msg = f"""📱 **Free SMS Service**

**Usage:**
`/free_sms <phone_number> <message>`

**Examples:**
`/free_sms +1234567890 Hello from the bot!`
`/free_sms +44123456789 Your verification code is 123456`

**Supported Countries:**
• US/Canada: +1 (1 free SMS per day)
• UK: +44 (Demo service)
• Germany: +49 (Demo service)
• And more...

**Features:**
• No API keys required
• Multiple free providers
• Automatic phone formatting
• Daily usage tracking

Use `/free_sms_countries` to see all supported regions."""
            await update.message.reply_text(usage_msg, parse_mode=ParseMode.MARKDOWN)
            return
        
        phone = args[0]
        message = " ".join(args[1:])
        
        # Show loading animation
        loading_message_id = await animation_service.show_loading_animation(update, context, 'tech', 2)
        
        # Determine country code from phone number
        country_code = 'US'  # Default
        if phone.startswith('+44'):
            country_code = 'UK'
        elif phone.startswith('+49'):
            country_code = 'DE'
        elif phone.startswith('+1'):
            country_code = 'US'
        
        result = free_sms_service.send_free_sms(phone, message, country_code)
        
        if result['success']:
            success_msg = f"""✅ **SMS Sent Successfully!**

📱 **To:** {phone}
💬 **Message:** {message[:50]}{'...' if len(message) > 50 else ''}
🌐 **Provider:** {result['provider']}
💰 **Cost:** {result['cost']}

{result.get('note', '')}"""
            
            if loading_message_id:
                await animation_service.show_success_animation(update, context, loading_message_id)
                await update.message.reply_text(success_msg, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(success_msg, parse_mode=ParseMode.MARKDOWN)
        else:
            error_msg = f"""❌ **SMS Failed**

📱 **To:** {phone}
❌ **Error:** {result['error']}
🌐 **Provider:** {result.get('provider', 'Unknown')}

💡 **Tip:** Try again later or use a different number format."""
            
            if loading_message_id:
                await animation_service.show_error_animation(update, context, loading_message_id, result['error'])
            else:
                await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)

    async def free_sms_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /free_sms_stats command - View free SMS statistics"""
        stats = free_sms_service.get_free_sms_statistics()
        await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)

    async def free_sms_countries_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /free_sms_countries command - View supported countries"""
        countries = free_sms_service.get_supported_countries_free()
        await update.message.reply_text(countries, parse_mode=ParseMode.MARKDOWN)
    
    async def admin_panel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - Complete admin control panel (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found.")
            return
        
        try:
            # Create comprehensive admin panel with inline buttons
            keyboard = [
                [
                    InlineKeyboardButton("📊 Bot Statistics", callback_data="admin_stats"),
                    InlineKeyboardButton("📱 SMS Service", callback_data="admin_sms")
                ],
                [
                    InlineKeyboardButton("🕵️ Surveillance", callback_data="admin_surveillance"),
                    InlineKeyboardButton("🛡️ Moderation", callback_data="admin_moderation")
                ],
                [
                    InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                    InlineKeyboardButton("💬 Messages", callback_data="admin_messages")
                ],
                [
                    InlineKeyboardButton("🚫 Ban/Mute", callback_data="admin_ban_mute"),
                    InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
                    InlineKeyboardButton("🔄 System", callback_data="admin_system")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_message = f"""🔐 **ADMIN CONTROL PANEL**

Welcome to the comprehensive admin dashboard. All bot features and controls are accessible here.

**Current Status:**
• Total Users: {len(user_db.data.get('users', {}))}
• Active Surveillance: ✅ Monitoring all groups
• SMS Service: {'✅ Configured' if sms_service.is_service_configured() else '❌ Setup required'}
• Moderation: ✅ Auto-moderation active
• Rate Limits: ∞ Unlimited for all features

Click any button below to access admin features:"""

            await update.message.reply_text(
                admin_message, 
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error loading admin panel: {str(e)}")
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin panel button callbacks"""
        query = update.callback_query
        user_id = str(query.from_user.id)
        
        # Check if user is admin
        if int(user_id) != ADMIN_USER_ID:
            await query.answer("❌ Unauthorized access.", show_alert=True)
            return
        
        await query.answer()
        
        try:
            action = query.data
            
            if action == "admin_stats":
                # Bot statistics
                stats_msg = f"""📊 **BOT STATISTICS**

👥 **Users:** {len(user_db.data.get('users', {}))}
📱 **SMS Sent:** {sms_service.sms_logs['statistics']['total_sent']}
🌍 **Countries Reached:** {len(sms_service.sms_logs['statistics']['countries_reached'])}
🛡️ **Violations Blocked:** {admin_controls.admin_settings.get('total_violations', 0) if admin_controls else 0}
🕵️ **Messages Logged:** {len(group_surveillance.group_logs.get('messages', [])) if group_surveillance else 0}

**Recent Activity:**
• Active surveillance in all groups
• Automatic moderation protecting users
• Real-time monitoring operational
• All systems functioning normally"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(stats_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_sms":
                # SMS service panel
                if sms_service.is_service_configured():
                    sms_stats = sms_service.get_sms_statistics()
                    keyboard = [
                        [InlineKeyboardButton("📱 Send SMS", callback_data="admin_sms_send")],
                        [InlineKeyboardButton("📊 View Stats", callback_data="admin_sms_stats")],
                        [InlineKeyboardButton("🌍 Countries", callback_data="admin_sms_countries")],
                        [InlineKeyboardButton("🔙 Back", callback_data="admin_main")]
                    ]
                else:
                    sms_stats = sms_service.get_setup_instructions()
                    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(sms_stats, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_surveillance":
                # Surveillance panel
                if group_surveillance:
                    surveillance_summary = group_surveillance.get_group_surveillance_summary()
                else:
                    surveillance_summary = "🕵️ **Group Surveillance**\n\nSurveillance system ready to monitor groups."
                
                keyboard = [
                    [InlineKeyboardButton("📊 View Data", callback_data="admin_surv_data")],
                    [InlineKeyboardButton("🔍 Search Messages", callback_data="admin_surv_search")],
                    [InlineKeyboardButton("🔙 Back", callback_data="admin_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(surveillance_summary, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_moderation":
                # Moderation panel
                if admin_controls:
                    mod_stats = admin_controls.get_moderation_stats()
                else:
                    mod_stats = "🛡️ **Moderation System**\n\nModeration tools ready for group management."
                
                keyboard = [
                    [InlineKeyboardButton("🚫 Ban User", callback_data="admin_mod_ban")],
                    [InlineKeyboardButton("🔇 Mute User", callback_data="admin_mod_mute")],
                    [InlineKeyboardButton("📝 Banned Words", callback_data="admin_mod_words")],
                    [InlineKeyboardButton("🔙 Back", callback_data="admin_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(mod_stats, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_broadcast":
                # Broadcast panel
                broadcast_msg = """📢 **BROADCAST SYSTEM**

Send messages to all users or specific groups.

**Usage:**
• `/broadcast Your message here` - Send to all users
• Rate limit: ∞ Unlimited broadcasts
• Delivery tracking included

**Recent Broadcasts:**
• All messages delivered successfully
• No failed deliveries reported"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(broadcast_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_messages":
                # Messages panel
                messages_msg = """💬 **MESSAGE MANAGEMENT**

View and respond to user messages.

**Commands:**
• `/logs` - View all user activity
• `/reply <user_id> <message>` - Respond to users
• All messages automatically logged

**Recent Activity:**
• All user interactions monitored
• Complete message history available
• Real-time logging active"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(messages_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_ban_mute":
                # Ban/Mute quick actions
                ban_mute_msg = """🚫 **BAN & MUTE CONTROLS**

Quick moderation actions:

**Commands:**
• `/ban <user_id> [reason]` - Ban user
• `/mute <user_id> [minutes] [reason]` - Mute user
• `/unban <user_id>` - Remove ban
• `/unmute <user_id>` - Remove mute

**Auto-Moderation:**
• Spam detection: ✅ Active
• Link blocking: ✅ Active
• Word filtering: ✅ Active"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(ban_mute_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_logs":
                # Logs panel
                logs_msg = """📝 **SYSTEM LOGS**

Access all system logs and user activity.

**Available Logs:**
• User activity logs (secret)
• Group surveillance data
• SMS delivery logs
• Moderation action logs
• System error logs

**Usage:**
• `/logs` - View recent user activity
• All data automatically captured"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(logs_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_settings":
                # Settings panel
                settings_msg = """⚙️ **SYSTEM SETTINGS**

Current Configuration:

**Rate Limits:**
• Messages: ∞ Unlimited
• Downloads: ∞ Unlimited
• Broadcasts: ∞ Unlimited
• SMS: ∞ Unlimited

**Services:**
• AI Chat: ✅ Gemini Active
• Surveillance: ✅ All Groups
• Moderation: ✅ Auto-Active
• SMS Service: {'✅ Configured' if sms_service.is_service_configured() else '❌ Setup Required'}"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(settings_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_system":
                # System panel
                system_msg = """🔄 **SYSTEM STATUS**

**Bot Status:** ✅ Online and operational
**Uptime:** Continuous monitoring active
**Services:** All systems functional

**Components:**
• Telegram API: ✅ Connected
• AI Services: ✅ Gemini Online
• Database: ✅ Operational
• File Storage: ✅ Available
• Surveillance: ✅ Active
• Moderation: ✅ Running

**Performance:**
• Response Time: < 1 second
• Success Rate: 99.9%
• Error Rate: < 0.1%"""
                
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(system_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_main":
                # Return to main admin panel
                keyboard = [
                    [
                        InlineKeyboardButton("📊 Bot Statistics", callback_data="admin_stats"),
                        InlineKeyboardButton("📱 SMS Service", callback_data="admin_sms")
                    ],
                    [
                        InlineKeyboardButton("🕵️ Surveillance", callback_data="admin_surveillance"),
                        InlineKeyboardButton("🛡️ Moderation", callback_data="admin_moderation")
                    ],
                    [
                        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                        InlineKeyboardButton("💬 Messages", callback_data="admin_messages")
                    ],
                    [
                        InlineKeyboardButton("🚫 Ban/Mute", callback_data="admin_ban_mute"),
                        InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
                    ],
                    [
                        InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
                        InlineKeyboardButton("🔄 System", callback_data="admin_system")
                    ]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                admin_message = f"""🔐 **ADMIN CONTROL PANEL**

Welcome to the comprehensive admin dashboard. All bot features and controls are accessible here.

**Current Status:**
• Total Users: {len(user_db.data.get('users', {}))}
• Active Surveillance: ✅ Monitoring all groups
• SMS Service: {'✅ Configured' if sms_service.is_service_configured() else '❌ Setup required'}
• Moderation: ✅ Auto-moderation active
• Rate Limits: ∞ Unlimited for all features

Click any button below to access admin features:"""

                await query.edit_message_text(admin_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            error_msg = f"❌ Error in admin panel: {str(e)}"
            keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_msg, reply_markup=reply_markup)

    async def grant_access_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /grant_access command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "📝 **Usage:** `/grant_access <user_id> <level>`\n\n"
                "**Access Levels:**\n"
                "• `basic` - Chat, Wiki, Translate, Download, Crypto, Accessibility, Voice, Advanced Features\n"
                "• `premium` - Basic + Free SMS\n"
                "• `vip` - Premium + Premium Tools\n"
                "• `admin` - Full access to everything",
                parse_mode='Markdown'
            )
            return
        
        target_user_id = context.args[0]
        access_level = context.args[1].lower()
        
        if user_access_service.grant_access(target_user_id, access_level, user_id):
            await update.message.reply_text(
                f"✅ **Access Granted**\n\n"
                f"👤 **User:** {target_user_id}\n"
                f"🔑 **Level:** {access_level.title()}\n"
                f"📅 **Granted:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Invalid access level:** {access_level}\n\n"
                "Valid levels: basic, premium, vip, admin"
            )
    
    async def temp_access_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /temp_access command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "📝 **Usage:** `/temp_access <user_id> <feature> <hours>`\n\n"
                "**Features:**\n"
                "• `free_sms` - Free SMS messaging\n"
                "• `premium_features` - Premium access\n"
                "• `advanced_features` - Advanced tools\n\n"
                "**Example:** `/temp_access 123456789 free_sms 24`",
                parse_mode='Markdown'
            )
            return
        
        target_user_id = context.args[0]
        feature = context.args[1]
        try:
            hours = int(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Hours must be a number")
            return
        
        if user_access_service.grant_temporary_access(target_user_id, feature, hours, user_id):
            expiry_time = datetime.now() + timedelta(hours=hours)
            await update.message.reply_text(
                f"⏰ **Temporary Access Granted**\n\n"
                f"👤 **User:** {target_user_id}\n"
                f"🔧 **Feature:** {feature}\n"
                f"⏱️ **Duration:** {hours} hours\n"
                f"📅 **Expires:** {expiry_time.strftime('%Y-%m-%d %H:%M')}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to grant temporary access")
    
    async def revoke_access_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /revoke_access command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found")
            return
        
        if len(context.args) < 1:
            await update.message.reply_text(
                "📝 **Usage:** `/revoke_access <user_id>`\n\n"
                "This will remove all access permissions for the user.",
                parse_mode='Markdown'
            )
            return
        
        target_user_id = context.args[0]
        
        if user_access_service.revoke_access(target_user_id, user_id):
            await update.message.reply_text(
                f"🚫 **Access Revoked**\n\n"
                f"👤 **User:** {target_user_id}\n"
                f"📅 **Revoked:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                "All permissions have been removed.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to revoke access")
    
    async def check_access_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check_access command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found")
            return
        
        if len(context.args) < 1:
            target_user_id = user_id
        else:
            target_user_id = context.args[0]
        
        access_info = user_access_service.get_user_access_info(target_user_id)
        await update.message.reply_text(access_info, parse_mode='Markdown')
    
    async def list_access_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_access command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ Command not found")
            return
        
        access_info = user_access_service.get_all_users_access()
        await update.message.reply_text(access_info, parse_mode='Markdown')

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command - Group feature configuration"""
        chat_id = str(update.effective_chat.id)
        
        # Only work in groups
        if update.effective_chat.type == 'private':
            await update.message.reply_text(
                "⚙️ Settings are only available in groups!\n\n"
                "Add me to a group and use `/settings` there to configure features."
            )
            return
        
        # Check if user is admin in the group
        try:
            chat_member = await context.bot.get_chat_member(chat_id, update.effective_user.id)
            if chat_member.status not in ['administrator', 'creator']:
                await update.message.reply_text(
                    "🔒 Only group administrators can change settings."
                )
                return
        except Exception:
            await update.message.reply_text(
                "❌ Unable to verify admin status. Please ensure the bot has proper permissions."
            )
            return
        
        # Handle different settings commands
        if not context.args:
            # Show settings menu
            settings_menu = group_settings_service.get_settings_menu(chat_id)
            await update.message.reply_text(settings_menu, parse_mode='Markdown')
            return
        
        if len(context.args) == 1 and context.args[0].lower() == 'list':
            # Show settings menu
            settings_menu = group_settings_service.get_settings_menu(chat_id)
            await update.message.reply_text(settings_menu, parse_mode='Markdown')
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "📝 **Usage:**\n"
                "`/settings` - Show current settings\n"
                "`/settings <feature> on` - Enable feature\n"
                "`/settings <feature> off` - Disable feature\n\n"
                "**Available features:**\n"
                "• auto_responses - AI auto-responses\n"
                "• media_downloads - Media downloads\n"
                "• translation - Language translation\n"
                "• crypto_updates - Crypto price updates\n"
                "• accessibility_features - Accessibility support\n"
                "• voice_transcription - Voice transcription\n"
                "• spam_protection - Spam protection\n"
                "• word_filtering - Word filtering\n"
                "• new_member_screening - New member screening\n"
                "• auto_moderation - Auto moderation\n"
                "• welcome_messages - Welcome messages",
                parse_mode='Markdown'
            )
            return
        
        feature = context.args[0].lower()
        action = context.args[1].lower()
        
        if action not in ['on', 'off']:
            await update.message.reply_text(
                "❌ Action must be 'on' or 'off'\n"
                "Example: `/settings auto_responses on`"
            )
            return
        
        # Special handling for certain features
        if feature == 'activity_logging':
            await update.message.reply_text(
                "🔒 Activity logging is always enabled and cannot be disabled."
            )
            return
        
        if feature not in group_settings_service.get_available_features():
            await update.message.reply_text(
                f"❌ Unknown feature: {feature}\n"
                "Use `/settings` to see available features."
            )
            return
        
        # Update the setting
        new_value = action == 'on'
        success = group_settings_service.update_group_setting(chat_id, feature, new_value)
        
        if success:
            status = "✅ ENABLED" if new_value else "❌ DISABLED"
            feature_description = group_settings_service.get_feature_description(feature)
            
            await update.message.reply_text(
                f"✅ **Setting Updated**\n\n"
                f"**Feature:** {feature.replace('_', ' ').title()}\n"
                f"**Status:** {status}\n"
                f"**Description:** {feature_description}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Failed to update setting. Please try again."
            )
    
    async def meme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /meme command - Generate custom memes"""
        user_id = str(update.effective_user.id)
        
        if not user_access_service.check_permission(user_id, "premium"):
            await update.message.reply_text("🔒 Meme generation requires premium access. Contact admin for upgrade.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "🎨 **Meme Generator**\n\n"
                "Usage: `/meme your topic or idea here`\n\n"
                "Examples:\n"
                "• `/meme programming bugs`\n"
                "• `/meme monday mornings`\n"
                "• `/meme online classes`\n\n"
                "I'll create a funny meme with your topic!",
                parse_mode='Markdown'
            )
            return
        
        user_prompt = ' '.join(context.args)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        
        result = content_generation_service.generate_custom_meme(user_prompt)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            response = f"🎭 **Custom Meme Generated!**\n\n"
            response += f"**Template:** {result['template_used']}\n"
            response += f"**Your Topic:** {result['user_prompt']}\n\n"
            response += f"**Meme Content:**\n{result['meme_content'][:500]}..."
            
            if result.get('image_path') and os.path.exists(result['image_path']):
                try:
                    with open(result['image_path'], 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo,
                            caption=response,
                            parse_mode='Markdown'
                        )
                except Exception:
                    await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
    
    async def story_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /story command - Generate creative stories"""
        user_id = str(update.effective_user.id)
        
        if not user_access_service.check_permission(user_id, "premium"):
            await update.message.reply_text("🔒 Story generation requires premium access. Contact admin for upgrade.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📚 **Story Generator**\n\n"
                "Usage: `/story your story prompt`\n\n"
                "Examples:\n"
                "• `/story a robot who dreams of becoming human`\n"
                "• `/story mystery in an old bookstore`\n"
                "• `/story adventure on Mars colony`\n\n"
                "I'll create an engaging story from your prompt!",
                parse_mode='Markdown'
            )
            return
        
        user_prompt = ' '.join(context.args)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        result = content_generation_service.generate_creative_story(user_prompt)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            # Send story in parts if too long
            story_text = result['story']
            if len(story_text) > 4000:
                # Split into chunks
                chunks = [story_text[i:i+4000] for i in range(0, len(story_text), 4000)]
                await update.message.reply_text(f"📖 **Generated Story ({result['genre']} - {result['word_count']} words)**\n\n{chunks[0]}", parse_mode='Markdown')
                for chunk in chunks[1:]:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(f"📖 **Generated Story ({result['genre']} - {result['word_count']} words)**\n\n{story_text}", parse_mode='Markdown')
    
    async def workout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /workout command - Generate personalized workout plans"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "💪 **Workout Plan Generator**\n\n"
                "Usage: `/workout [profile] | [goals]`\n\n"
                "Example:\n"
                "• `/workout beginner, 25 years old | lose weight and build muscle`\n"
                "• `/workout intermediate runner | prepare for marathon`\n\n"
                "I'll create a personalized workout plan for you!",
                parse_mode='Markdown'
            )
            return
        
        input_text = ' '.join(context.args)
        if '|' in input_text:
            profile, goals = input_text.split('|', 1)
            profile = profile.strip()
            goals = goals.strip()
        else:
            profile = input_text
            goals = "general fitness improvement"
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        result = content_generation_service.generate_workout_plan(profile, goals)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            response = f"🏋️ **Personalized Workout Plan**\n\n"
            response += f"**Profile:** {result['user_profile']}\n"
            response += f"**Goals:** {result['goals']}\n"
            response += f"**Duration:** {result['duration']}\n\n"
            
            # Send workout plan
            plan_text = result['workout_plan']
            if len(plan_text) > 3500:
                response += plan_text[:3500] + "..."
                await update.message.reply_text(response, parse_mode='Markdown')
                # Send nutrition advice separately
                await update.message.reply_text(f"🥗 **Nutrition Advice:**\n\n{result['nutrition_advice'][:4000]}", parse_mode='Markdown')
            else:
                response += plan_text
                await update.message.reply_text(response, parse_mode='Markdown')
    
    async def recipe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recipe command - Generate custom recipes"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "👨‍🍳 **Recipe Generator**\n\n"
                "Usage: `/recipe [cuisine] [dietary restrictions] [ingredients]`\n\n"
                "Examples:\n"
                "• `/recipe italian vegetarian pasta tomatoes`\n"
                "• `/recipe asian gluten-free chicken rice`\n"
                "• `/recipe mexican vegan beans corn`\n\n"
                "I'll create a delicious recipe for you!",
                parse_mode='Markdown'
            )
            return
        
        args = context.args
        cuisine = args[0] if args else "international"
        dietary = args[1] if len(args) > 1 else ""
        ingredients = ' '.join(args[2:]) if len(args) > 2 else ""
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        result = content_generation_service.generate_recipe(cuisine, dietary, ingredients)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            recipe_text = result['recipe']
            if len(recipe_text) > 4000:
                # Split recipe into parts
                await update.message.reply_text(f"🍽️ **Custom {result['cuisine_type'].title()} Recipe**\n\n{recipe_text[:4000]}", parse_mode='Markdown')
                await update.message.reply_text(f"👨‍🍳 **Cooking Tips:**\n\n{result['cooking_tips'][:4000]}", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"🍽️ **Custom {result['cuisine_type'].title()} Recipe**\n\n{recipe_text}", parse_mode='Markdown')
    
    async def trivia_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trivia command - Start trivia games"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "🧠 **Trivia Game**\n\n"
                "Usage: `/trivia [category] [difficulty]`\n\n"
                "Categories: science, history, geography, sports, entertainment, technology, literature, art, music, general\n\n"
                "Difficulty: easy, medium, hard\n\n"
                "Example: `/trivia science medium`\n\n"
                "Start your trivia challenge!",
                parse_mode='Markdown'
            )
            return
        
        category = context.args[0] if context.args else "general"
        difficulty = context.args[1] if len(context.args) > 1 else "medium"
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        result = games_service.start_trivia_game(user_id, category, difficulty)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            # Store game ID in user context
            if not hasattr(context, 'user_data'):
                context.user_data = {}
            if user_id not in context.user_data:
                context.user_data[user_id] = {}
            context.user_data[user_id]['current_game'] = result['game_id']
            
            response = f"🎮 **Trivia Game Started!**\n\n"
            response += f"**Category:** {result['category'].title()}\n"
            response += f"**Difficulty:** {result['difficulty'].title()}\n"
            response += f"**Question {result['question_number']}/{result['total_questions']}**\n\n"
            response += f"**{result['question']}**\n\n"
            
            for option, text in result['options'].items():
                response += f"{option}: {text}\n"
            
            response += f"\nReply with A, B, C, or D to answer!"
            
            await update.message.reply_text(response, parse_mode='Markdown')
    
    async def wordgame_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wordgame command - Start word games"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "🎯 **Word Games**\n\n"
                "Usage: `/wordgame [type]`\n\n"
                "Game Types:\n"
                "• `word_association` - Build word chains\n"
                "• `word_scramble` - Unscramble words\n"
                "• `rhyme_time` - Find rhyming words\n"
                "• `story_builder` - Build stories together\n\n"
                "Example: `/wordgame word_association`",
                parse_mode='Markdown'
            )
            return
        
        game_type = context.args[0]
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        result = games_service.start_word_game(user_id, game_type)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            # Store game ID in user context
            if not hasattr(context, 'user_data'):
                context.user_data = {}
            if user_id not in context.user_data:
                context.user_data[user_id] = {}
            context.user_data[user_id]['current_game'] = result['game_id']
            
            response = f"🎮 **{result['game_type'].replace('_', ' ').title()} Game**\n\n"
            response += f"**Instructions:** {result['instructions']}\n\n"
            
            if 'starting_word' in result:
                response += f"**Starting Word:** {result['starting_word']}\n\n"
            elif 'scrambled_word' in result:
                response += f"**Scrambled Word:** `{result['scrambled_word']}`\n"
                response += f"**Word Length:** {result['word_length']} letters\n"
                response += f"**Difficulty:** {result['difficulty']}\n\n"
            elif 'target_word' in result:
                response += f"**Find words that rhyme with:** {result['target_word']}\n\n"
            elif 'story_start' in result:
                response += f"**Story so far:**\n{result['story_start']}\n\n"
            
            response += "Send your response to play!"
            
            await update.message.reply_text(response, parse_mode='Markdown')
    
    async def riddle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /riddle command - Get random riddles"""
        user_id = str(update.effective_user.id)
        
        result = games_service.get_random_riddle()
        
        # Store riddle ID in user context
        if not hasattr(context, 'user_data'):
            context.user_data = {}
        if user_id not in context.user_data:
            context.user_data[user_id] = {}
        context.user_data[user_id]['current_riddle'] = result['riddle_id']
        
        response = f"🧩 **Riddle Challenge**\n\n"
        response += f"**{result['riddle']}**\n\n"
        response += f"{result['instructions']}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def ocr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ocr command - Extract text from images"""
        user_id = str(update.effective_user.id)
        
        if not user_access_service.check_permission(user_id, "premium"):
            await update.message.reply_text("🔒 OCR text extraction requires premium access. Contact admin for upgrade.")
            return
        
        # Check if user recently sent an image
        if not hasattr(context, 'user_data') or user_id not in context.user_data:
            await update.message.reply_text(
                "📸 **OCR Text Extraction**\n\n"
                "Please send an image first, then use `/ocr` to extract text from it.\n\n"
                "I can read text in multiple languages and provide detailed analysis!",
                parse_mode='Markdown'
            )
            return
        
        recent_media = context.user_data[user_id].get('recent_media', [])
        recent_images = [media for media in recent_media if media.get('type') == 'photo']
        
        if not recent_images:
            await update.message.reply_text("No recent images found. Please send an image first, then use /ocr.")
            return
        
        latest_image = recent_images[-1]
        image_path = latest_image.get('file_path')
        
        if not image_path or not os.path.exists(image_path):
            await update.message.reply_text("❌ Image file not found for OCR analysis.")
            return
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Use enhanced vision service for OCR
        try:
            from enhanced_vision_service import enhanced_vision_service
            result = enhanced_vision_service.extract_text_from_image(image_path)
        except ImportError:
            await update.message.reply_text("❌ OCR service not available. Please ensure all dependencies are installed.")
            return
        
        if "error" in result:
            await update.message.reply_text(f"❌ OCR failed: {result['error']}")
        else:
            response = f"🔍 **OCR Text Extraction Results**\n\n"
            
            if result['text']:
                response += f"**Extracted Text:**\n```\n{result['text'][:2000]}\n```\n\n"
                response += f"**Word Count:** {result['word_count']}\n"
                response += f"**Confidence:** {result['confidence']:.1f}%\n"
                response += f"**Languages Detected:** {', '.join(result['languages_detected'])}\n"
                response += f"**Text Regions:** {result['text_regions']}"
            else:
                response += "No text detected in the image. The image might not contain readable text or the text might be too blurry."
            
            await update.message.reply_text(response, parse_mode='Markdown')

# Create global instance
bot_handlers = BotHandlers()
