import json
import os
from typing import Dict, List, Set, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserAccessService:
    def __init__(self):
        self.access_data = self.load_access_data()
        self.permission_levels = {
            'basic': ['chat', 'wiki', 'translate', 'download', 'crypto', 'accessibility', 'voice', 'advanced_features'],
            'premium': ['chat', 'wiki', 'translate', 'download', 'crypto', 'accessibility', 'voice', 'advanced_features', 'free_sms'],
            'vip': ['chat', 'wiki', 'translate', 'download', 'crypto', 'accessibility', 'voice', 'advanced_features', 'free_sms', 'premium_tools'],
            'admin': ['all']  # Full access to everything
        }
    
    def load_access_data(self) -> Dict[str, Any]:
        """Load user access data from file"""
        try:
            if os.path.exists('user_access.json'):
                with open('user_access.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading access data: {e}")
        
        return {
            'users': {},  # user_id -> access_level
            'permissions': {},  # user_id -> [list of specific permissions]
            'temporary_access': {},  # user_id -> {feature: expiry_timestamp}
            'access_logs': [],  # Log of access changes
            'settings': {
                'default_level': 'basic',
                'require_approval': True,
                'auto_expire_temp_access': True
            }
        }
    
    def save_access_data(self):
        """Save user access data to file"""
        try:
            with open('user_access.json', 'w', encoding='utf-8') as f:
                json.dump(self.access_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving access data: {e}")
    
    def grant_access(self, user_id: str, access_level: str, granted_by: str) -> bool:
        """Grant access level to a user"""
        if access_level not in self.permission_levels:
            return False
        
        self.access_data['users'][user_id] = access_level
        
        # Log the access change
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'grant_access',
            'user_id': user_id,
            'access_level': access_level,
            'granted_by': granted_by
        }
        self.access_data['access_logs'].append(log_entry)
        
        self.save_access_data()
        return True
    
    def revoke_access(self, user_id: str, revoked_by: str) -> bool:
        """Revoke user access"""
        if user_id in self.access_data['users']:
            del self.access_data['users'][user_id]
        
        if user_id in self.access_data['permissions']:
            del self.access_data['permissions'][user_id]
        
        if user_id in self.access_data['temporary_access']:
            del self.access_data['temporary_access'][user_id]
        
        # Log the access change
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'revoke_access',
            'user_id': user_id,
            'revoked_by': revoked_by
        }
        self.access_data['access_logs'].append(log_entry)
        
        self.save_access_data()
        return True
    
    def grant_temporary_access(self, user_id: str, feature: str, hours: int, granted_by: str) -> bool:
        """Grant temporary access to a specific feature"""
        if user_id not in self.access_data['temporary_access']:
            self.access_data['temporary_access'][user_id] = {}
        
        expiry_time = datetime.now().timestamp() + (hours * 3600)
        self.access_data['temporary_access'][user_id][feature] = expiry_time
        
        # Log the access change
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'grant_temporary_access',
            'user_id': user_id,
            'feature': feature,
            'hours': hours,
            'granted_by': granted_by
        }
        self.access_data['access_logs'].append(log_entry)
        
        self.save_access_data()
        return True
    
    def check_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a feature"""
        # Clean up expired temporary access first
        self.cleanup_expired_access()
        
        # Check if user has permanent access level
        user_level = self.access_data['users'].get(user_id)
        if user_level:
            if user_level == 'admin':
                return True
            
            allowed_features = self.permission_levels.get(user_level, [])
            if feature in allowed_features:
                return True
        
        # Check temporary access
        temp_access = self.access_data['temporary_access'].get(user_id, {})
        if feature in temp_access:
            expiry_time = temp_access[feature]
            if datetime.now().timestamp() < expiry_time:
                return True
        
        # Check specific permissions
        user_permissions = self.access_data['permissions'].get(user_id, [])
        if feature in user_permissions:
            return True
        
        # Default level access
        default_level = self.access_data['settings']['default_level']
        default_features = self.permission_levels.get(default_level, [])
        return feature in default_features
    
    def cleanup_expired_access(self):
        """Remove expired temporary access"""
        current_time = datetime.now().timestamp()
        any_expired = False
        
        for user_id in list(self.access_data['temporary_access'].keys()):
            user_temp_access = self.access_data['temporary_access'][user_id]
            
            # Remove expired features
            expired_features = [
                feature for feature, expiry in user_temp_access.items()
                if current_time >= expiry
            ]
            
            for feature in expired_features:
                del user_temp_access[feature]
                any_expired = True
            
            # Remove user entry if no temporary access left
            if not user_temp_access:
                del self.access_data['temporary_access'][user_id]
        
        if any_expired:
            self.save_access_data()
    
    def get_user_access_info(self, user_id: str) -> str:
        """Get formatted access information for a user"""
        self.cleanup_expired_access()
        
        user_level = self.access_data['users'].get(user_id, 'basic')
        user_permissions = self.access_data['permissions'].get(user_id, [])
        temp_access = self.access_data['temporary_access'].get(user_id, {})
        
        info = f"""👤 **User Access Information**

**Access Level:** {user_level.title()}
**Permanent Features:** {', '.join(self.permission_levels.get(user_level, []))}

**Additional Permissions:** {', '.join(user_permissions) if user_permissions else 'None'}

**Temporary Access:**"""
        
        if temp_access:
            for feature, expiry in temp_access.items():
                expiry_dt = datetime.fromtimestamp(expiry)
                info += f"\n• {feature}: Until {expiry_dt.strftime('%Y-%m-%d %H:%M')}"
        else:
            info += "\n• None"
        
        return info
    
    def get_all_users_access(self) -> str:
        """Get formatted access information for all users"""
        self.cleanup_expired_access()
        
        info = "👥 **All Users Access Summary**\n\n"
        
        if not self.access_data['users']:
            info += "No users with special access levels.\n"
        else:
            for user_id, level in self.access_data['users'].items():
                temp_count = len(self.access_data['temporary_access'].get(user_id, {}))
                perm_count = len(self.access_data['permissions'].get(user_id, []))
                
                info += f"**User {user_id}:**\n"
                info += f"• Level: {level.title()}\n"
                if temp_count > 0:
                    info += f"• Temporary Access: {temp_count} features\n"
                if perm_count > 0:
                    info += f"• Additional Permissions: {perm_count} features\n"
                info += "\n"
        
        info += f"**Default Level:** {self.access_data['settings']['default_level'].title()}\n"
        info += f"**Total Access Logs:** {len(self.access_data['access_logs'])}"
        
        return info
    
    def get_access_commands_help(self) -> str:
        """Get help text for access management commands"""
        return """🔐 **User Access Management Commands**

**Grant Access:**
`/grant_access <user_id> <level>` - Grant permanent access level
`/temp_access <user_id> <feature> <hours>` - Grant temporary access

**Access Levels:**
• `basic` - Chat, Wiki, Translate, Download, Crypto
• `premium` - Basic + Free SMS, Accessibility, Voice
• `vip` - Premium + Advanced Features
• `admin` - Full access to everything

**Examples:**
`/grant_access 123456789 premium` - Grant premium access
`/temp_access 123456789 free_sms 24` - Grant SMS access for 24 hours
`/revoke_access 123456789` - Remove all access
`/check_access 123456789` - Check user's access
`/list_access` - List all user access levels

**Features:**
• Automatic cleanup of expired access
• Access logging for auditing
• Flexible permission system
• Temporary and permanent access"""

# Global instance
user_access_service = UserAccessService()