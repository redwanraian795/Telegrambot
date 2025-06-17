import os
import json
from typing import Dict, Any, List, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        # Twilio credentials
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.phone_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio client if credentials are available
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        
        # SMS logs for tracking
        self.sms_logs = self.load_sms_logs()
        
        # Country codes for validation
        self.country_codes = {
            "US": "+1", "CA": "+1", "GB": "+44", "DE": "+49", "FR": "+33",
            "IT": "+39", "ES": "+34", "AU": "+61", "JP": "+81", "CN": "+86",
            "IN": "+91", "BR": "+55", "RU": "+7", "KR": "+82", "MX": "+52",
            "BD": "+880", "PK": "+92", "ID": "+62", "TR": "+90", "SA": "+966",
            "AE": "+971", "EG": "+20", "ZA": "+27", "NG": "+234", "KE": "+254",
            "GH": "+233", "MA": "+212", "TN": "+216", "DZ": "+213", "LY": "+218",
            "SD": "+249", "ET": "+251", "UG": "+256", "TZ": "+255", "ZW": "+263",
            "ZM": "+260", "MW": "+265", "MZ": "+258", "BW": "+267", "NA": "+264",
            "SZ": "+268", "LS": "+266", "MG": "+261", "MU": "+230", "SC": "+248",
            "RE": "+262", "YT": "+262", "KM": "+269", "DJ": "+253", "SO": "+252",
            "ER": "+291", "CF": "+236", "TD": "+235", "CM": "+237", "GQ": "+240",
            "GA": "+241", "CG": "+242", "CD": "+243", "AO": "+244", "ST": "+239"
        }
    
    def load_sms_logs(self) -> Dict[str, Any]:
        """Load SMS logs from file"""
        try:
            if os.path.exists("sms_logs.json"):
                with open("sms_logs.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading SMS logs: {e}")
        return {
            "sent_messages": [],
            "failed_messages": [],
            "statistics": {
                "total_sent": 0,
                "total_failed": 0,
                "countries_reached": [],
                "monthly_usage": {}
            }
        }
    
    def save_sms_logs(self):
        """Save SMS logs to file"""
        try:
            with open("sms_logs.json", 'w', encoding='utf-8') as f:
                json.dump(self.sms_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving SMS logs: {e}")
    
    def format_phone_number(self, phone: str, country_code: str = None) -> str:
        """Format phone number with country code"""
        # Remove any non-digit characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # If already has country code, return as is
        if phone.startswith('+'):
            return phone
        
        # Add country code if provided
        if country_code:
            if country_code.upper() in self.country_codes:
                return self.country_codes[country_code.upper()] + phone
            elif country_code.startswith('+'):
                return country_code + phone
        
        # Default to US/Canada if no country code
        return "+1" + phone
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone.startswith('+'):
            return False
        
        # Remove + and check if all remaining are digits
        digits = phone[1:].replace(' ', '').replace('-', '')
        if not digits.isdigit():
            return False
        
        # Check reasonable length (6-15 digits for international numbers)
        return 6 <= len(digits) <= 15
    
    async def send_sms(self, phone_number: str, message: str, country_code: str = None) -> Dict[str, Any]:
        """Send SMS to any country"""
        if not self.client:
            return {
                "success": False,
                "error": "Twilio credentials not configured. Please contact admin to set up SMS service.",
                "requires_setup": True
            }
        
        try:
            # Format phone number
            formatted_phone = self.format_phone_number(phone_number, country_code)
            
            # Validate phone number
            if not self.validate_phone_number(formatted_phone):
                return {
                    "success": False,
                    "error": f"Invalid phone number format: {formatted_phone}",
                    "phone": formatted_phone
                }
            
            # Send SMS via Twilio
            sms_message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=formatted_phone
            )
            
            # Log successful message
            log_entry = {
                "timestamp": sms_message.date_created.isoformat() if sms_message.date_created else None,
                "to": formatted_phone,
                "message": message[:100] + "..." if len(message) > 100 else message,
                "sid": sms_message.sid,
                "status": sms_message.status,
                "country_code": country_code,
                "price": sms_message.price if hasattr(sms_message, 'price') else None,
                "currency": sms_message.price_unit if hasattr(sms_message, 'price_unit') else None
            }
            
            self.sms_logs["sent_messages"].append(log_entry)
            self.sms_logs["statistics"]["total_sent"] += 1
            
            # Track country if provided
            if country_code and country_code.upper() not in self.sms_logs["statistics"]["countries_reached"]:
                self.sms_logs["statistics"]["countries_reached"].append(country_code.upper())
            
            self.save_sms_logs()
            
            return {
                "success": True,
                "message_sid": sms_message.sid,
                "status": sms_message.status,
                "to": formatted_phone,
                "country": country_code.upper() if country_code else "Unknown",
                "price": sms_message.price if hasattr(sms_message, 'price') else "Unknown"
            }
        
        except TwilioException as e:
            # Log failed message
            error_log = {
                "timestamp": None,
                "to": formatted_phone if 'formatted_phone' in locals() else phone_number,
                "message": message[:100] + "..." if len(message) > 100 else message,
                "error": str(e),
                "country_code": country_code
            }
            
            self.sms_logs["failed_messages"].append(error_log)
            self.sms_logs["statistics"]["total_failed"] += 1
            self.save_sms_logs()
            
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}",
                "phone": formatted_phone if 'formatted_phone' in locals() else phone_number
            }
        
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "phone": phone_number
            }
    
    async def send_bulk_sms(self, recipients: List[Dict[str, str]], message: str) -> Dict[str, Any]:
        """Send SMS to multiple recipients
        recipients format: [{"phone": "+1234567890", "country": "US", "name": "Optional"}, ...]
        """
        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for recipient in recipients:
            phone = recipient.get("phone", "")
            country = recipient.get("country", "")
            name = recipient.get("name", "Unknown")
            
            result = await self.send_sms(phone, message, country)
            
            if result["success"]:
                results["successful"] += 1
                results["details"].append({
                    "phone": phone,
                    "name": name,
                    "status": "sent",
                    "message_sid": result.get("message_sid")
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "phone": phone,
                    "name": name,
                    "status": "failed",
                    "error": result.get("error")
                })
        
        return results
    
    def get_sms_statistics(self) -> str:
        """Get formatted SMS statistics"""
        stats = self.sms_logs["statistics"]
        
        response = "📊 **SMS Service Statistics**\n\n"
        response += f"📤 Total Messages Sent: {stats['total_sent']}\n"
        response += f"❌ Total Failed: {stats['total_failed']}\n"
        response += f"🌍 Countries Reached: {len(stats['countries_reached'])}\n"
        
        if stats['countries_reached']:
            response += f"📍 Countries: {', '.join(stats['countries_reached'])}\n"
        
        # Recent messages
        if self.sms_logs["sent_messages"]:
            response += "\n📨 **Recent Messages:**\n"
            for msg in self.sms_logs["sent_messages"][-5:]:
                response += f"• To: {msg['to']} | {msg['timestamp'][:10] if msg['timestamp'] else 'Unknown'}\n"
        
        return response
    
    def get_country_codes_list(self) -> str:
        """Get formatted list of supported country codes"""
        response = "🌍 **Supported Country Codes:**\n\n"
        
        # Group by region for better organization
        regions = {
            "North America": ["US", "CA", "MX"],
            "Europe": ["GB", "DE", "FR", "IT", "ES", "RU"],
            "Asia": ["JP", "CN", "IN", "KR", "BD", "PK", "ID"],
            "Middle East": ["SA", "AE", "TR"],
            "Africa": ["EG", "ZA", "NG", "KE", "GH", "MA"],
            "Oceania": ["AU"]
        }
        
        for region, countries in regions.items():
            response += f"**{region}:**\n"
            for country in countries:
                if country in self.country_codes:
                    response += f"• {country}: {self.country_codes[country]}\n"
            response += "\n"
        
        response += "📝 **Usage:** /sms +1234567890 Your message here\n"
        response += "📝 **With Country:** /sms +1234567890 US Your message here"
        
        return response
    
    def is_service_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return bool(self.client and self.phone_number)
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for SMS service"""
        return """🔧 **SMS Service Setup Required**

To enable unlimited SMS messaging to any country, please configure:

1. **TWILIO_ACCOUNT_SID** - Your Twilio Account SID
2. **TWILIO_AUTH_TOKEN** - Your Twilio Auth Token  
3. **TWILIO_PHONE_NUMBER** - Your Twilio phone number (e.g., +1234567890)

📝 **Get Twilio Credentials:**
1. Sign up at https://www.twilio.com
2. Get your Account SID and Auth Token from Console
3. Purchase a phone number for sending SMS
4. Add credits for international messaging

💰 **Pricing:** Twilio charges per SMS sent (typically $0.0075-$0.05 per message depending on country)

Once configured, admin can send unlimited SMS to any country! 🌍"""

# Global SMS service instance
sms_service = SMSService()