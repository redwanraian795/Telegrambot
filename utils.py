import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config import USER_DATABASE_FILE, ADMIN_MESSAGES_FILE, DOWNLOADS_DIR, RATE_LIMIT_MESSAGES, RATE_LIMIT_MEDIA_DOWNLOADS, RATE_LIMIT_BROADCASTS

class UserDatabase:
    def __init__(self):
        self.data = self.load_database()
    
    def load_database(self) -> Dict[str, Any]:
        if os.path.exists(USER_DATABASE_FILE):
            try:
                with open(USER_DATABASE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"users": {}, "broadcast_lists": [], "stats": {"total_messages": 0, "total_users": 0}}
    
    def save_database(self):
        try:
            with open(USER_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def add_user(self, user_id: str, username: str = None, first_name: str = None):
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "username": username,
                "first_name": first_name,
                "joined_date": datetime.now().isoformat(),
                "message_count": 0,
                "last_activity": datetime.now().isoformat(),
                "rate_limits": {
                    "messages": [],
                    "downloads": [],
                    "broadcasts": []
                }
            }
            self.data["stats"]["total_users"] += 1
            self.save_database()
    
    def update_user_activity(self, user_id: str):
        if user_id in self.data["users"]:
            self.data["users"][user_id]["last_activity"] = datetime.now().isoformat()
            self.data["users"][user_id]["message_count"] += 1
            self.data["stats"]["total_messages"] += 1
            self.save_database()
    
    def get_user_stats(self) -> Dict[str, Any]:
        return self.data["stats"]
    
    def get_all_users(self) -> List[str]:
        return list(self.data["users"].keys())

class RateLimiter:
    def __init__(self, db: UserDatabase):
        self.db = db
    
    def check_rate_limit(self, user_id: str, limit_type: str) -> bool:
        now = datetime.now()
        user_data = self.db.data["users"].get(user_id, {})
        rate_limits = user_data.get("rate_limits", {})
        
        if limit_type not in rate_limits:
            rate_limits[limit_type] = []
        
        # Clean old timestamps
        if limit_type == "messages":
            cutoff = now - timedelta(minutes=1)
            limit = RATE_LIMIT_MESSAGES
        elif limit_type == "downloads":
            cutoff = now - timedelta(hours=1)
            limit = RATE_LIMIT_MEDIA_DOWNLOADS
        elif limit_type == "broadcasts":
            cutoff = now - timedelta(days=1)
            limit = RATE_LIMIT_BROADCASTS
        else:
            return True
        
        # Remove old timestamps
        rate_limits[limit_type] = [
            ts for ts in rate_limits[limit_type] 
            if datetime.fromisoformat(ts) > cutoff
        ]
        
        # Check if limit exceeded
        if len(rate_limits[limit_type]) >= limit:
            return False
        
        # Add current timestamp
        rate_limits[limit_type].append(now.isoformat())
        self.db.save_database()
        return True

class AdminMessageHandler:
    def __init__(self):
        self.messages = self.load_messages()
    
    def load_messages(self) -> List[Dict[str, Any]]:
        if os.path.exists(ADMIN_MESSAGES_FILE):
            try:
                with open(ADMIN_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def save_messages(self):
        try:
            with open(ADMIN_MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving admin messages: {e}")
    
    def add_message(self, user_id: str, username: str, message: str):
        self.messages.append({
            "user_id": user_id,
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "unread"
        })
        self.save_messages()
    
    def get_unread_messages(self) -> List[Dict[str, Any]]:
        return [msg for msg in self.messages if msg["status"] == "unread"]
    
    def mark_as_read(self, message_index: int):
        if 0 <= message_index < len(self.messages):
            self.messages[message_index]["status"] = "read"
            self.save_messages()

def create_downloads_directory():
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

def format_file_size(bytes_size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def clean_old_downloads():
    """Clean downloads older than 24 hours"""
    if not os.path.exists(DOWNLOADS_DIR):
        return
    
    cutoff = time.time() - (24 * 60 * 60)  # 24 hours ago
    for filename in os.listdir(DOWNLOADS_DIR):
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.isfile(filepath) and os.path.getctime(filepath) < cutoff:
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing old download {filepath}: {e}")

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Import user access service
from user_access_service import user_access_service
