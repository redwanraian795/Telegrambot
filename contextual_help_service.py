import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from character_customization_service import character_service

class ContextualHelpService:
    """
    Smart contextual help system with witty personality-driven explanations
    Provides intelligent, entertaining guidance based on user context and actions
    """
    
    def __init__(self):
        self.help_triggers_file = "help_triggers.json"
        self.user_help_history_file = "user_help_history.json"
        
        self.help_triggers = self.load_help_triggers()
        self.user_help_history = self.load_user_help_history()
        
        # Define contextual help scenarios
        self.help_scenarios = {
            "command_not_found": {
                "context": "user_types_invalid_command",
                "triggers": ["unknown command", "not found", "invalid"],
                "help_templates": {
                    "cheerful": [
                        "🌟 Oops! That command doesn't exist, but don't worry! Try `/help` to see all my amazing abilities!",
                        "😊 Hmm, I don't know that one! But I know lots of other cool tricks - check `/help` for the full menu!",
                        "✨ That's not a real command, but hey, creativity points! See what I CAN do with `/help`!"
                    ],
                    "cool": [
                        "😎 That command's not in my playbook. Hit `/help` to see what I'm actually good at.",
                        "🤙 Nice try, but that's not a thing. Check `/help` for the real commands.",
                        "💯 Command not found, but `/help` will show you what's actually available."
                    ],
                    "energetic": [
                        "⚡ WHOA! That command doesn't exist! But I've got TONS of real ones! Try `/help` NOW!",
                        "💥 NOPE! But I have SO MANY AWESOME commands! Check `/help` for the FULL POWER!",
                        "🚀 COMMAND ERROR! But don't worry - `/help` will show you my INCREDIBLE abilities!"
                    ],
                    "zen": [
                        "🧘 That command is like a leaf that never grew on my tree. Find the real ones with `/help`.",
                        "☯️ In the garden of commands, that one does not bloom. Seek wisdom with `/help`.",
                        "🌸 That path does not exist in my digital zen garden. Try `/help` for the true way."
                    ],
                    "funny": [
                        "🤪 That command is as real as my chances of becoming a stand-up comedian! Try `/help` instead!",
                        "😂 ERROR 404: Command not found, much like my sense of humor! But `/help` definitely works!",
                        "🎭 That command is faker than my British accent! Check `/help` for the real deal!"
                    ],
                    "professional": [
                        "💼 Command not recognized. Please reference `/help` for available functionality.",
                        "📊 Invalid command input. Access the command directory via `/help`.",
                        "🎯 Command not found in current system. Use `/help` to view available options."
                    ]
                }
            },
            
            "download_no_url": {
                "context": "download_command_without_url",
                "triggers": ["no url", "missing link", "empty download"],
                "help_templates": {
                    "cheerful": [
                        "🎬 Psst! I need a link to work my magic! Drop a YouTube URL and watch me fetch your content!",
                        "📥 Oops! You forgot the URL! Give me a link and I'll download it faster than you can say 'buffering'!",
                        "✨ Almost there! Just add a YouTube/TikTok link after `/download` and I'll do the rest!"
                    ],
                    "cool": [
                        "😎 Need a URL to make this happen. Drop the link and I'll handle business.",
                        "🔥 Missing the link, my friend. Add a URL and watch me work.",
                        "💪 Can't download air! Give me a URL and I'll get your content."
                    ],
                    "energetic": [
                        "⚡ I NEED A LINK TO UNLEASH MY DOWNLOADING POWER! Give me that URL!",
                        "💥 WHERE'S THE URL?! I can't download without it! Feed me those links!",
                        "🚀 LINK REQUIRED FOR MAXIMUM DOWNLOAD ENERGY! Paste that URL now!"
                    ],
                    "zen": [
                        "🌊 A download without a URL is like a river without water. Please provide the link.",
                        "🧘 The download command seeks its companion - the URL. Unite them and content shall flow.",
                        "☯️ To download, one must first provide that which shall be downloaded. The URL, young grasshopper."
                    ],
                    "funny": [
                        "🤷 I'm not a mind reader! (Though that would be a cool feature) Give me a URL!",
                        "😅 My crystal ball is broken! I need a URL to download anything!",
                        "🔮 Unless you want me to download your hopes and dreams, I'll need an actual URL!"
                    ],
                    "professional": [
                        "📋 URL parameter required for download function. Please include media link.",
                        "🎯 Download requires valid URL input. Format: `/download <URL>`",
                        "💻 Missing required parameter: URL. Please provide media link to proceed."
                    ]
                }
            },
            
            "translate_no_text": {
                "context": "translate_command_without_text",
                "triggers": ["no text", "missing translation", "empty translate"],
                "help_templates": {
                    "cheerful": [
                        "🌍 I speak many languages, but I need text to translate! Try `/translate Hello` to see magic happen!",
                        "✨ Oops! You forgot what to translate! Give me some text and I'll work my multilingual magic!",
                        "🗣️ I'm ready to translate, but I need words first! Add some text after `/translate`!"
                    ],
                    "cool": [
                        "😎 I'm a polyglot, but I need something to translate. Drop some text and I'll handle it.",
                        "🌐 Missing the text to translate. Give me words and I'll do my thing.",
                        "💯 Need actual text to translate. Format: `/translate <your text>`"
                    ],
                    "energetic": [
                        "⚡ I SPEAK ALL THE LANGUAGES! But I need TEXT to translate! Give me words!",
                        "💥 TRANSLATION MODE ACTIVATED! But WHERE'S the text?! Feed me sentences!",
                        "🚀 I'm READY to translate ANYTHING! Just tell me WHAT to translate!"
                    ],
                    "zen": [
                        "🌸 To translate, one must first have words to transform. Please provide text.",
                        "☯️ The translator awaits the gift of words. Share your text and I shall reshape it.",
                        "🧘 Silence cannot be translated into silence. Provide text for linguistic harmony."
                    ],
                    "funny": [
                        "😂 I can't translate mind-reading! Give me actual text to work with!",
                        "🤪 My universal translator is broken without input! Add some text!",
                        "🎭 I speak fluent gibberish, but I need YOUR text to translate!"
                    ],
                    "professional": [
                        "🔤 Text input required for translation service. Format: `/translate <text>`",
                        "📝 Missing text parameter. Please provide content to translate.",
                        "🎯 Translation function requires text input. Include message to translate."
                    ]
                }
            },
            
            "feature_discovery": {
                "context": "after_basic_usage",
                "triggers": ["completed_basic_task", "first_success"],
                "help_templates": {
                    "cheerful": [
                        "🎉 Great job! Did you know I can also create memes with `/meme`? Let's make something funny!",
                        "✨ Nice work! Want to try something new? I can generate stories with `/story` - let's get creative!",
                        "🌟 Awesome! I've got more tricks up my sleeve - try `/personality` to see all my different moods!"
                    ],
                    "cool": [
                        "👑 Smooth. Want to level up? Try `/crypto` for some market analysis.",
                        "🔥 Nice one. Check out `/meme` if you want to create something viral.",
                        "💯 Solid. I've got more skills - try `/character` to customize my personality."
                    ],
                    "energetic": [
                        "💥 EXCELLENT! Want MORE power? Try `/games` for EPIC trivia battles!",
                        "⚡ AMAZING! I can also create INCREDIBLE workout plans with `/workout`!",
                        "🚀 FANTASTIC! Check out `/meme` for HILARIOUS content creation!"
                    ],
                    "zen": [
                        "🌸 Well done. Perhaps you'd enjoy the creative flow of `/story` for tale weaving?",
                        "☯️ Success flows naturally. Consider `/meditation` - I mean `/character zen` for peaceful interactions.",
                        "🧘 Harmony achieved. Explore `/recipe` for nourishing culinary wisdom."
                    ],
                    "funny": [
                        "😂 Great! Want to see me fail at humor? Try `/meme` and watch my comedy career crash!",
                        "🤪 Nice! I can also butcher recipes with `/recipe` - culinary disasters guaranteed!",
                        "🎭 Excellent! Check out `/trivia` where my wrong answers are comedy gold!"
                    ],
                    "professional": [
                        "✅ Task completed successfully. Consider exploring `/portfolio` for financial tracking.",
                        "📊 Operation successful. Additional functionality available via `/admin` (if authorized).",
                        "🎯 Objective achieved. Expand capabilities with `/professional` tools suite."
                    ]
                }
            },
            
            "complex_command_guidance": {
                "context": "user_using_advanced_features",
                "triggers": ["complex_command", "multiple_parameters"],
                "help_templates": {
                    "cheerful": [
                        "🎯 Pro tip! Use `/character set <type>` to match my personality to your vibe!",
                        "✨ Heads up! You can customize my expressions with `/character customize <mood> <emoji>`!",
                        "🌟 Fun fact! Try `/personality` to see all my different character styles in action!"
                    ],
                    "cool": [
                        "😎 Pro move: `/character set cool` if you want me to stay this chill.",
                        "💯 Advanced tip: Customize my expressions to match your style.",
                        "🔥 Level up: Use `/character preview <type>` to test different personalities."
                    ],
                    "energetic": [
                        "⚡ POWER USER TIP! Set me to energetic mode with `/character set energetic`!",
                        "💥 ADVANCED FEATURE! Customize my emoji expressions for MAXIMUM PERSONALITY!",
                        "🚀 PRO LEVEL! Use `/character` to unlock FULL customization power!"
                    ],
                    "zen": [
                        "🌸 Wisdom: Customize your experience with `/character` for harmony.",
                        "☯️ Advanced path: Shape my responses to match your inner peace.",
                        "🧘 Master level: Use `/character zen` for tranquil interactions."
                    ],
                    "funny": [
                        "😂 Expert tip: Use `/character set funny` for maximum dad jokes! (You've been warned)",
                        "🤪 Advanced feature: Customize my expressions, because why not make it weirder?",
                        "🎭 Pro comedian move: Try different personalities and rate my jokes!"
                    ],
                    "professional": [
                        "💼 Advanced configuration: Use `/character set professional` for business mode.",
                        "📊 Optimization tip: Customize personality settings for workflow efficiency.",
                        "🎯 System enhancement: Character customization available via `/character` command."
                    ]
                }
            },
            
            "error_recovery": {
                "context": "after_command_error",
                "triggers": ["error occurred", "failed operation", "exception"],
                "help_templates": {
                    "cheerful": [
                        "😅 Oops! Something went wonky, but don't worry! These things happen - let's try again!",
                        "🌈 Every cloud has a silver lining! This error just means we get to try something new!",
                        "✨ Plot twist! Even I make mistakes sometimes. Let's troubleshoot this together!"
                    ],
                    "cool": [
                        "🤷 Things happen. No biggie - let's sort this out and keep moving.",
                        "😌 Error? More like a learning opportunity. We'll get this sorted.",
                        "💪 Minor setback. I'll handle it - that's what I'm here for."
                    ],
                    "energetic": [
                        "💥 ERROR ALERT! But NO PROBLEM! I'll bounce back STRONGER than ever!",
                        "⚡ OOPS! Even supercomputers have off days! Let's POWER THROUGH this!",
                        "🚀 SYSTEM HICCUP! But I'm UNSTOPPABLE! We'll crush this error together!"
                    ],
                    "zen": [
                        "🌊 Every error is a teacher. Let us learn from this moment and flow forward.",
                        "☯️ In the dance of code, sometimes we stumble. Balance will be restored.",
                        "🧘 This error, like all things, shall pass. Patience brings clarity."
                    ],
                    "funny": [
                        "🤦 Well, that went about as well as my stand-up career! Let's try again!",
                        "😂 Error 404: My competence not found! But seriously, let's fix this!",
                        "🎭 That failed harder than my jokes! But unlike my humor, this IS fixable!"
                    ],
                    "professional": [
                        "🔧 Error detected. Implementing diagnostic protocols for resolution.",
                        "📊 System exception encountered. Initiating recovery procedures.",
                        "⚡ Operational error logged. Preparing alternative approach."
                    ]
                }
            }
        }
        
        # Help timing controls
        self.help_cooldowns = {
            "command_not_found": timedelta(minutes=5),
            "download_no_url": timedelta(minutes=3),
            "translate_no_text": timedelta(minutes=3),
            "feature_discovery": timedelta(hours=2),
            "complex_command_guidance": timedelta(hours=1),
            "error_recovery": timedelta(minutes=10)
        }
    
    def load_help_triggers(self) -> Dict[str, Any]:
        """Load help trigger tracking"""
        if os.path.exists(self.help_triggers_file):
            try:
                with open(self.help_triggers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_help_triggers(self):
        """Save help trigger tracking"""
        with open(self.help_triggers_file, 'w', encoding='utf-8') as f:
            json.dump(self.help_triggers, f, indent=2, ensure_ascii=False)
    
    def load_user_help_history(self) -> Dict[str, Any]:
        """Load user help interaction history"""
        if os.path.exists(self.user_help_history_file):
            try:
                with open(self.user_help_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_user_help_history(self):
        """Save user help interaction history"""
        with open(self.user_help_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_help_history, f, indent=2, ensure_ascii=False)
    
    def should_show_help(self, user_id: str, scenario: str) -> bool:
        """Check if help should be shown based on cooldowns and user history"""
        user_id = str(user_id)
        current_time = datetime.now()
        
        # Initialize user history if needed
        if user_id not in self.user_help_history:
            self.user_help_history[user_id] = {}
        
        user_history = self.user_help_history[user_id]
        
        # Check if we're in cooldown period
        if scenario in user_history:
            last_shown = datetime.fromisoformat(user_history[scenario]['last_shown'])
            cooldown = self.help_cooldowns.get(scenario, timedelta(hours=1))
            
            if current_time - last_shown < cooldown:
                return False
        
        return True
    
    def get_contextual_help(self, user_id: str, scenario: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Get contextual help message based on scenario and user's character"""
        user_id = str(user_id)
        
        # Check if we should show help
        if not self.should_show_help(user_id, scenario):
            return None
        
        # Get user's character type
        user_char = character_service.get_user_character(user_id)
        character_type = user_char.get("character_type", "cheerful")
        
        # Get help scenario
        if scenario not in self.help_scenarios:
            return None
        
        scenario_data = self.help_scenarios[scenario]
        templates = scenario_data['help_templates']
        
        # Get appropriate template for character type
        if character_type not in templates:
            character_type = "cheerful"  # Fallback
        
        help_messages = templates[character_type]
        help_message = random.choice(help_messages)
        
        # Record that we showed help
        self.record_help_shown(user_id, scenario)
        
        return help_message
    
    def record_help_shown(self, user_id: str, scenario: str):
        """Record that help was shown to prevent spam"""
        user_id = str(user_id)
        current_time = datetime.now()
        
        if user_id not in self.user_help_history:
            self.user_help_history[user_id] = {}
        
        self.user_help_history[user_id][scenario] = {
            'last_shown': current_time.isoformat(),
            'count': self.user_help_history[user_id].get(scenario, {}).get('count', 0) + 1
        }
        
        self.save_user_help_history()
    
    def trigger_help_for_command_error(self, user_id: str, command: str) -> Optional[str]:
        """Show help for command not found errors"""
        return self.get_contextual_help(user_id, "command_not_found", {"command": command})
    
    def trigger_help_for_missing_parameter(self, user_id: str, command: str, missing_param: str) -> Optional[str]:
        """Show help for missing parameters"""
        if command == "download" and "url" in missing_param.lower():
            return self.get_contextual_help(user_id, "download_no_url")
        elif command == "translate" and "text" in missing_param.lower():
            return self.get_contextual_help(user_id, "translate_no_text")
        return None
    
    def trigger_help_for_successful_action(self, user_id: str, action: str) -> Optional[str]:
        """Show feature discovery help after successful basic actions"""
        # Only show for users who haven't seen this recently
        return self.get_contextual_help(user_id, "feature_discovery", {"action": action})
    
    def trigger_help_for_complex_command(self, user_id: str, command: str) -> Optional[str]:
        """Show guidance for complex commands"""
        complex_commands = ["character", "crypto", "admin", "meme", "story"]
        if command in complex_commands:
            return self.get_contextual_help(user_id, "complex_command_guidance", {"command": command})
        return None
    
    def trigger_help_for_error(self, user_id: str, error_type: str) -> Optional[str]:
        """Show encouraging help after errors"""
        return self.get_contextual_help(user_id, "error_recovery", {"error": error_type})
    
    def get_user_help_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's help interaction statistics"""
        user_id = str(user_id)
        if user_id not in self.user_help_history:
            return {"total_helps": 0, "scenarios": {}}
        
        user_data = self.user_help_history[user_id]
        total_helps = sum(scenario.get('count', 0) for scenario in user_data.values())
        
        return {
            "total_helps": total_helps,
            "scenarios": {scenario: data.get('count', 0) for scenario, data in user_data.items()}
        }
    
    def reset_user_help_history(self, user_id: str) -> bool:
        """Reset help history for a user"""
        user_id = str(user_id)
        if user_id in self.user_help_history:
            del self.user_help_history[user_id]
            self.save_user_help_history()
            return True
        return False
    
    def create_custom_help_bubble(self, user_id: str, message: str, bubble_type: str = "info") -> str:
        """Create a custom help bubble with user's character style"""
        user_char = character_service.get_user_character(user_id)
        character_type = user_char.get("character_type", "cheerful")
        
        # Get appropriate emoji for bubble type
        emoji_map = {
            "cheerful": {"info": "💡", "warning": "⚠️", "success": "🎉", "error": "😅"},
            "cool": {"info": "💯", "warning": "🔥", "success": "👑", "error": "🤷"},
            "energetic": {"info": "⚡", "warning": "💥", "success": "🚀", "error": "💪"},
            "zen": {"info": "🌸", "warning": "🌊", "success": "☯️", "error": "🧘"},
            "funny": {"info": "🤔", "warning": "😬", "success": "😂", "error": "🤪"},
            "professional": {"info": "📋", "warning": "⚠️", "success": "✅", "error": "🔧"}
        }
        
        emoji = emoji_map.get(character_type, emoji_map["cheerful"])[bubble_type]
        return f"{emoji} **BotBuddy Help:** {message}"
    
    def get_help_bubble(self, user_id: str, bubble_type: str = "info", message: str = "") -> str:
        """Get help bubble - alias for create_custom_help_bubble"""
        return self.create_custom_help_bubble(user_id, message, bubble_type)

# Create global instance for import
help_service = ContextualHelpService()

# Initialize global service
contextual_help_service = ContextualHelpService()