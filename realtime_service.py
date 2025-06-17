import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import logging
from telegram.ext import ContextTypes
from telegram import Bot
import pytz

logger = logging.getLogger(__name__)

class RealTimeService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_feeds = {}
        self.price_alerts = {}
        self.news_feeds = {}
        self.weather_alerts = {}
        self.user_subscriptions = self.load_subscriptions()
        self.running = False
        
    def load_subscriptions(self) -> Dict[str, Any]:
        """Load user subscriptions from file"""
        try:
            if os.path.exists("realtime_subscriptions.json"):
                with open("realtime_subscriptions.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading subscriptions: {e}")
        return {}
    
    def save_subscriptions(self):
        """Save user subscriptions to file"""
        try:
            with open("realtime_subscriptions.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_subscriptions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving subscriptions: {e}")
    
    async def start_realtime_services(self):
        """Start all real-time services"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting real-time services...")
        
        # Start background tasks
        asyncio.create_task(self.crypto_price_monitor())
        asyncio.create_task(self.news_feed_monitor())
        asyncio.create_task(self.weather_monitor())
        asyncio.create_task(self.reminder_checker())
        asyncio.create_task(self.market_alerts())
        
    async def stop_realtime_services(self):
        """Stop all real-time services"""
        self.running = False
        logger.info("Stopping real-time services...")
    
    def subscribe_price_alert(self, user_id: str, symbol: str, target_price: float, alert_type: str = "above") -> bool:
        """Subscribe to cryptocurrency price alerts"""
        try:
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = {"price_alerts": [], "news": [], "weather": []}
            
            alert = {
                "symbol": symbol.lower(),
                "target_price": target_price,
                "alert_type": alert_type,  # "above" or "below"
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.user_subscriptions[user_id]["price_alerts"].append(alert)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Price alert subscription error: {e}")
            return False
    
    def subscribe_news_feed(self, user_id: str, keywords: List[str], category: str = "general") -> bool:
        """Subscribe to real-time news feeds"""
        try:
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = {"price_alerts": [], "news": [], "weather": []}
            
            news_sub = {
                "keywords": keywords,
                "category": category,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "last_update": datetime.now().isoformat()
            }
            
            self.user_subscriptions[user_id]["news"].append(news_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"News subscription error: {e}")
            return False
    
    def subscribe_weather_alerts(self, user_id: str, location: str, alert_types: List[str]) -> bool:
        """Subscribe to weather alerts"""
        try:
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = {"price_alerts": [], "news": [], "weather": []}
            
            weather_sub = {
                "location": location,
                "alert_types": alert_types,  # ["rain", "storm", "temperature", "wind"]
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.user_subscriptions[user_id]["weather"].append(weather_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Weather subscription error: {e}")
            return False
    
    async def crypto_price_monitor(self):
        """Monitor cryptocurrency prices and send alerts"""
        while self.running:
            try:
                for user_id, subscriptions in self.user_subscriptions.items():
                    price_alerts = subscriptions.get("price_alerts", [])
                    
                    for alert in price_alerts:
                        if not alert.get("active", True):
                            continue
                            
                        symbol = alert["symbol"]
                        target_price = alert["target_price"]
                        alert_type = alert["alert_type"]
                        
                        # Get current price
                        current_price = await self.get_crypto_price(symbol)
                        if current_price is None:
                            continue
                        
                        # Check if alert should trigger
                        should_alert = False
                        if alert_type == "above" and current_price >= target_price:
                            should_alert = True
                        elif alert_type == "below" and current_price <= target_price:
                            should_alert = True
                        
                        if should_alert:
                            # Send alert
                            message = f"🚨 **Price Alert!**\n\n"
                            message += f"💰 **{symbol.upper()}** has reached ${current_price:,.2f}\n"
                            message += f"🎯 **Target:** ${target_price:,.2f} ({alert_type})\n"
                            message += f"⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                # Deactivate alert after sending
                                alert["active"] = False
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send price alert to {user_id}: {e}")
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Crypto price monitor error: {e}")
                await asyncio.sleep(60)
    
    async def get_crypto_price(self, symbol: str) -> Optional[float]:
        """Get current cryptocurrency price"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if symbol in data:
                    return data[symbol]["usd"]
                    
        except Exception as e:
            logger.error(f"Error getting crypto price for {symbol}: {e}")
        
        return None
    
    async def news_feed_monitor(self):
        """Monitor news feeds and send updates"""
        while self.running:
            try:
                for user_id, subscriptions in self.user_subscriptions.items():
                    news_subs = subscriptions.get("news", [])
                    
                    for news_sub in news_subs:
                        if not news_sub.get("active", True):
                            continue
                        
                        keywords = news_sub["keywords"]
                        category = news_sub["category"]
                        last_update = datetime.fromisoformat(news_sub["last_update"])
                        
                        # Check if it's time for update (every 2 hours)
                        if datetime.now() - last_update < timedelta(hours=2):
                            continue
                        
                        # Get news updates
                        news_items = await self.get_news_updates(keywords, category)
                        
                        if news_items:
                            message = f"📰 **News Update - {category.title()}**\n\n"
                            for item in news_items[:3]:  # Limit to 3 items
                                message += f"• **{item['title']}**\n"
                                message += f"  {item['description'][:100]}...\n"
                                message += f"  🔗 {item['url']}\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                news_sub["last_update"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send news update to {user_id}: {e}")
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"News feed monitor error: {e}")
                await asyncio.sleep(1800)
    
    async def get_news_updates(self, keywords: List[str], category: str) -> List[Dict]:
        """Get news updates from RSS feeds or APIs"""
        try:
            # Simulate news fetching - in production, use real news APIs
            news_items = []
            
            for keyword in keywords[:2]:  # Limit keywords
                # Mock news items - replace with real API calls
                news_items.append({
                    "title": f"Breaking: {keyword.title()} News Update",
                    "description": f"Latest developments in {keyword} sector with significant market impact",
                    "url": f"https://news.example.com/{keyword.lower()}-update",
                    "timestamp": datetime.now()
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting news updates: {e}")
            return []
    
    async def weather_monitor(self):
        """Monitor weather conditions and send alerts"""
        while self.running:
            try:
                for user_id, subscriptions in self.user_subscriptions.items():
                    weather_subs = subscriptions.get("weather", [])
                    
                    for weather_sub in weather_subs:
                        if not weather_sub.get("active", True):
                            continue
                        
                        location = weather_sub["location"]
                        alert_types = weather_sub["alert_types"]
                        
                        # Get weather data
                        weather_data = await self.get_weather_data(location)
                        
                        if weather_data:
                            alerts = self.check_weather_alerts(weather_data, alert_types)
                            
                            if alerts:
                                message = f"🌤️ **Weather Alert - {location}**\n\n"
                                for alert in alerts:
                                    message += f"⚠️ {alert}\n"
                                
                                try:
                                    await self.bot.send_message(chat_id=user_id, text=message)
                                except Exception as e:
                                    logger.error(f"Failed to send weather alert to {user_id}: {e}")
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Weather monitor error: {e}")
                await asyncio.sleep(1800)
    
    async def get_weather_data(self, location: str) -> Optional[Dict]:
        """Get current weather data"""
        try:
            # Mock weather data - replace with real weather API
            return {
                "location": location,
                "temperature": 25,
                "condition": "partly_cloudy",
                "humidity": 65,
                "wind_speed": 10,
                "precipitation": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting weather data for {location}: {e}")
            return None
    
    def check_weather_alerts(self, weather_data: Dict, alert_types: List[str]) -> List[str]:
        """Check if weather conditions trigger alerts"""
        alerts = []
        
        try:
            if "rain" in alert_types and weather_data.get("precipitation", 0) > 0:
                alerts.append(f"Rain expected - {weather_data['precipitation']}mm")
            
            if "temperature" in alert_types:
                temp = weather_data.get("temperature", 0)
                if temp > 30:
                    alerts.append(f"High temperature warning - {temp}°C")
                elif temp < 5:
                    alerts.append(f"Low temperature warning - {temp}°C")
            
            if "wind" in alert_types and weather_data.get("wind_speed", 0) > 25:
                alerts.append(f"Strong wind warning - {weather_data['wind_speed']} km/h")
            
        except Exception as e:
            logger.error(f"Weather alert check error: {e}")
        
        return alerts
    
    async def reminder_checker(self):
        """Check and send due reminders"""
        while self.running:
            try:
                # Import here to avoid circular imports
                from scheduling_service import SchedulingService
                scheduling_service = SchedulingService()
                
                due_reminders = scheduling_service.get_due_reminders()
                
                for reminder in due_reminders:
                    user_id = reminder["user_id"]
                    message = f"⏰ **Reminder!**\n\n📝 {reminder['message']}"
                    
                    try:
                        await self.bot.send_message(chat_id=user_id, text=message)
                        logger.info(f"Sent reminder to {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {user_id}: {e}")
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Reminder checker error: {e}")
                await asyncio.sleep(300)
    
    async def market_alerts(self):
        """Send market opening/closing alerts"""
        while self.running:
            try:
                now = datetime.now(pytz.timezone('US/Eastern'))
                current_time = now.strftime('%H:%M')
                
                # Market opening alert (9:30 AM EST)
                if current_time == '09:30':
                    message = "🔔 **US Stock Market is now OPEN!**\n\nTrading has begun for the day. Good luck with your investments!"
                    await self.broadcast_to_subscribers(message, "market_alerts")
                
                # Market closing alert (4:00 PM EST)
                elif current_time == '16:00':
                    message = "🔔 **US Stock Market is now CLOSED!**\n\nTrading has ended for the day. See you tomorrow!"
                    await self.broadcast_to_subscribers(message, "market_alerts")
                
                # Wait 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Market alerts error: {e}")
                await asyncio.sleep(300)
    
    async def broadcast_to_subscribers(self, message: str, alert_type: str):
        """Broadcast message to all subscribers of a specific alert type"""
        try:
            for user_id, subscriptions in self.user_subscriptions.items():
                if alert_type in subscriptions.get("enabled_alerts", []):
                    try:
                        await self.bot.send_message(chat_id=user_id, text=message)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {user_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
    
    def get_user_subscriptions_info(self, user_id: str) -> str:
        """Get formatted info about user's subscriptions"""
        try:
            subs = self.user_subscriptions.get(user_id, {})
            
            if not subs:
                return "📱 You have no active real-time subscriptions.\n\nUse commands like `/alert`, `/newsfeed`, `/weather` to subscribe!"
            
            info = "📱 **Your Real-Time Subscriptions:**\n\n"
            
            # Price alerts
            price_alerts = subs.get("price_alerts", [])
            active_price_alerts = [a for a in price_alerts if a.get("active", True)]
            if active_price_alerts:
                info += f"💰 **Price Alerts ({len(active_price_alerts)}):**\n"
                for alert in active_price_alerts[:3]:
                    info += f"• {alert['symbol'].upper()} {alert['alert_type']} ${alert['target_price']}\n"
                info += "\n"
            
            # News feeds
            news_subs = subs.get("news", [])
            active_news = [n for n in news_subs if n.get("active", True)]
            if active_news:
                info += f"📰 **News Feeds ({len(active_news)}):**\n"
                for news in active_news[:2]:
                    keywords = ", ".join(news['keywords'][:3])
                    info += f"• {news['category'].title()}: {keywords}\n"
                info += "\n"
            
            # Weather alerts
            weather_subs = subs.get("weather", [])
            active_weather = [w for w in weather_subs if w.get("active", True)]
            if active_weather:
                info += f"🌤️ **Weather Alerts ({len(active_weather)}):**\n"
                for weather in active_weather[:2]:
                    alerts = ", ".join(weather['alert_types'])
                    info += f"• {weather['location']}: {alerts}\n"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting subscriptions info: {e}")
            return "❌ Error retrieving subscription information."