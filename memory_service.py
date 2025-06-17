import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

class MemoryService:
    """Advanced conversation memory and user context tracking"""
    
    def __init__(self):
        self.memory_file = "user_memory.json"
        self.context_file = "conversation_context.json"
        self.personalities_file = "user_personalities.json"
        self.memory_data = self.load_memory()
        self.context_data = self.load_context()
        self.personalities = self.load_personalities()
    
    def load_memory(self) -> Dict[str, Any]:
        """Load user memory data"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_memory(self):
        """Save user memory data"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory_data, f, indent=2)
        except Exception:
            pass
    
    def load_context(self) -> Dict[str, Any]:
        """Load conversation context"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_context(self):
        """Save conversation context"""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context_data, f, indent=2)
        except Exception:
            pass
    
    def load_personalities(self) -> Dict[str, Any]:
        """Load user personality profiles"""
        try:
            if os.path.exists(self.personalities_file):
                with open(self.personalities_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_personalities(self):
        """Save user personality profiles"""
        try:
            with open(self.personalities_file, 'w') as f:
                json.dump(self.personalities, f, indent=2)
        except Exception:
            pass
    
    def remember_fact(self, user_id: str, fact: str, category: str = "general"):
        """Store a fact about the user"""
        if user_id not in self.memory_data:
            self.memory_data[user_id] = {
                "facts": {},
                "preferences": {},
                "interests": [],
                "conversation_history": [],
                "important_dates": {},
                "locations": []
            }
        
        if category not in self.memory_data[user_id]["facts"]:
            self.memory_data[user_id]["facts"][category] = []
        
        fact_entry = {
            "fact": fact,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.8
        }
        
        self.memory_data[user_id]["facts"][category].append(fact_entry)
        self.save_memory()
    
    def get_user_facts(self, user_id: str, category: str = None) -> List[Dict]:
        """Retrieve facts about a user"""
        if user_id not in self.memory_data:
            return []
        
        if category:
            return self.memory_data[user_id]["facts"].get(category, [])
        
        all_facts = []
        for cat_facts in self.memory_data[user_id]["facts"].values():
            all_facts.extend(cat_facts)
        
        return sorted(all_facts, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    def store_user_fact(self, user_id: str, category: str, fact: str):
        """Store a fact about the user (alias for remember_fact)"""
        self.remember_fact(user_id, fact, category)
    
    def store_conversation(self, user_id: str, message: str, response: str, topic: str = None):
        """Store a conversation exchange"""
        self.update_conversation_context(user_id, message, response, topic)
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations for a user"""
        if user_id not in self.context_data:
            return []
        
        recent = self.context_data[user_id].get("recent_messages", [])
        return recent[-limit:] if recent else []
    
    def store_user_preference(self, user_id: str, preference_key: str, value: str):
        """Store user preference"""
        if user_id not in self.memory_data:
            self.memory_data[user_id] = {
                "facts": {},
                "preferences": {},
                "interests": [],
                "conversation_history": [],
                "important_dates": {},
                "locations": []
            }
        
        self.memory_data[user_id]["preferences"][preference_key] = value
        self.save_memory()
    
    def get_user_preference(self, user_id: str, preference_key: str) -> str:
        """Get user preference"""
        if user_id not in self.memory_data:
            return None
        
        return self.memory_data[user_id]["preferences"].get(preference_key)
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context and memory data"""
        if user_id not in self.memory_data:
            return {}
        
        return {
            "facts": self.get_user_facts(user_id),
            "preferences": self.memory_data[user_id]["preferences"],
            "recent_conversations": self.get_recent_conversations(user_id, limit=5)
        }
    
    def update_conversation_context(self, user_id: str, message: str, response: str, topic: str = None):
        """Track conversation context and topics"""
        if user_id not in self.context_data:
            self.context_data[user_id] = {
                "recent_messages": [],
                "topics": defaultdict(int),
                "conversation_style": {},
                "last_interaction": None
            }
        
        # Add to recent messages (keep last 20)
        context_entry = {
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "topic": topic
        }
        
        self.context_data[user_id]["recent_messages"].append(context_entry)
        self.context_data[user_id]["recent_messages"] = self.context_data[user_id]["recent_messages"][-20:]
        
        # Track topics
        if topic:
            self.context_data[user_id]["topics"][topic] += 1
        
        # Update last interaction
        self.context_data[user_id]["last_interaction"] = datetime.now().isoformat()
        
        self.save_context()
    
    def analyze_personality(self, user_id: str, message: str):
        """Analyze and build user personality profile"""
        if user_id not in self.personalities:
            self.personalities[user_id] = {
                "traits": {},
                "communication_style": {},
                "interests": {},
                "mood_patterns": [],
                "learning_style": "unknown",
                "humor_preference": "unknown"
            }
        
        # Simple personality analysis based on message patterns
        message_lower = message.lower()
        
        # Detect humor preference
        if any(word in message_lower for word in ["lol", "haha", "funny", "joke", "😂", "🤣"]):
            self.personalities[user_id]["humor_preference"] = "enjoys_humor"
        
        # Detect communication style
        if len(message.split()) > 20:
            self.personalities[user_id]["communication_style"]["verbose"] = True
        elif len(message.split()) < 5:
            self.personalities[user_id]["communication_style"]["concise"] = True
        
        # Detect question patterns
        if "?" in message:
            self.personalities[user_id]["traits"]["curious"] = self.personalities[user_id]["traits"].get("curious", 0) + 1
        
        # Detect politeness
        if any(word in message_lower for word in ["please", "thank", "sorry", "excuse"]):
            self.personalities[user_id]["traits"]["polite"] = self.personalities[user_id]["traits"].get("polite", 0) + 1
        
        self.save_personalities()
    
    def get_conversation_context(self, user_id: str) -> str:
        """Get formatted conversation context for AI responses"""
        if user_id not in self.context_data:
            return ""
        
        context = self.context_data[user_id]
        recent_topics = sorted(context["topics"].items(), key=lambda x: x[1], reverse=True)[:3]
        recent_messages = context["recent_messages"][-3:]
        
        context_summary = f"User context: "
        
        if recent_topics:
            topics_str = ", ".join([topic for topic, count in recent_topics])
            context_summary += f"Recent topics: {topics_str}. "
        
        if recent_messages:
            context_summary += f"Last discussed: {recent_messages[-1]['topic'] or 'general'}. "
        
        # Add personality insights
        if user_id in self.personalities:
            personality = self.personalities[user_id]
            if personality["humor_preference"] == "enjoys_humor":
                context_summary += "User enjoys humor. "
            if personality["communication_style"].get("verbose"):
                context_summary += "User prefers detailed responses. "
        
        return context_summary
    
    def get_user_summary(self, user_id: str) -> str:
        """Get comprehensive user summary for admin"""
        if user_id not in self.memory_data and user_id not in self.context_data:
            return "No data available for this user."
        
        summary = f"**User {user_id} Summary:**\n\n"
        
        # Facts
        facts = self.get_user_facts(user_id)
        if facts:
            summary += f"**Remembered Facts:** {len(facts)} items\n"
            for fact in facts[:3]:
                summary += f"• {fact['fact']}\n"
        
        # Conversation patterns
        if user_id in self.context_data:
            context = self.context_data[user_id]
            top_topics = sorted(context["topics"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_topics:
                summary += f"\n**Top Topics:** {', '.join([t[0] for t in top_topics])}\n"
        
        # Personality
        if user_id in self.personalities:
            personality = self.personalities[user_id]
            summary += f"\n**Communication Style:** {personality['communication_style']}\n"
            summary += f"**Humor Preference:** {personality['humor_preference']}\n"
        
        return summary

# Global instance
memory_service = MemoryService()