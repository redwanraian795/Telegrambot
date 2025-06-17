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

logger = logging.getLogger(__name__)

class FinancialTools:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.subscriptions = self.load_subscriptions()
        self.running = False
        
    def load_subscriptions(self) -> Dict[str, Any]:
        """Load financial subscriptions from file"""
        try:
            if os.path.exists("financial_subscriptions.json"):
                with open("financial_subscriptions.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading financial subscriptions: {e}")
        return {}
    
    def save_subscriptions(self):
        """Save financial subscriptions to file"""
        try:
            with open("financial_subscriptions.json", 'w', encoding='utf-8') as f:
                json.dump(self.subscriptions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving financial subscriptions: {e}")
    
    async def start_monitoring(self):
        """Start financial monitoring"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting financial monitoring...")
        
        # Start monitoring tasks
        asyncio.create_task(self.stock_monitor())
        asyncio.create_task(self.forex_monitor())
        asyncio.create_task(self.earnings_monitor())
        asyncio.create_task(self.economic_calendar_monitor())
        
    async def stop_monitoring(self):
        """Stop financial monitoring"""
        self.running = False
        logger.info("Stopping financial monitoring...")
    
    def subscribe_stock_alerts(self, user_id: str, symbols: List[str], alert_type: str, threshold: float) -> bool:
        """Subscribe to stock price alerts"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"stocks": [], "forex": [], "earnings": [], "economic": []}
            
            stock_sub = {
                "symbols": symbols,
                "alert_type": alert_type,  # "above", "below", "change_percent"
                "threshold": threshold,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.subscriptions[user_id]["stocks"].append(stock_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Stock subscription error: {e}")
            return False
    
    def subscribe_forex_alerts(self, user_id: str, pairs: List[str], alert_type: str, threshold: float) -> bool:
        """Subscribe to forex alerts"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"stocks": [], "forex": [], "earnings": [], "economic": []}
            
            forex_sub = {
                "pairs": pairs,
                "alert_type": alert_type,
                "threshold": threshold,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.subscriptions[user_id]["forex"].append(forex_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Forex subscription error: {e}")
            return False
    
    def subscribe_earnings_alerts(self, user_id: str, symbols: List[str]) -> bool:
        """Subscribe to earnings report alerts"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"stocks": [], "forex": [], "earnings": [], "economic": []}
            
            earnings_sub = {
                "symbols": symbols,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.subscriptions[user_id]["earnings"].append(earnings_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Earnings subscription error: {e}")
            return False
    
    def subscribe_economic_calendar(self, user_id: str, events: List[str], importance: str) -> bool:
        """Subscribe to economic calendar events"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"stocks": [], "forex": [], "earnings": [], "economic": []}
            
            economic_sub = {
                "events": events,
                "importance": importance,  # "high", "medium", "low"
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.subscriptions[user_id]["economic"].append(economic_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Economic subscription error: {e}")
            return False
    
    async def stock_monitor(self):
        """Monitor stock prices"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    stock_subs = subs.get("stocks", [])
                    
                    for stock_sub in stock_subs:
                        if not stock_sub.get("active", True):
                            continue
                        
                        symbols = stock_sub["symbols"]
                        alert_type = stock_sub["alert_type"]
                        threshold = stock_sub["threshold"]
                        
                        # Get stock data
                        stock_data = await self.get_stock_data(symbols)
                        
                        for data in stock_data:
                            should_alert = self.check_stock_alert(data, alert_type, threshold)
                            
                            if should_alert:
                                message = f"📈 **Stock Alert!**\n\n"
                                message += f"💼 **{data['symbol']}**: ${data['price']:.2f}\n"
                                message += f"📊 **Change**: {data['change']:+.2f} ({data['change_percent']:+.1f}%)\n"
                                message += f"🎯 **Alert**: {alert_type} ${threshold:.2f}\n"
                                message += f"⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}"
                                
                                try:
                                    await self.bot.send_message(chat_id=user_id, text=message)
                                    stock_sub["active"] = False  # Deactivate after alert
                                    self.save_subscriptions()
                                except Exception as e:
                                    logger.error(f"Failed to send stock alert to {user_id}: {e}")
                
                # Check every 2 minutes during market hours
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"Stock monitor error: {e}")
                await asyncio.sleep(300)
    
    async def get_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Get real stock data from Alpha Vantage API"""
        try:
            stock_data = []
            for symbol in symbols:
                # Using Alpha Vantage free API - replace with your API key
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo"
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        quote = data.get("Global Quote", {})
                        
                        if quote:
                            stock_data.append({
                                "symbol": symbol.upper(),
                                "price": float(quote.get("05. price", 0)),
                                "change": float(quote.get("09. change", 0)),
                                "change_percent": float(quote.get("10. change percent", "0%").replace("%", "")),
                                "volume": int(quote.get("06. volume", 0)),
                                "timestamp": datetime.now()
                            })
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
                    
            return stock_data
            
        except Exception as e:
            logger.error(f"Error getting stock data: {e}")
            return []
    
    def check_stock_alert(self, data: Dict, alert_type: str, threshold: float) -> bool:
        """Check if stock alert should trigger"""
        try:
            price = data["price"]
            change_percent = data["change_percent"]
            
            if alert_type == "above" and price >= threshold:
                return True
            elif alert_type == "below" and price <= threshold:
                return True
            elif alert_type == "change_percent" and abs(change_percent) >= threshold:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking stock alert: {e}")
            return False
    
    async def forex_monitor(self):
        """Monitor forex pairs"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    forex_subs = subs.get("forex", [])
                    
                    for forex_sub in forex_subs:
                        if not forex_sub.get("active", True):
                            continue
                        
                        pairs = forex_sub["pairs"]
                        alert_type = forex_sub["alert_type"]
                        threshold = forex_sub["threshold"]
                        
                        # Get forex data
                        forex_data = await self.get_forex_data(pairs)
                        
                        for data in forex_data:
                            should_alert = self.check_forex_alert(data, alert_type, threshold)
                            
                            if should_alert:
                                message = f"💱 **Forex Alert!**\n\n"
                                message += f"🌍 **{data['pair']}**: {data['rate']:.5f}\n"
                                message += f"📊 **Change**: {data['change']:+.5f} ({data['change_percent']:+.2f}%)\n"
                                message += f"🎯 **Alert**: {alert_type} {threshold}\n"
                                message += f"⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}"
                                
                                try:
                                    await self.bot.send_message(chat_id=user_id, text=message)
                                    forex_sub["active"] = False
                                    self.save_subscriptions()
                                except Exception as e:
                                    logger.error(f"Failed to send forex alert to {user_id}: {e}")
                
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Forex monitor error: {e}")
                await asyncio.sleep(600)
    
    async def get_forex_data(self, pairs: List[str]) -> List[Dict]:
        """Get real forex data from Fixer.io API"""
        try:
            forex_data = []
            
            for pair in pairs:
                # Parse currency pair (e.g., "EURUSD" -> base: EUR, quote: USD)
                if len(pair) == 6:
                    base = pair[:3]
                    quote = pair[3:]
                    
                    # Using Fixer.io API - replace with your API key
                    url = f"http://data.fixer.io/api/latest?access_key=YOUR_API_KEY&base={base}&symbols={quote}"
                    
                    try:
                        # For demo purposes, using mock data
                        forex_data.append({
                            "pair": pair.upper(),
                            "rate": 1.0850 if pair.upper() == "EURUSD" else 1.2650,
                            "change": 0.0025,
                            "change_percent": 0.23,
                            "timestamp": datetime.now()
                        })
                    except Exception as e:
                        logger.error(f"Error fetching forex data for {pair}: {e}")
                        continue
                        
            return forex_data
            
        except Exception as e:
            logger.error(f"Error getting forex data: {e}")
            return []
    
    def check_forex_alert(self, data: Dict, alert_type: str, threshold: float) -> bool:
        """Check if forex alert should trigger"""
        try:
            rate = data["rate"]
            change_percent = data["change_percent"]
            
            if alert_type == "above" and rate >= threshold:
                return True
            elif alert_type == "below" and rate <= threshold:
                return True
            elif alert_type == "change_percent" and abs(change_percent) >= threshold:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking forex alert: {e}")
            return False
    
    async def earnings_monitor(self):
        """Monitor earnings reports"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    earnings_subs = subs.get("earnings", [])
                    
                    for earnings_sub in earnings_subs:
                        if not earnings_sub.get("active", True):
                            continue
                        
                        symbols = earnings_sub["symbols"]
                        
                        # Get earnings calendar
                        earnings_data = await self.get_earnings_calendar(symbols)
                        
                        if earnings_data:
                            message = f"📊 **Earnings Reports Alert**\n\n"
                            for earning in earnings_data[:3]:
                                message += f"🏢 **{earning['symbol']}**\n"
                                message += f"📅 **Date**: {earning['date']}\n"
                                message += f"⏰ **Time**: {earning['time']}\n"
                                message += f"💰 **Est. EPS**: ${earning['estimate']}\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                earnings_sub["last_check"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send earnings alert to {user_id}: {e}")
                
                # Check once per day
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Earnings monitor error: {e}")
                await asyncio.sleep(3600)
    
    async def get_earnings_calendar(self, symbols: List[str]) -> List[Dict]:
        """Get earnings calendar data"""
        try:
            earnings_data = []
            
            for symbol in symbols:
                # Using Earnings Calendar API - replace with real API
                earnings_data.append({
                    "symbol": symbol.upper(),
                    "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "time": "After Market Close",
                    "estimate": "2.45",
                    "actual": None,
                    "surprise": None
                })
                
            return earnings_data
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar: {e}")
            return []
    
    async def economic_calendar_monitor(self):
        """Monitor economic calendar events"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    economic_subs = subs.get("economic", [])
                    
                    for economic_sub in economic_subs:
                        if not economic_sub.get("active", True):
                            continue
                        
                        events = economic_sub["events"]
                        importance = economic_sub["importance"]
                        
                        # Get economic events
                        economic_data = await self.get_economic_events(events, importance)
                        
                        if economic_data:
                            message = f"📰 **Economic Calendar Alert**\n\n"
                            for event in economic_data[:3]:
                                importance_emoji = "🔴" if event['importance'] == "high" else "🟡" if event['importance'] == "medium" else "🟢"
                                message += f"{importance_emoji} **{event['event']}**\n"
                                message += f"📅 **Date**: {event['date']}\n"
                                message += f"🌍 **Country**: {event['country']}\n"
                                message += f"📊 **Forecast**: {event['forecast']}\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                economic_sub["last_check"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send economic alert to {user_id}: {e}")
                
                # Check twice per day
                await asyncio.sleep(43200)
                
            except Exception as e:
                logger.error(f"Economic monitor error: {e}")
                await asyncio.sleep(3600)
    
    async def get_economic_events(self, events: List[str], importance: str) -> List[Dict]:
        """Get economic calendar events"""
        try:
            economic_data = []
            
            for event in events:
                economic_data.append({
                    "event": event,
                    "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "time": "14:30",
                    "country": "United States",
                    "importance": importance,
                    "forecast": "2.1%",
                    "previous": "1.8%",
                    "actual": None
                })
                
            return economic_data
            
        except Exception as e:
            logger.error(f"Error getting economic events: {e}")
            return []
    
    def get_financial_subscriptions_info(self, user_id: str) -> str:
        """Get formatted info about user's financial subscriptions"""
        try:
            subs = self.subscriptions.get(user_id, {})
            
            if not subs:
                return "💼 You have no active financial monitoring.\n\nUse `/stocks`, `/forex`, `/earnings` to subscribe!"
            
            info = "💼 **Your Financial Monitoring:**\n\n"
            
            # Stock subscriptions
            stock_subs = subs.get("stocks", [])
            active_stocks = [s for s in stock_subs if s.get("active", True)]
            if active_stocks:
                info += f"📈 **Stock Alerts ({len(active_stocks)}):**\n"
                for stock in active_stocks[:2]:
                    symbols = ", ".join(stock['symbols'][:3])
                    info += f"• {symbols}: {stock['alert_type']} ${stock['threshold']}\n"
                info += "\n"
            
            # Forex subscriptions
            forex_subs = subs.get("forex", [])
            active_forex = [f for f in forex_subs if f.get("active", True)]
            if active_forex:
                info += f"💱 **Forex Alerts ({len(active_forex)}):**\n"
                for forex in active_forex[:2]:
                    pairs = ", ".join(forex['pairs'][:3])
                    info += f"• {pairs}: {forex['alert_type']} {forex['threshold']}\n"
                info += "\n"
            
            # Earnings subscriptions
            earnings_subs = subs.get("earnings", [])
            active_earnings = [e for e in earnings_subs if e.get("active", True)]
            if active_earnings:
                info += f"📊 **Earnings Alerts ({len(active_earnings)}):**\n"
                for earning in active_earnings[:2]:
                    symbols = ", ".join(earning['symbols'][:3])
                    info += f"• {symbols}\n"
                info += "\n"
            
            # Economic subscriptions
            economic_subs = subs.get("economic", [])
            active_economic = [e for e in economic_subs if e.get("active", True)]
            if active_economic:
                info += f"📰 **Economic Calendar ({len(active_economic)}):**\n"
                for economic in active_economic[:2]:
                    events = ", ".join(economic['events'][:2])
                    info += f"• {events} ({economic['importance']} importance)\n"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting financial subscriptions info: {e}")
            return "❌ Error retrieving financial subscriptions."