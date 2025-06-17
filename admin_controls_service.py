import asyncio
import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import logging
from telegram.ext import ContextTypes
from telegram import Bot, Update, ChatMember

logger = logging.getLogger(__name__)

class AdminControlsService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.banned_words = self.load_banned_words()
        self.spam_detection = self.load_spam_settings()
        self.user_warnings = self.load_user_warnings()
        self.banned_users = self.load_banned_users()
        self.muted_users = self.load_muted_users()
        self.admin_settings = self.load_admin_settings()
        
    def load_banned_words(self) -> Set[str]:
        """Load banned words list"""
        try:
            if os.path.exists("banned_words.json"):
                with open("banned_words.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get("words", []))
        except Exception as e:
            logger.error(f"Error loading banned words: {e}")
        return {
            "spam", "scam", "fake", "porn", "xxx", "18+", "adult", 
            "casino", "gambling", "bitcoin scam", "free money", 
            "click here", "telegram.me", "t.me", "join now"
        }
    
    def save_banned_words(self):
        """Save banned words list"""
        try:
            with open("banned_words.json", 'w', encoding='utf-8') as f:
                json.dump({"words": list(self.banned_words)}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving banned words: {e}")
    
    def load_spam_settings(self) -> Dict[str, Any]:
        """Load spam detection settings"""
        try:
            if os.path.exists("spam_settings.json"):
                with open("spam_settings.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading spam settings: {e}")
        return {
            "max_messages_per_minute": 10,
            "max_identical_messages": 3,
            "max_links_per_message": 2,
            "auto_ban_threshold": 5,
            "auto_mute_duration": 3600,  # 1 hour in seconds
            "link_detection_enabled": True,
            "bio_link_ban": True
        }
    
    def save_spam_settings(self):
        """Save spam detection settings"""
        try:
            with open("spam_settings.json", 'w', encoding='utf-8') as f:
                json.dump(self.spam_detection, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving spam settings: {e}")
    
    def load_user_warnings(self) -> Dict[str, Any]:
        """Load user warnings database"""
        try:
            if os.path.exists("user_warnings.json"):
                with open("user_warnings.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user warnings: {e}")
        return {}
    
    def save_user_warnings(self):
        """Save user warnings database"""
        try:
            with open("user_warnings.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_warnings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving user warnings: {e}")
    
    def load_banned_users(self) -> Dict[str, Any]:
        """Load banned users database"""
        try:
            if os.path.exists("banned_users.json"):
                with open("banned_users.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading banned users: {e}")
        return {}
    
    def save_banned_users(self):
        """Save banned users database"""
        try:
            with open("banned_users.json", 'w', encoding='utf-8') as f:
                json.dump(self.banned_users, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving banned users: {e}")
    
    def load_muted_users(self) -> Dict[str, Any]:
        """Load muted users database"""
        try:
            if os.path.exists("muted_users.json"):
                with open("muted_users.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading muted users: {e}")
        return {}
    
    def save_muted_users(self):
        """Save muted users database"""
        try:
            with open("muted_users.json", 'w', encoding='utf-8') as f:
                json.dump(self.muted_users, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving muted users: {e}")
    
    def load_admin_settings(self) -> Dict[str, Any]:
        """Load admin settings"""
        try:
            if os.path.exists("admin_settings.json"):
                with open("admin_settings.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading admin settings: {e}")
        return {
            "auto_moderation": True,
            "delete_spam_messages": True,
            "warn_before_ban": True,
            "max_warnings": 3,
            "log_violations": True,
            "notify_admins": True
        }
    
    def save_admin_settings(self):
        """Save admin settings"""
        try:
            with open("admin_settings.json", 'w', encoding='utf-8') as f:
                json.dump(self.admin_settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving admin settings: {e}")
    
    async def check_message_violations(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check message for violations and take action"""
        try:
            message = update.effective_message
            user = update.effective_user
            chat = update.effective_chat
            
            if not message or not user or not chat:
                return False
            
            if chat.type not in ['group', 'supergroup']:
                return False  # Only moderate groups
            
            user_id = str(user.id)
            chat_id = str(chat.id)
            
            violations = []
            
            # Check if user is banned
            if self.is_user_banned(user_id, chat_id):
                await self.ban_user(update, context, user_id, "Previously banned user")
                return True
            
            # Check if user is muted
            if self.is_user_muted(user_id, chat_id):
                await message.delete()
                return True
            
            # Check for banned words
            if message.text:
                banned_word_found = self.check_banned_words(message.text)
                if banned_word_found:
                    violations.append(f"Banned word: {banned_word_found}")
            
            # Check for spam patterns
            spam_detected = await self.check_spam_patterns(user_id, chat_id, message)
            if spam_detected:
                violations.extend(spam_detected)
            
            # Check for links
            if self.spam_detection.get("link_detection_enabled", True):
                links_found = self.check_message_links(message.text or "")
                if links_found > self.spam_detection.get("max_links_per_message", 2):
                    violations.append(f"Too many links: {links_found}")
            
            # Check user bio for links (if enabled)
            if self.spam_detection.get("bio_link_ban", True):
                bio_violation = await self.check_user_bio_links(user)
                if bio_violation:
                    violations.append(bio_violation)
            
            # Take action if violations found
            if violations:
                await self.handle_violations(update, context, user_id, chat_id, violations)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking message violations: {e}")
            return False
    
    def check_banned_words(self, text: str) -> Optional[str]:
        """Check text for banned words"""
        if not text:
            return None
        
        text_lower = text.lower()
        for banned_word in self.banned_words:
            if banned_word.lower() in text_lower:
                return banned_word
        return None
    
    async def check_spam_patterns(self, user_id: str, chat_id: str, message) -> List[str]:
        """Check for spam patterns"""
        violations = []
        
        try:
            # Initialize user tracking
            if user_id not in self.user_warnings:
                self.user_warnings[user_id] = {
                    "message_history": [],
                    "last_messages": [],
                    "violation_count": 0
                }
            
            user_data = self.user_warnings[user_id]
            current_time = time.time()
            
            # Clean old message history (keep last minute)
            user_data["message_history"] = [
                msg for msg in user_data["message_history"] 
                if current_time - msg["timestamp"] < 60
            ]
            
            # Add current message
            message_data = {
                "timestamp": current_time,
                "text": message.text or "",
                "chat_id": chat_id
            }
            user_data["message_history"].append(message_data)
            
            # Check message frequency
            recent_messages = len(user_data["message_history"])
            if recent_messages > self.spam_detection.get("max_messages_per_minute", 10):
                violations.append(f"Message spam: {recent_messages} messages/minute")
            
            # Check for identical messages
            if message.text:
                identical_count = sum(
                    1 for msg in user_data["message_history"][-10:] 
                    if msg["text"] == message.text
                )
                if identical_count >= self.spam_detection.get("max_identical_messages", 3):
                    violations.append(f"Identical message spam: {identical_count} times")
            
            self.save_user_warnings()
            
        except Exception as e:
            logger.error(f"Error checking spam patterns: {e}")
        
        return violations
    
    def check_message_links(self, text: str) -> int:
        """Count links in message"""
        if not text:
            return 0
        
        # Common link patterns
        link_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r't\.me/[a-zA-Z0-9_]+',
            r'telegram\.me/[a-zA-Z0-9_]+',
            r'@[a-zA-Z0-9_]+bot'
        ]
        
        link_count = 0
        for pattern in link_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            link_count += len(matches)
        
        return link_count
    
    async def check_user_bio_links(self, user) -> Optional[str]:
        """Check user bio for suspicious links"""
        try:
            if not user.username and not user.first_name:
                return None
            
            # Check username for suspicious patterns
            if user.username:
                suspicious_patterns = ['bot', 'admin', 'official', 'support', 'help']
                for pattern in suspicious_patterns:
                    if pattern in user.username.lower():
                        return f"Suspicious username: {user.username}"
            
            # Note: Telegram API doesn't expose user bio directly
            # This would require additional API calls or user interaction
            
        except Exception as e:
            logger.error(f"Error checking user bio: {e}")
        
        return None
    
    async def handle_violations(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              user_id: str, chat_id: str, violations: List[str]):
        """Handle user violations"""
        try:
            user = update.effective_user
            message = update.effective_message
            
            # Delete the offending message
            if self.admin_settings.get("delete_spam_messages", True):
                try:
                    await message.delete()
                except Exception as e:
                    logger.error(f"Could not delete message: {e}")
            
            # Add warning
            if user_id not in self.user_warnings:
                self.user_warnings[user_id] = {
                    "warnings": 0,
                    "violations": [],
                    "last_warning": None
                }
            
            self.user_warnings[user_id]["warnings"] += 1
            self.user_warnings[user_id]["violations"].extend(violations)
            self.user_warnings[user_id]["last_warning"] = datetime.now().isoformat()
            
            warning_count = self.user_warnings[user_id]["warnings"]
            max_warnings = self.admin_settings.get("max_warnings", 3)
            
            # Send warning or take action
            if warning_count >= max_warnings:
                # Auto-ban after max warnings
                await self.ban_user(update, context, user_id, f"Exceeded {max_warnings} warnings")
                
                # Notify in group
                warning_msg = f"🚫 User {user.first_name} has been banned for repeated violations:\n"
                for violation in violations:
                    warning_msg += f"• {violation}\n"
                
            elif self.admin_settings.get("warn_before_ban", True):
                # Send warning
                warning_msg = f"⚠️ Warning {warning_count}/{max_warnings} for {user.first_name}:\n"
                for violation in violations:
                    warning_msg += f"• {violation}\n"
                warning_msg += f"\nNext violation will result in a ban."
                
                # Mute for short period
                await self.mute_user(update, context, user_id, 300, "Violation warning")
            
            # Send notification to group
            try:
                await context.bot.send_message(chat_id=chat_id, text=warning_msg)
            except Exception as e:
                logger.error(f"Could not send warning message: {e}")
            
            self.save_user_warnings()
            
            # Log violation
            if self.admin_settings.get("log_violations", True):
                self.log_violation(user_id, chat_id, violations)
            
        except Exception as e:
            logger.error(f"Error handling violations: {e}")
    
    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       user_id: str, reason: str) -> bool:
        """Ban user from group"""
        try:
            chat_id = update.effective_chat.id
            
            # Ban user
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=int(user_id))
            
            # Record ban
            if user_id not in self.banned_users:
                self.banned_users[user_id] = {}
            
            self.banned_users[user_id][str(chat_id)] = {
                "banned_at": datetime.now().isoformat(),
                "reason": reason,
                "banned_by": "auto_moderation"
            }
            
            self.save_banned_users()
            
            logger.info(f"Banned user {user_id} from chat {chat_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False
    
    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                        user_id: str, duration: int, reason: str) -> bool:
        """Mute user for specified duration"""
        try:
            chat_id = update.effective_chat.id
            until_date = datetime.now() + timedelta(seconds=duration)
            
            # Restrict user permissions
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=int(user_id),
                permissions=context.bot.get_chat_permissions(chat_id),
                until_date=until_date
            )
            
            # Record mute
            if user_id not in self.muted_users:
                self.muted_users[user_id] = {}
            
            self.muted_users[user_id][str(chat_id)] = {
                "muted_at": datetime.now().isoformat(),
                "until": until_date.isoformat(),
                "reason": reason,
                "duration": duration
            }
            
            self.save_muted_users()
            
            logger.info(f"Muted user {user_id} in chat {chat_id} for {duration}s: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error muting user: {e}")
            return False
    
    def is_user_banned(self, user_id: str, chat_id: str) -> bool:
        """Check if user is banned"""
        return (user_id in self.banned_users and 
                chat_id in self.banned_users[user_id])
    
    def is_user_muted(self, user_id: str, chat_id: str) -> bool:
        """Check if user is currently muted"""
        if user_id not in self.muted_users or chat_id not in self.muted_users[user_id]:
            return False
        
        mute_data = self.muted_users[user_id][chat_id]
        until_time = datetime.fromisoformat(mute_data["until"])
        
        if datetime.now() > until_time:
            # Mute expired, remove it
            del self.muted_users[user_id][chat_id]
            if not self.muted_users[user_id]:
                del self.muted_users[user_id]
            self.save_muted_users()
            return False
        
        return True
    
    def add_banned_word(self, word: str) -> bool:
        """Add word to banned list"""
        try:
            self.banned_words.add(word.lower())
            self.save_banned_words()
            return True
        except Exception as e:
            logger.error(f"Error adding banned word: {e}")
            return False
    
    def remove_banned_word(self, word: str) -> bool:
        """Remove word from banned list"""
        try:
            self.banned_words.discard(word.lower())
            self.save_banned_words()
            return True
        except Exception as e:
            logger.error(f"Error removing banned word: {e}")
            return False
    
    async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                         user_id: str) -> bool:
        """Unban user from group"""
        try:
            chat_id = str(update.effective_chat.id)
            
            # Unban user
            await context.bot.unban_chat_member(chat_id=int(chat_id), user_id=int(user_id))
            
            # Remove from banned list
            if user_id in self.banned_users and chat_id in self.banned_users[user_id]:
                del self.banned_users[user_id][chat_id]
                if not self.banned_users[user_id]:
                    del self.banned_users[user_id]
                self.save_banned_users()
            
            logger.info(f"Unbanned user {user_id} from chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False
    
    async def unmute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          user_id: str) -> bool:
        """Unmute user"""
        try:
            chat_id = str(update.effective_chat.id)
            
            # Restore full permissions
            await context.bot.restrict_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id),
                permissions=context.bot.get_chat_permissions(int(chat_id))
            )
            
            # Remove from muted list
            if user_id in self.muted_users and chat_id in self.muted_users[user_id]:
                del self.muted_users[user_id][chat_id]
                if not self.muted_users[user_id]:
                    del self.muted_users[user_id]
                self.save_muted_users()
            
            logger.info(f"Unmuted user {user_id} in chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unmuting user: {e}")
            return False
    
    def log_violation(self, user_id: str, chat_id: str, violations: List[str]):
        """Log violation to file"""
        try:
            violation_log = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "chat_id": chat_id,
                "violations": violations
            }
            
            with open("violation_logs.json", 'a', encoding='utf-8') as f:
                f.write(json.dumps(violation_log) + "\n")
                
        except Exception as e:
            logger.error(f"Error logging violation: {e}")
    
    def get_moderation_stats(self, chat_id: str = None) -> str:
        """Get moderation statistics"""
        try:
            stats = "🛡️ **MODERATION STATISTICS**\n\n"
            
            # Banned users count
            banned_count = 0
            if chat_id:
                banned_count = sum(1 for user_data in self.banned_users.values() 
                                 if chat_id in user_data)
            else:
                banned_count = len(self.banned_users)
            
            # Muted users count
            muted_count = 0
            if chat_id:
                muted_count = sum(1 for user_data in self.muted_users.values() 
                                if chat_id in user_data)
            else:
                muted_count = len(self.muted_users)
            
            # Warnings count
            warning_count = sum(user_data.get("warnings", 0) 
                              for user_data in self.user_warnings.values())
            
            stats += f"🚫 **Banned Users**: {banned_count}\n"
            stats += f"🔇 **Muted Users**: {muted_count}\n"
            stats += f"⚠️ **Total Warnings**: {warning_count}\n"
            stats += f"📝 **Banned Words**: {len(self.banned_words)}\n\n"
            
            # Settings status
            stats += f"**Auto-Moderation**: {'✅' if self.admin_settings.get('auto_moderation') else '❌'}\n"
            stats += f"**Link Detection**: {'✅' if self.spam_detection.get('link_detection_enabled') else '❌'}\n"
            stats += f"**Bio Link Ban**: {'✅' if self.spam_detection.get('bio_link_ban') else '❌'}\n"
            stats += f"**Max Warnings**: {self.admin_settings.get('max_warnings', 3)}\n"
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting moderation stats: {e}")
            return "❌ Error retrieving moderation statistics."
    
    def get_banned_words_list(self) -> str:
        """Get formatted banned words list"""
        if not self.banned_words:
            return "📝 No banned words configured.\n\nUse `/add_banned_word <word>` to add words."
        
        words_list = "📝 **BANNED WORDS LIST**\n\n"
        words_list += f"**Total**: {len(self.banned_words)} words\n\n"
        
        # Group words by first letter
        sorted_words = sorted(self.banned_words)
        for i, word in enumerate(sorted_words[:20], 1):  # Show first 20
            words_list += f"{i}. {word}\n"
        
        if len(self.banned_words) > 20:
            words_list += f"\n... and {len(self.banned_words) - 20} more words"
        
        return words_list

# Global instance
admin_controls = None