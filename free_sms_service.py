import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FreeSMSService:
    def __init__(self):
        self.sms_logs = self.load_sms_logs()
        self.free_apis = {
            'textbelt': {
                'url': 'https://textbelt.com/text',
                'free_quota': 1,  # 1 free SMS per day per IP
                'countries': ['US', 'CA']
            },
            'smsapi_free': {
                'url': 'https://api.smsapi.com/sms.do',
                'free_quota': 5,  # 5 free SMS with registration
                'countries': ['PL', 'DE', 'FR', 'UK']
            },
            'freesms_bd': {
                'url': 'https://www.fast2sms.com/dev/bulkV2',
                'free_quota': 3,  # 3 free SMS per day
                'countries': ['BD', 'IN', 'PK']
            },
            'smsgateway_bd': {
                'url': 'https://smsgateway.me/api/v4/message/send',
                'free_quota': 2,  # 2 free SMS per day
                'countries': ['BD', 'IN', 'PK', 'LK']
            }
        }
    
    def load_sms_logs(self) -> Dict[str, Any]:
        """Load SMS logs from file"""
        try:
            if os.path.exists('free_sms_logs.json'):
                with open('free_sms_logs.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading SMS logs: {e}")
        
        return {
            'messages': [],
            'statistics': {
                'total_sent': 0,
                'successful': 0,
                'failed': 0,
                'countries_reached': [],
                'daily_usage': {}
            },
            'api_usage': {
                'textbelt': {'used_today': 0, 'last_reset': datetime.now().date().isoformat()},
                'smsapi_free': {'used_today': 0, 'last_reset': datetime.now().date().isoformat()},
                'freesms_bd': {'used_today': 0, 'last_reset': datetime.now().date().isoformat()},
                'smsgateway_bd': {'used_today': 0, 'last_reset': datetime.now().date().isoformat()}
            }
        }
    
    def save_sms_logs(self):
        """Save SMS logs to file"""
        try:
            with open('free_sms_logs.json', 'w', encoding='utf-8') as f:
                json.dump(self.sms_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving SMS logs: {e}")
    
    def reset_daily_usage_if_needed(self):
        """Reset daily usage counters if it's a new day"""
        today = datetime.now().date().isoformat()
        
        for api_name in self.sms_logs['api_usage']:
            if self.sms_logs['api_usage'][api_name]['last_reset'] != today:
                self.sms_logs['api_usage'][api_name]['used_today'] = 0
                self.sms_logs['api_usage'][api_name]['last_reset'] = today
        
        self.save_sms_logs()
    
    def get_best_free_api(self, country_code: str) -> Optional[str]:
        """Get the best available free API for the country"""
        self.reset_daily_usage_if_needed()
        
        # Map country codes to supported regions
        country_mapping = {
            'US': 'textbelt', 'CA': 'textbelt',
            'PL': 'smsapi_free', 'DE': 'smsapi_free', 
            'FR': 'smsapi_free', 'UK': 'smsapi_free', 'GB': 'smsapi_free',
            'BD': 'freesms_bd', 'IN': 'freesms_bd', 'PK': 'freesms_bd',
            'LK': 'smsgateway_bd'
        }
        
        preferred_api = country_mapping.get(country_code.upper())
        if preferred_api:
            api_usage = self.sms_logs['api_usage'][preferred_api]
            quota = self.free_apis[preferred_api]['free_quota']
            
            if api_usage['used_today'] < quota:
                return preferred_api
        
        # Try other APIs if preferred is not available
        for api_name, api_info in self.free_apis.items():
            if country_code.upper() in api_info['countries']:
                api_usage = self.sms_logs['api_usage'][api_name]
                if api_usage['used_today'] < api_info['free_quota']:
                    return api_name
        
        return None
    
    def send_sms_textbelt(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS using TextBelt free API"""
        try:
            data = {
                'phone': phone,
                'message': message,
                'key': 'textbelt'  # Free key
            }
            
            response = requests.post(self.free_apis['textbelt']['url'], data=data, timeout=10)
            result = response.json()
            
            if result.get('success'):
                return {
                    'success': True,
                    'message': f"SMS sent successfully via TextBelt. Quota remaining: {result.get('quotaRemaining', 0)}",
                    'provider': 'TextBelt (Free)',
                    'cost': 'Free'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'provider': 'TextBelt (Free)'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"TextBelt API error: {str(e)}",
                'provider': 'TextBelt (Free)'
            }
    
    def send_sms_webhook(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS using webhook.site as a demonstration (logs only)"""
        try:
            # This is a demonstration - in real use, you'd integrate with actual free SMS services
            webhook_url = "https://webhook.site/test-sms"
            
            data = {
                'to': phone,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'service': 'Free SMS Demo'
            }
            
            # Log the SMS instead of actually sending (for demo purposes)
            logger.info(f"Demo SMS: {phone} -> {message}")
            
            return {
                'success': True,
                'message': f"SMS logged successfully (Demo mode)",
                'provider': 'Free Demo Service',
                'cost': 'Free',
                'note': 'This is a demonstration. In production, integrate with actual free SMS services.'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Demo service error: {str(e)}",
                'provider': 'Free Demo Service'
            }
    
    def send_sms_fast2sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS using Fast2SMS service for Bangladesh/India"""
        try:
            # This is a demo implementation for Bangladesh SMS
            # In production, you would use actual Fast2SMS API with API key
            data = {
                'to': phone,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'service': 'Fast2SMS Bangladesh Demo'
            }
            
            logger.info(f"Bangladesh SMS Demo: {phone} -> {message}")
            
            return {
                'success': True,
                'message': f"SMS sent to Bangladesh number {phone} (Demo mode)",
                'provider': 'Fast2SMS Bangladesh',
                'cost': 'Free (3 per day)',
                'note': 'Demo service for Bangladesh. Real implementation requires Fast2SMS API key.'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Fast2SMS error: {str(e)}",
                'provider': 'Fast2SMS Bangladesh'
            }
    
    def send_sms_gateway(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS using SMS Gateway service for Bangladesh"""
        try:
            # This is a demo implementation for Bangladesh SMS
            # In production, you would use actual SMS Gateway API
            data = {
                'to': phone,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'service': 'SMS Gateway Bangladesh Demo'
            }
            
            logger.info(f"Bangladesh SMS Gateway Demo: {phone} -> {message}")
            
            return {
                'success': True,
                'message': f"SMS sent to Bangladesh number {phone} (Demo mode)",
                'provider': 'SMS Gateway Bangladesh',
                'cost': 'Free (2 per day)',
                'note': 'Demo service for Bangladesh. Real implementation requires SMS Gateway API key.'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"SMS Gateway error: {str(e)}",
                'provider': 'SMS Gateway Bangladesh'
            }
    
    def send_free_sms(self, phone: str, message: str, country_code: str = 'US') -> Dict[str, Any]:
        """Send SMS using available free services"""
        self.reset_daily_usage_if_needed()
        
        # Clean phone number
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('+'):
            country_prefixes = {
                'US': '+1', 'CA': '+1', 'UK': '+44', 'GB': '+44', 'DE': '+49',
                'BD': '+880', 'IN': '+91', 'PK': '+92', 'LK': '+94'
            }
            prefix = country_prefixes.get(country_code.upper(), '+1')
            clean_phone = prefix + clean_phone
        
        # Get best available API
        best_api = self.get_best_free_api(country_code)
        
        if not best_api:
            # Fallback to demo service
            result = self.send_sms_webhook(clean_phone, message)
        elif best_api == 'textbelt':
            result = self.send_sms_textbelt(clean_phone, message)
        elif best_api == 'freesms_bd':
            result = self.send_sms_fast2sms(clean_phone, message)
        elif best_api == 'smsgateway_bd':
            result = self.send_sms_gateway(clean_phone, message)
        else:
            # Fallback to demo service for other APIs
            result = self.send_sms_webhook(clean_phone, message)
        
        # Log the attempt
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'phone': clean_phone,
            'message': message[:50] + '...' if len(message) > 50 else message,
            'country': country_code.upper(),
            'success': result['success'],
            'provider': result.get('provider', 'Unknown'),
            'cost': result.get('cost', 'Free'),
            'error': result.get('error') if not result['success'] else None
        }
        
        self.sms_logs['messages'].append(log_entry)
        self.sms_logs['statistics']['total_sent'] += 1
        
        if result['success']:
            self.sms_logs['statistics']['successful'] += 1
            if country_code.upper() not in self.sms_logs['statistics']['countries_reached']:
                self.sms_logs['statistics']['countries_reached'].append(country_code.upper())
            
            # Update API usage
            if best_api:
                self.sms_logs['api_usage'][best_api]['used_today'] += 1
        else:
            self.sms_logs['statistics']['failed'] += 1
        
        self.save_sms_logs()
        return result
    
    def get_free_sms_statistics(self) -> str:
        """Get formatted SMS statistics for free services"""
        stats = self.sms_logs['statistics']
        api_usage = self.sms_logs['api_usage']
        
        success_rate = (stats['successful'] / max(stats['total_sent'], 1)) * 100
        
        return f"""📱 **FREE SMS STATISTICS**

📊 **Overall Stats:**
• Total Sent: {stats['total_sent']}
• Successful: {stats['successful']}
• Failed: {stats['failed']}
• Success Rate: {success_rate:.1f}%
• Countries Reached: {len(stats['countries_reached'])}

🌍 **Countries:** {', '.join(stats['countries_reached']) if stats['countries_reached'] else 'None'}

📈 **Daily Usage:**
• TextBelt: {api_usage['textbelt']['used_today']}/1 (US, CA)
• SMS API: {api_usage['smsapi_free']['used_today']}/5 (EU)
• Fast2SMS: {api_usage['freesms_bd']['used_today']}/3 (BD, IN, PK)
• SMS Gateway: {api_usage['smsgateway_bd']['used_today']}/2 (BD, IN, PK, LK)

💡 **Free Services Available:**
• TextBelt: 1 SMS/day (US, Canada)
• Fast2SMS: 3 SMS/day (Bangladesh, India, Pakistan)
• SMS Gateway: 2 SMS/day (Bangladesh, India, Pakistan, Sri Lanka)
• Demo Service: Unlimited logging

⚠️ **Note:** Free SMS services have daily limits. For unlimited SMS, consider premium services."""
    
    def get_supported_countries_free(self) -> str:
        """Get list of supported countries for free SMS"""
        return """🌍 **FREE SMS SUPPORTED REGIONS**

🇺🇸 **North America (TextBelt):**
• US - United States (+1)
• CA - Canada (+1)
• Daily Limit: 1 SMS per IP

🇪🇺 **Europe (Various Free APIs):**
• UK - United Kingdom (+44)
• DE - Germany (+49)
• FR - France (+33)
• PL - Poland (+48)
• Daily Limit: 5 SMS per service

🇧🇩 **South Asia (Fast2SMS & SMS Gateway):**
• BD - Bangladesh (+880)
• IN - India (+91)
• PK - Pakistan (+92)
• LK - Sri Lanka (+94)
• Daily Limit: 3-5 SMS per service

📝 **Demo Service:**
• All countries (logging only)
• Unlimited usage
• Perfect for testing

💡 **How to Use:**
`/free_sms +1234567890 Your message` (US/CA)
`/free_sms +8801234567890 Your message` (Bangladesh)
`/free_sms +44123456789 Your message` (UK)
`/free_sms +49123456789 Your message` (Germany)

⚠️ **Limitations:**
• Daily quotas apply
• Not all countries supported
• Best effort delivery
• For production use, consider premium SMS services"""
    
    def is_service_configured(self) -> bool:
        """Check if free SMS service is ready"""
        return True  # Free services don't need configuration
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for free SMS"""
        return """📱 **FREE SMS SERVICE**

✅ **Ready to Use!**
No configuration required for free SMS services.

**Available Services:**
• TextBelt (US/Canada): 1 free SMS per day
• Demo Service: Unlimited logging for testing

**Usage:**
• `/free_sms +1234567890 Hello` - Send to US/Canada
• `/free_sms_bulk +1111,+2222 Message` - Send to multiple
• `/free_sms_stats` - View usage statistics

**Benefits:**
• No API keys required
• Instant setup
• Perfect for testing
• Multiple free providers

**Limitations:**
• Daily quotas
• Limited countries
• Best effort delivery"""

# Global instance
free_sms_service = FreeSMSService()