import json
import os
from typing import Dict, Any, List
from datetime import datetime

class GroupSettingsService:
    def __init__(self):
        self.settings_file = "group_settings.json"
        self.group_settings = self.load_group_settings()
        
        # Default settings for new groups
        self.default_settings = {
            'auto_responses': True,           # AI responds to all messages
            'media_downloads': True,          # Bot can download media
            'translation': True,              # Translation services
            'crypto_updates': False,          # Cryptocurrency price updates
            'accessibility_features': True,   # Text-to-speech and accessibility
            'voice_transcription': True,     # Voice message transcription
            'spam_protection': False,         # Auto spam detection and removal
            'word_filtering': False,          # Banned words filtering
            'new_member_screening': False,    # Screen new members
            'auto_moderation': False,         # Automatic banning/muting
            'activity_logging': True,         # Log group activity (always on for admin)
            'welcome_messages': False,        # Welcome new members
            'admin_notifications': True      # Notify admin of group activity
        }
    
    def load_group_settings(self) -> Dict[str, Any]:
        """Load group settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading group settings: {e}")
            return {}
    
    def save_group_settings(self):
        """Save group settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.group_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving group settings: {e}")
    
    def get_group_settings(self, chat_id: str) -> Dict[str, Any]:
        """Get settings for a specific group"""
        if chat_id not in self.group_settings:
            self.group_settings[chat_id] = self.default_settings.copy()
            self.group_settings[chat_id]['created_at'] = datetime.now().isoformat()
            self.save_group_settings()
        
        return self.group_settings[chat_id]
    
    def update_group_setting(self, chat_id: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a group"""
        try:
            if chat_id not in self.group_settings:
                self.group_settings[chat_id] = self.default_settings.copy()
            
            if setting in self.default_settings:
                self.group_settings[chat_id][setting] = value
                self.group_settings[chat_id]['updated_at'] = datetime.now().isoformat()
                self.save_group_settings()
                return True
            return False
        except Exception as e:
            print(f"Error updating group setting: {e}")
            return False
    
    def is_feature_enabled(self, chat_id: str, feature: str) -> bool:
        """Check if a feature is enabled for a group"""
        settings = self.get_group_settings(chat_id)
        return settings.get(feature, False)
    
    def get_settings_menu(self, chat_id: str) -> str:
        """Get formatted settings menu for a group"""
        settings = self.get_group_settings(chat_id)
        
        menu = "🔧 **Group Settings**\n\n"
        menu += "**Available Features:**\n"
        
        feature_descriptions = {
            'auto_responses': '🤖 AI Auto-Responses',
            'media_downloads': '📥 Media Downloads', 
            'translation': '🌍 Language Translation',
            'crypto_updates': '💰 Crypto Price Updates',
            'accessibility_features': '♿ Accessibility Support',
            'voice_transcription': '🎤 Voice Transcription',
            'spam_protection': '🛡️ Spam Protection',
            'word_filtering': '🚫 Word Filtering',
            'new_member_screening': '👥 New Member Screening',
            'auto_moderation': '⚖️ Auto Moderation',
            'welcome_messages': '👋 Welcome Messages'
        }
        
        for feature, description in feature_descriptions.items():
            status = "✅ ON" if settings.get(feature, False) else "❌ OFF"
            menu += f"{description}: {status}\n"
        
        menu += f"\n📊 Activity Logging: ✅ ALWAYS ON\n"
        menu += f"📱 Admin Notifications: {'✅ ON' if settings.get('admin_notifications', True) else '❌ OFF'}\n"
        
        menu += "\n**Usage:**\n"
        menu += "`/settings <feature> on` - Enable feature\n"
        menu += "`/settings <feature> off` - Disable feature\n"
        menu += "`/settings list` - Show this menu\n"
        
        return menu
    
    def get_available_features(self) -> List[str]:
        """Get list of available features"""
        return list(self.default_settings.keys())
    
    def get_feature_description(self, feature: str) -> str:
        """Get description of a specific feature"""
        descriptions = {
            'auto_responses': 'AI automatically responds to messages in the group',
            'media_downloads': 'Bot can download and process media files shared in group',
            'translation': 'Automatic language translation services',
            'crypto_updates': 'Real-time cryptocurrency price updates and alerts',
            'accessibility_features': 'Text-to-speech and accessibility support for members',
            'voice_transcription': 'Automatic transcription of voice messages',
            'spam_protection': 'Automatic detection and removal of spam messages',
            'word_filtering': 'Filter and remove messages containing banned words',
            'new_member_screening': 'Screen new members for suspicious activity',
            'auto_moderation': 'Automatic muting/banning of rule violators',
            'activity_logging': 'Log all group activity (always enabled for admin monitoring)',
            'welcome_messages': 'Send welcome messages to new group members',
            'admin_notifications': 'Send notifications to admin about group activity'
        }
        
        return descriptions.get(feature, 'Unknown feature')
    
    def get_group_stats(self, chat_id: str) -> Dict[str, Any]:
        """Get group statistics"""
        settings = self.get_group_settings(chat_id)
        
        enabled_features = sum(1 for feature, enabled in settings.items() 
                             if isinstance(enabled, bool) and enabled)
        
        return {
            'total_features': len(self.default_settings),
            'enabled_features': enabled_features,
            'created_at': settings.get('created_at', 'Unknown'),
            'updated_at': settings.get('updated_at', 'Never')
        }

# Global instance
group_settings_service = GroupSettingsService()