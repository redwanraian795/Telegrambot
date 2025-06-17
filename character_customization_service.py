import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

class CharacterCustomizationService:
    """
    Playful character customization with mood-based emoji expressions
    Allows users to personalize their BotBuddy experience
    """
    
    def __init__(self):
        self.user_characters_file = "user_characters.json"
        self.user_characters = self.load_user_characters()
        
        # Predefined character personalities with emoji expressions
        self.character_templates = {
            "cheerful": {
                "name": "Cheerful Buddy",
                "description": "Always upbeat and positive! 🌈",
                "expressions": {
                    "greeting": ["😊", "😄", "🌟", "✨", "🎉"],
                    "working": ["💪", "⚡", "🔥", "🚀", "✨"],
                    "success": ["🎉", "🥳", "🌟", "✅", "🎊"],
                    "error": ["😅", "🤗", "💫", "🌈", "😊"],
                    "thinking": ["🤔", "💭", "🌟", "✨", "🔍"],
                    "downloading": ["📥", "⬇️", "💫", "🌟", "⚡"],
                    "uploading": ["📤", "⬆️", "🚀", "✨", "🌟"]
                },
                "phrases": {
                    "greeting": ["Hey there! Ready for some fun?", "What adventure shall we go on today?", "Yay! Let's make something awesome!"],
                    "working": ["Working my magic!", "Almost there, hang tight!", "Making progress, woohoo!"],
                    "success": ["Nailed it! Amazing work!", "Success! That was fantastic!", "Boom! Mission accomplished!"],
                    "error": ["Oops! No worries, let's try again!", "Tiny hiccup, but we've got this!", "Plot twist! Let's figure this out together!"]
                }
            },
            
            "cool": {
                "name": "Cool Buddy",
                "description": "Laid-back and smooth operator 😎",
                "expressions": {
                    "greeting": ["😎", "🤙", "👑", "💯", "🔥"],
                    "working": ["⚡", "🚀", "💻", "🔧", "💪"],
                    "success": ["💯", "🔥", "👑", "✨", "💪"],
                    "error": ["🤷", "😌", "🔄", "💭", "🎯"],
                    "thinking": ["🤔", "💭", "🧠", "⚡", "🎯"],
                    "downloading": ["📥", "⬇️", "💾", "🔥", "⚡"],
                    "uploading": ["📤", "⬆️", "🚀", "💯", "🔥"]
                },
                "phrases": {
                    "greeting": ["What's up! Ready to roll?", "Hey, let's get this done smoothly", "Sup! Time to work some magic"],
                    "working": ["On it like a pro", "Smooth operator at work", "Making it happen"],
                    "success": ["Clean execution, nice!", "That's how it's done!", "Smooth as butter!"],
                    "error": ["No biggie, we'll sort this out", "Minor glitch, already on it", "Happens to the best of us"]
                }
            },
            
            "energetic": {
                "name": "Energy Buddy",
                "description": "High-energy and super enthusiastic! ⚡",
                "expressions": {
                    "greeting": ["🤩", "⚡", "🔥", "💥", "🚀"],
                    "working": ["💨", "⚡", "🏃", "💪", "🔥"],
                    "success": ["💥", "🎆", "🔥", "⚡", "🚀"],
                    "error": ["💨", "🔄", "⚡", "💪", "🎯"],
                    "thinking": ["⚡", "💡", "🧠", "💭", "🔥"],
                    "downloading": ["📥", "💨", "⚡", "🔥", "💥"],
                    "uploading": ["📤", "🚀", "💨", "⚡", "💥"]
                },
                "phrases": {
                    "greeting": ["LET'S GOOO! Ready to crush this?", "ENERGY LEVELS: MAXIMUM!", "Time to DOMINATE this task!"],
                    "working": ["FULL SPEED AHEAD!", "CRUSHING IT RIGHT NOW!", "MAXIMUM EFFORT ENGAGED!"],
                    "success": ["ABSOLUTELY DESTROYED IT!", "VICTORY ACHIEVED!", "THAT WAS INCREDIBLE!"],
                    "error": ["NO PROBLEM! WE'LL POWER THROUGH!", "QUICK ADJUSTMENT INCOMING!", "UNSTOPPABLE FORCE ACTIVATED!"]
                }
            },
            
            "zen": {
                "name": "Zen Buddy",
                "description": "Calm, wise, and peaceful 🧘",
                "expressions": {
                    "greeting": ["🧘", "☯️", "🌸", "🕊️", "🌿"],
                    "working": ["🌊", "🌸", "⏳", "🧘", "☯️"],
                    "success": ["🌟", "🌸", "☯️", "🕊️", "✨"],
                    "error": ["🌊", "🌸", "☯️", "🧘", "🌿"],
                    "thinking": ["🧘", "💭", "🌸", "☯️", "🧠"],
                    "downloading": ["📥", "🌊", "⏳", "🌸", "☯️"],
                    "uploading": ["📤", "🌊", "⏳", "🌸", "☯️"]
                },
                "phrases": {
                    "greeting": ["Welcome, friend. How may I assist you today?", "Greetings. Let us begin this journey together.", "Peace be with you. What shall we accomplish?"],
                    "working": ["Patience, progress flows like water", "Working with mindful precision", "All things unfold in their time"],
                    "success": ["Balance achieved, well done", "Success flows naturally", "Harmony restored"],
                    "error": ["Every challenge teaches us wisdom", "From obstacles, we learn and grow", "Peace through understanding"]
                }
            },
            
            "funny": {
                "name": "Comedy Buddy",
                "description": "Always ready with a joke! 😂",
                "expressions": {
                    "greeting": ["😂", "🤣", "😄", "🎭", "🤪"],
                    "working": ["🤓", "😜", "🎯", "🤹", "😂"],
                    "success": ["🎉", "😂", "🥳", "🎭", "🤩"],
                    "error": ["🤦", "😅", "🙃", "🤷", "😂"],
                    "thinking": ["🤔", "💭", "🧠", "😜", "🎭"],
                    "downloading": ["📥", "🤹", "⬇️", "😄", "🎯"],
                    "uploading": ["📤", "🤹", "⬆️", "😄", "🎯"]
                },
                "phrases": {
                    "greeting": ["Why did the bot cross the code? To get to the other side!", "Knock knock! Who's there? Your helpful assistant!", "Ready to debug some laughs together?"],
                    "working": ["Working harder than a one-legged cat in a sandbox!", "Processing faster than my jokes are bad!", "Crunching data like potato chips!"],
                    "success": ["Ta-da! Like magic, but with more electricity!", "Success! Even my errors are features now!", "Boom! Nailed it like a hammer with GPS!"],
                    "error": ["Oops! Even supercomputers have off days!", "Error 404: Perfection not found, but close enough!", "Plot twist! This wasn't supposed to happen!"]
                }
            },
            
            "professional": {
                "name": "Pro Buddy",
                "description": "Efficient and business-focused 💼",
                "expressions": {
                    "greeting": ["💼", "👔", "📊", "⚡", "🎯"],
                    "working": ["⚡", "🔧", "💻", "📊", "🎯"],
                    "success": ["✅", "📈", "💯", "🎯", "⚡"],
                    "error": ["🔧", "📊", "🔄", "💻", "⚡"],
                    "thinking": ["🧠", "💭", "📊", "🎯", "💻"],
                    "downloading": ["📥", "📊", "💾", "⚡", "🎯"],
                    "uploading": ["📤", "📊", "💾", "⚡", "🎯"]
                },
                "phrases": {
                    "greeting": ["Good day! Ready to optimize productivity?", "Hello! Let's achieve our objectives efficiently.", "Greetings! Time to execute our strategy."],
                    "working": ["Processing request with maximum efficiency", "Executing task with precision", "Implementing solution systematically"],
                    "success": ["Objective completed successfully", "Task executed within parameters", "Deliverable achieved on schedule"],
                    "error": ["Minor deviation detected, implementing correction", "Adjusting approach for optimal results", "Recalibrating for improved performance"]
                }
            }
        }
        
        # Mood multipliers for different situations
        self.mood_contexts = {
            "morning": {"energy": 1.2, "cheerfulness": 1.3, "professionalism": 1.1},
            "afternoon": {"energy": 1.0, "cheerfulness": 1.0, "professionalism": 1.2},
            "evening": {"energy": 0.8, "cheerfulness": 1.1, "professionalism": 0.9},
            "weekend": {"energy": 1.1, "cheerfulness": 1.4, "professionalism": 0.7},
            "error_context": {"patience": 1.5, "humor": 1.2, "supportiveness": 1.4},
            "success_context": {"celebration": 1.5, "energy": 1.3, "positivity": 1.4}
        }
    
    def load_user_characters(self) -> Dict[str, Any]:
        """Load user character preferences"""
        if os.path.exists(self.user_characters_file):
            try:
                with open(self.user_characters_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_user_characters(self):
        """Save user character preferences"""
        with open(self.user_characters_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_characters, f, indent=2, ensure_ascii=False)
    
    def get_user_character(self, user_id: str) -> Dict[str, Any]:
        """Get user's current character settings"""
        user_id = str(user_id)
        if user_id not in self.user_characters:
            # Default to cheerful character
            self.user_characters[user_id] = {
                "character_type": "cheerful",
                "custom_expressions": {},
                "mood_preferences": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_user_characters()
        
        return self.user_characters[user_id]
    
    def set_user_character(self, user_id: str, character_type: str) -> Dict[str, Any]:
        """Set user's character type"""
        user_id = str(user_id)
        
        if character_type not in self.character_templates:
            return {"success": False, "error": "Invalid character type"}
        
        user_char = self.get_user_character(user_id)
        user_char["character_type"] = character_type
        user_char["last_updated"] = datetime.now().isoformat()
        
        self.save_user_characters()
        
        template = self.character_templates[character_type]
        return {
            "success": True,
            "character": template,
            "message": f"Character set to {template['name']}! {template['description']}"
        }
    
    def customize_expression(self, user_id: str, expression_type: str, new_emoji: str) -> Dict[str, Any]:
        """Customize specific emoji expression for user"""
        user_id = str(user_id)
        user_char = self.get_user_character(user_id)
        
        if "custom_expressions" not in user_char:
            user_char["custom_expressions"] = {}
        
        if expression_type not in user_char["custom_expressions"]:
            user_char["custom_expressions"][expression_type] = []
        
        # Add new emoji to custom expressions
        if new_emoji not in user_char["custom_expressions"][expression_type]:
            user_char["custom_expressions"][expression_type].append(new_emoji)
            user_char["last_updated"] = datetime.now().isoformat()
            self.save_user_characters()
            
            return {
                "success": True,
                "message": f"Added {new_emoji} to your {expression_type} expressions!"
            }
        else:
            return {
                "success": False,
                "message": f"{new_emoji} is already in your {expression_type} expressions"
            }
    
    def get_expression(self, user_id: str, expression_type: str, context: str = None) -> str:
        """Get appropriate emoji expression for user and context"""
        user_char = self.get_user_character(user_id)
        character_type = user_char.get("character_type", "cheerful")
        template = self.character_templates[character_type]
        
        # Start with template expressions
        expressions = template["expressions"].get(expression_type, ["😊"])
        
        # Add custom expressions if any
        custom_expressions = user_char.get("custom_expressions", {}).get(expression_type, [])
        if custom_expressions:
            expressions.extend(custom_expressions)
        
        # Apply context-based mood adjustments
        if context and context in self.mood_contexts:
            # For now, just return random from available expressions
            # Future: implement mood multiplier logic
            pass
        
        return random.choice(expressions)
    
    def get_phrase(self, user_id: str, phrase_type: str, context: str = None) -> str:
        """Get appropriate phrase for user and context"""
        user_char = self.get_user_character(user_id)
        character_type = user_char.get("character_type", "cheerful")
        template = self.character_templates[character_type]
        
        phrases = template["phrases"].get(phrase_type, ["Hello there!"])
        return random.choice(phrases)
    
    def get_character_message(self, user_id: str, message_type: str, context: str = None) -> str:
        """Get complete character message with emoji and phrase"""
        emoji = self.get_expression(user_id, message_type, context)
        phrase = self.get_phrase(user_id, message_type, context)
        
        return f"{emoji} **BotBuddy:** '{phrase}'"
    
    def get_available_characters(self) -> Dict[str, Dict[str, Any]]:
        """Get all available character templates"""
        return {k: {"name": v["name"], "description": v["description"]} 
                for k, v in self.character_templates.items()}
    
    def get_user_character_info(self, user_id: str) -> Dict[str, Any]:
        """Get detailed info about user's current character"""
        user_char = self.get_user_character(user_id)
        character_type = user_char.get("character_type", "cheerful")
        template = self.character_templates[character_type]
        
        return {
            "current_character": template,
            "custom_expressions": user_char.get("custom_expressions", {}),
            "expressions_count": sum(len(exprs) for exprs in user_char.get("custom_expressions", {}).values()),
            "character_type": character_type,
            "last_updated": user_char.get("last_updated", "Never")
        }
    
    def reset_character(self, user_id: str) -> Dict[str, Any]:
        """Reset user's character to default"""
        user_id = str(user_id)
        if user_id in self.user_characters:
            del self.user_characters[user_id]
            self.save_user_characters()
        
        return {
            "success": True,
            "message": "Character reset to default (Cheerful Buddy)!"
        }
    
    def get_character_response(self, user_id: str, message_type: str, context: str = None) -> str:
        """Get character response - alias for get_character_message"""
        return self.get_character_message(user_id, message_type, context)
    
    def create_mood_preview(self, character_type: str) -> str:
        """Create a preview of character expressions"""
        if character_type not in self.character_templates:
            return "Invalid character type"
        
        template = self.character_templates[character_type]
        preview = f"**{template['name']}** - {template['description']}\n\n"
        
        for mood, emojis in template["expressions"].items():
            preview += f"**{mood.title()}:** {' '.join(emojis[:3])}\n"
        
        return preview

# Initialize global service
character_service = CharacterCustomizationService()