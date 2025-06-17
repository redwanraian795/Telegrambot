import json
import os
from typing import Dict, Any

class LanguageService:
    def __init__(self):
        self.user_languages = self.load_user_languages()
        self.translations = self.load_translations()
        
    def load_user_languages(self) -> Dict[str, str]:
        """Load user language preferences"""
        try:
            if os.path.exists("user_languages.json"):
                with open("user_languages.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_user_languages(self):
        """Save user language preferences"""
        try:
            with open("user_languages.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_languages, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionary"""
        return {
            "en": {
                # Bot responses
                "welcome_message": "🤖 Welcome to AI Telegram Bot!\n\nI'm your intelligent assistant powered by advanced AI. I can help you with unlimited conversations, downloads, translations, and much more!\n\n🌟 Key Features:\n• Unlimited AI chat with Gemini\n• Download from all platforms (YouTube, Instagram, TikTok, etc.)\n• Real-time crypto tracking & predictions\n• Smart home automation\n• Voice & image analysis\n• Complete group moderation\n• And much more!\n\nType /help to see all commands or just start chatting!",
                "help_title": "🔧 **Available Commands:**\n\n",
                "language_changed": "✅ Language changed to English!",
                "choose_language": "🌐 Choose your language:\n\n🇺🇸 /english - English interface\n🇧🇩 /bangla - বাংলা ইন্টারফেস",
                "admin_only": "❌ Admin access required for this command.",
                "group_only": "❌ This command only works in groups.",
                "rate_limit": "⏳ Please slow down. Rate limit exceeded.",
                "error_occurred": "❌ An error occurred: {error}",
                "success": "✅ Success!",
                "banned_user": "🚫 User {user} has been banned.\nReason: {reason}",
                "muted_user": "🔇 User {user} has been muted for {duration} minutes.\nReason: {reason}",
                "unmuted_user": "🔊 User {user} has been unmuted.",
                "unbanned_user": "✅ User {user} has been unbanned.",
                "word_added": "✅ Added '{word}' to banned words list.",
                "word_removed": "✅ Removed '{word}' from banned words list.",
                "usage_format": "Usage: {usage}",
                "crypto_price": "💰 **{symbol}** Price Information:",
                "downloading": "⬇️ Downloading your media...",
                "download_complete": "✅ Download complete! Here's your file:",
                "translating": "🌐 Translating...",
                "generating_response": "🤖 Generating AI response...",
                "analyzing_image": "🔍 Analyzing image...",
                "creating_meme": "😄 Creating meme...",
                "surveillance_summary": "🕵️ **Surveillance Summary**",
                "moderation_stats": "🛡️ **Moderation Statistics**",
                "accessibility_enabled": "♿ Accessibility mode enabled",
                "accessibility_disabled": "♿ Accessibility mode disabled",
                "speaking": "🗣️ Converting to speech...",
                "no_results": "No results found.",
                "search_results": "🔍 **Search Results:**"
            },
            "bn": {
                # Bengali translations
                "welcome_message": "🤖 AI টেলিগ্রাম বটে স্বাগতম!\n\nআমি আপনার বুদ্ধিমান সহায়ক যা উন্নত AI দ্বারা চালিত। আমি আপনাকে সীমাহীন কথোপকথন, ডাউনলোড, অনুবাদ এবং আরও অনেক কিছুতে সাহায্য করতে পারি!\n\n🌟 প্রধান বৈশিষ্ট্য:\n• জেমিনি দিয়ে সীমাহীন AI চ্যাট\n• সব প্ল্যাটফর্ম থেকে ডাউনলোড (ইউটিউব, ইনস্টাগ্রাম, টিকটক ইত্যাদি)\n• রিয়েল-টাইম ক্রিপ্টো ট্র্যাকিং ও পূর্বাভাস\n• স্মার্ট হোম অটোমেশন\n• ভয়েস ও ইমেজ বিশ্লেষণ\n• সম্পূর্ণ গ্রুপ মডারেশন\n• আরও অনেক কিছু!\n\nসব কমান্ড দেখতে /help টাইপ করুন অথবা চ্যাট শুরু করুন!",
                "help_title": "🔧 **উপলব্ধ কমান্ড:**\n\n",
                "language_changed": "✅ ভাষা বাংলায় পরিবর্তিত হয়েছে!",
                "choose_language": "🌐 আপনার ভাষা নির্বাচন করুন:\n\n🇺🇸 /english - ইংরেজি ইন্টারফেস\n🇧🇩 /bangla - বাংলা ইন্টারফেস",
                "admin_only": "❌ এই কমান্ডের জন্য অ্যাডমিন অ্যাক্সেস প্রয়োজন।",
                "group_only": "❌ এই কমান্ড শুধুমাত্র গ্রুপে কাজ করে।",
                "rate_limit": "⏳ দয়া করে ধীরে করুন। রেট লিমিট অতিক্রম করেছে।",
                "error_occurred": "❌ একটি ত্রুটি ঘটেছে: {error}",
                "success": "✅ সফল!",
                "banned_user": "🚫 ব্যবহারকারী {user} কে নিষিদ্ধ করা হয়েছে।\nকারণ: {reason}",
                "muted_user": "🔇 ব্যবহারকারী {user} কে {duration} মিনিটের জন্য নিঃশব্দ করা হয়েছে।\nকারণ: {reason}",
                "unmuted_user": "🔊 ব্যবহারকারী {user} এর নিঃশব্দতা তুলে নেওয়া হয়েছে।",
                "unbanned_user": "✅ ব্যবহারকারী {user} এর নিষেধাজ্ঞা তুলে নেওয়া হয়েছে।",
                "word_added": "✅ '{word}' নিষিদ্ধ শব্দের তালিকায় যোগ করা হয়েছে।",
                "word_removed": "✅ '{word}' নিষিদ্ধ শব্দের তালিকা থেকে সরানো হয়েছে।",
                "usage_format": "ব্যবহার: {usage}",
                "crypto_price": "💰 **{symbol}** দামের তথ্য:",
                "downloading": "⬇️ আপনার মিডিয়া ডাউনলোড করা হচ্ছে...",
                "download_complete": "✅ ডাউনলোড সম্পন্ন! এই আপনার ফাইল:",
                "translating": "🌐 অনুবাদ করা হচ্ছে...",
                "generating_response": "🤖 AI প্রতিক্রিয়া তৈরি করা হচ্ছে...",
                "analyzing_image": "🔍 ছবি বিশ্লেষণ করা হচ্ছে...",
                "creating_meme": "😄 মিম তৈরি করা হচ্ছে...",
                "surveillance_summary": "🕵️ **নজরদারি সারসংক্ষেপ**",
                "moderation_stats": "🛡️ **মডারেশন পরিসংখ্যান**",
                "accessibility_enabled": "♿ অ্যাক্সেসযোগ্যতা মোড সক্রিয় করা হয়েছে",
                "accessibility_disabled": "♿ অ্যাক্সেসযোগ্যতা মোড নিষ্ক্রিয় করা হয়েছে",
                "speaking": "🗣️ বক্তৃতায় রূপান্তর করা হচ্ছে...",
                "no_results": "কোন ফলাফল পাওয়া যায়নি।",
                "search_results": "🔍 **অনুসন্ধানের ফলাফল:**"
            }
        }
    
    def set_user_language(self, user_id: str, language: str) -> bool:
        """Set user's preferred language"""
        if language in ["en", "bn"]:
            self.user_languages[user_id] = language
            self.save_user_languages()
            return True
        return False
    
    def get_user_language(self, user_id: str) -> str:
        """Get user's preferred language, default to English"""
        return self.user_languages.get(user_id, "en")
    
    def get_text(self, user_id: str, key: str, **kwargs) -> str:
        """Get translated text for user"""
        lang = self.get_user_language(user_id)
        text = self.translations.get(lang, self.translations["en"]).get(key, key)
        
        # Format with provided arguments
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text
    
    def get_command_descriptions(self, user_id: str) -> Dict[str, str]:
        """Get command descriptions in user's language"""
        lang = self.get_user_language(user_id)
        
        if lang == "bn":
            return {
                "start": "বট শুরু করুন এবং স্বাগত বার্তা দেখুন",
                "help": "সব উপলব্ধ কমান্ড সহ এই সাহায্য বার্তা দেখান",
                "chat": "জেমিনি AI এর সাথে চ্যাট করুন - সীমাহীন কথোপকথন",
                "wiki": "তথ্যের জন্য উইকিপিডিয়া অনুসন্ধান করুন",
                "study": "শিক্ষামূলক প্রশ্ন জিজ্ঞাসা করুন (পাঠ্যবই স্তর)",
                "download": "সীমাহীন ডাউনলোড - সব প্ল্যাটফর্ম থেকে ভিডিও/সঙ্গীত",
                "translate": "ভাষার মধ্যে পাঠ্য অনুবাদ করুন",
                "accessibility": "অ্যাক্সেসযোগ্যতা মোড টগল করুন (উচ্চ-বৈপরীত্য, পাঠ্য-থেকে-বক্তৃতা)",
                "speak": "পাঠ্যকে বক্তৃতা অডিও বার্তায় রূপান্তর করুন",
                "broadcast": "একাধিক ব্যবহারকারীদের বার্তা পাঠান (শুধুমাত্র অ্যাডমিন)",
                "contact": "বট প্রশাসকের সাথে যোগাযোগ করুন",
                "stats": "বট ব্যবহারের পরিসংখ্যান দেখান (শুধুমাত্র অ্যাডমিন)",
                "crypto": "ক্রিপ্টোকারেন্সি দাম এবং তথ্য পান",
                "alert": "দাম সতর্কতা সেট করুন",
                "live": "লাইভ বাজার ডেটা ফিড",
                "ban": "গ্রুপ থেকে ব্যবহারকারী নিষিদ্ধ করুন (অ্যাডমিন)",
                "mute": "গ্রুপে ব্যবহারকারী নিঃশব্দ করুন (অ্যাডমিন)",
                "english": "ইংরেজি ইন্টারফেসে পরিবর্তন করুন",
                "bangla": "বাংলা ইন্টারফেসে পরিবর্তন করুন"
            }
        else:
            return {
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
                "stats": "Show bot usage statistics (admin only)",
                "crypto": "Get cryptocurrency prices and info",
                "alert": "Set price alerts",
                "live": "Live market data feeds",
                "ban": "Ban user from group (admin)",
                "mute": "Mute user in group (admin)",
                "english": "Switch to English interface",
                "bangla": "Switch to Bangla interface"
            }

# Global instance
language_service = LanguageService()