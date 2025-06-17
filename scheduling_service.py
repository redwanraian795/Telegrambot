import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import pytz
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

class SchedulingService:
    def __init__(self):
        self.reminders_file = "user_reminders.json"
        self.user_timezones_file = "user_timezones.json"
        self.reminders = self.load_reminders()
        self.user_timezones = self.load_timezones()
        self.active_reminders = {}
    
    def load_reminders(self) -> Dict[str, List[Dict]]:
        """Load reminders from file"""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
        return {}
    
    def save_reminders(self):
        """Save reminders to file"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving reminders: {e}")
    
    def load_timezones(self) -> Dict[str, str]:
        """Load user timezones from file"""
        try:
            if os.path.exists(self.user_timezones_file):
                with open(self.user_timezones_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading timezones: {e}")
        return {}
    
    def save_timezones(self):
        """Save user timezones to file"""
        try:
            with open(self.user_timezones_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_timezones, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving timezones: {e}")
    
    def set_user_timezone(self, user_id: str, timezone: str) -> bool:
        """Set user's timezone"""
        try:
            # Validate timezone
            pytz.timezone(timezone)
            self.user_timezones[user_id] = timezone
            self.save_timezones()
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False
    
    def get_user_timezone(self, user_id: str) -> str:
        """Get user's timezone or default to UTC"""
        return self.user_timezones.get(user_id, 'UTC')
    
    def parse_time_input(self, time_str: str, user_id: str) -> Optional[datetime]:
        """Parse various time formats"""
        user_tz = pytz.timezone(self.get_user_timezone(user_id))
        now = datetime.now(user_tz)
        
        try:
            # Handle relative times
            if 'minute' in time_str.lower():
                minutes = int([x for x in time_str.split() if x.isdigit()][0])
                return now + timedelta(minutes=minutes)
            elif 'hour' in time_str.lower():
                hours = int([x for x in time_str.split() if x.isdigit()][0])
                return now + timedelta(hours=hours)
            elif 'day' in time_str.lower():
                days = int([x for x in time_str.split() if x.isdigit()][0])
                return now + timedelta(days=days)
            elif 'tomorrow' in time_str.lower():
                tomorrow = now + timedelta(days=1)
                if ':' in time_str:
                    time_part = time_str.split()[-1]
                    hour, minute = map(int, time_part.split(':'))
                    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                # Try to parse absolute time
                parsed_time = parser.parse(time_str)
                if parsed_time.tzinfo is None:
                    parsed_time = user_tz.localize(parsed_time)
                return parsed_time
        except Exception as e:
            logger.error(f"Time parsing error: {e}")
            return None
    
    def create_reminder(self, user_id: str, time_str: str, message: str) -> Dict[str, Any]:
        """Create a new reminder"""
        reminder_time = self.parse_time_input(time_str, user_id)
        
        if not reminder_time:
            return {"success": False, "error": "Invalid time format"}
        
        if reminder_time <= datetime.now(pytz.timezone(self.get_user_timezone(user_id))):
            return {"success": False, "error": "Reminder time must be in the future"}
        
        reminder = {
            "id": f"{user_id}_{len(self.reminders.get(user_id, []))}_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "message": message,
            "reminder_time": reminder_time.isoformat(),
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        if user_id not in self.reminders:
            self.reminders[user_id] = []
        
        self.reminders[user_id].append(reminder)
        self.save_reminders()
        
        return {
            "success": True,
            "reminder": reminder,
            "formatted_time": reminder_time.strftime("%Y-%m-%d %H:%M %Z")
        }
    
    def get_user_reminders(self, user_id: str) -> List[Dict]:
        """Get all active reminders for a user"""
        user_reminders = self.reminders.get(user_id, [])
        return [r for r in user_reminders if r.get('active', True)]
    
    def cancel_reminder(self, user_id: str, reminder_id: str) -> bool:
        """Cancel a specific reminder"""
        user_reminders = self.reminders.get(user_id, [])
        for reminder in user_reminders:
            if reminder['id'] == reminder_id:
                reminder['active'] = False
                self.save_reminders()
                return True
        return False
    
    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due"""
        due_reminders = []
        now = datetime.now(pytz.UTC)
        
        for user_id, user_reminders in self.reminders.items():
            for reminder in user_reminders:
                if not reminder.get('active', True):
                    continue
                
                reminder_time = parser.parse(reminder['reminder_time'])
                if reminder_time <= now:
                    due_reminders.append(reminder)
                    reminder['active'] = False  # Mark as sent
        
        if due_reminders:
            self.save_reminders()
        
        return due_reminders
    
    def format_reminders_list(self, user_id: str) -> str:
        """Format user's reminders for display"""
        reminders = self.get_user_reminders(user_id)
        
        if not reminders:
            return "📅 You have no active reminders."
        
        formatted = "📅 **Your Active Reminders:**\n\n"
        user_tz = pytz.timezone(self.get_user_timezone(user_id))
        
        for i, reminder in enumerate(reminders, 1):
            reminder_time = parser.parse(reminder['reminder_time'])
            local_time = reminder_time.astimezone(user_tz)
            
            formatted += f"{i}. **{reminder['message']}**\n"
            formatted += f"   ⏰ {local_time.strftime('%Y-%m-%d %H:%M %Z')}\n"
            formatted += f"   🆔 ID: `{reminder['id']}`\n\n"
        
        formatted += "To cancel a reminder, use: `/cancel_reminder [ID]`"
        return formatted
    
    def get_common_timezones(self) -> str:
        """Get list of common timezones"""
        common_tz = [
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai",
            "Australia/Sydney", "Australia/Melbourne", "Pacific/Auckland"
        ]
        
        formatted = "🌍 **Common Timezones:**\n\n"
        for tz in common_tz:
            try:
                timezone = pytz.timezone(tz)
                now = datetime.now(timezone)
                formatted += f"• `{tz}` - {now.strftime('%H:%M %Z')}\n"
            except:
                continue
        
        formatted += "\nUse `/timezone [timezone]` to set your timezone"
        return formatted