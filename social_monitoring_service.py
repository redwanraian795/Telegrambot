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

class SocialMonitoringService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.subscriptions = self.load_subscriptions()
        self.running = False
        
    def load_subscriptions(self) -> Dict[str, Any]:
        """Load social media subscriptions from file"""
        try:
            if os.path.exists("social_subscriptions.json"):
                with open("social_subscriptions.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading social subscriptions: {e}")
        return {}
    
    def save_subscriptions(self):
        """Save social media subscriptions to file"""
        try:
            with open("social_subscriptions.json", 'w', encoding='utf-8') as f:
                json.dump(self.subscriptions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving social subscriptions: {e}")
    
    async def start_monitoring(self):
        """Start social media monitoring"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting social media monitoring...")
        
        # Start monitoring tasks
        asyncio.create_task(self.twitter_monitor())
        asyncio.create_task(self.reddit_monitor())
        asyncio.create_task(self.telegram_channel_monitor())
        
    async def stop_monitoring(self):
        """Stop social media monitoring"""
        self.running = False
        logger.info("Stopping social media monitoring...")
    
    def subscribe_twitter_mentions(self, user_id: str, keywords: List[str]) -> bool:
        """Subscribe to Twitter mentions monitoring"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"twitter": [], "reddit": [], "telegram": []}
            
            twitter_sub = {
                "keywords": keywords,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "last_check": datetime.now().isoformat()
            }
            
            self.subscriptions[user_id]["twitter"].append(twitter_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Twitter subscription error: {e}")
            return False
    
    def subscribe_reddit_sentiment(self, user_id: str, subreddits: List[str], keywords: List[str]) -> bool:
        """Subscribe to Reddit sentiment analysis"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"twitter": [], "reddit": [], "telegram": []}
            
            reddit_sub = {
                "subreddits": subreddits,
                "keywords": keywords,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "last_check": datetime.now().isoformat()
            }
            
            self.subscriptions[user_id]["reddit"].append(reddit_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Reddit subscription error: {e}")
            return False
    
    def subscribe_telegram_channels(self, user_id: str, channels: List[str]) -> bool:
        """Subscribe to Telegram channel monitoring"""
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {"twitter": [], "reddit": [], "telegram": []}
            
            telegram_sub = {
                "channels": channels,
                "created_at": datetime.now().isoformat(),
                "active": True,
                "last_check": datetime.now().isoformat()
            }
            
            self.subscriptions[user_id]["telegram"].append(telegram_sub)
            self.save_subscriptions()
            return True
            
        except Exception as e:
            logger.error(f"Telegram subscription error: {e}")
            return False
    
    async def twitter_monitor(self):
        """Monitor Twitter mentions"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    twitter_subs = subs.get("twitter", [])
                    
                    for twitter_sub in twitter_subs:
                        if not twitter_sub.get("active", True):
                            continue
                        
                        keywords = twitter_sub["keywords"]
                        
                        # Simulate Twitter API call - replace with real Twitter API
                        mentions = await self.get_twitter_mentions(keywords)
                        
                        if mentions:
                            message = f"🐦 **Twitter Mentions Alert**\n\n"
                            for mention in mentions[:3]:
                                message += f"• @{mention['user']}: {mention['text'][:100]}...\n"
                                message += f"  ❤️ {mention['likes']} | 🔄 {mention['retweets']}\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                twitter_sub["last_check"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send Twitter alert to {user_id}: {e}")
                
                # Check every 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Twitter monitor error: {e}")
                await asyncio.sleep(300)
    
    async def get_twitter_mentions(self, keywords: List[str]) -> List[Dict]:
        """Get Twitter mentions - simulated data"""
        try:
            # Mock Twitter data - replace with real Twitter API integration
            mentions = []
            for keyword in keywords:
                mentions.append({
                    "user": f"crypto_trader_{keyword}",
                    "text": f"Breaking: {keyword.upper()} showing strong bullish signals! Technical analysis suggests potential breakout incoming.",
                    "likes": 156,
                    "retweets": 89,
                    "timestamp": datetime.now(),
                    "url": f"https://twitter.com/user/status/123456789"
                })
            return mentions
            
        except Exception as e:
            logger.error(f"Error getting Twitter mentions: {e}")
            return []
    
    async def reddit_monitor(self):
        """Monitor Reddit sentiment"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    reddit_subs = subs.get("reddit", [])
                    
                    for reddit_sub in reddit_subs:
                        if not reddit_sub.get("active", True):
                            continue
                        
                        subreddits = reddit_sub["subreddits"]
                        keywords = reddit_sub["keywords"]
                        
                        # Get Reddit sentiment
                        sentiment_data = await self.get_reddit_sentiment(subreddits, keywords)
                        
                        if sentiment_data:
                            message = f"📱 **Reddit Sentiment Alert**\n\n"
                            for data in sentiment_data[:3]:
                                sentiment_emoji = "🟢" if data['sentiment'] > 0.6 else "🟡" if data['sentiment'] > 0.4 else "🔴"
                                message += f"{sentiment_emoji} r/{data['subreddit']}: {data['title'][:80]}...\n"
                                message += f"  👍 {data['upvotes']} | 💬 {data['comments']} | Sentiment: {data['sentiment']:.1f}/1.0\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                reddit_sub["last_check"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send Reddit alert to {user_id}: {e}")
                
                # Check every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Reddit monitor error: {e}")
                await asyncio.sleep(600)
    
    async def get_reddit_sentiment(self, subreddits: List[str], keywords: List[str]) -> List[Dict]:
        """Get Reddit sentiment analysis - simulated data"""
        try:
            # Mock Reddit data - replace with real Reddit API integration
            sentiment_data = []
            for subreddit in subreddits:
                for keyword in keywords:
                    sentiment_data.append({
                        "subreddit": subreddit,
                        "title": f"Discussion about {keyword} - massive potential or overhyped?",
                        "upvotes": 245,
                        "comments": 67,
                        "sentiment": 0.75,  # Positive sentiment
                        "url": f"https://reddit.com/r/{subreddit}/comments/abc123",
                        "timestamp": datetime.now()
                    })
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment: {e}")
            return []
    
    async def telegram_channel_monitor(self):
        """Monitor Telegram channels"""
        while self.running:
            try:
                for user_id, subs in self.subscriptions.items():
                    telegram_subs = subs.get("telegram", [])
                    
                    for telegram_sub in telegram_subs:
                        if not telegram_sub.get("active", True):
                            continue
                        
                        channels = telegram_sub["channels"]
                        
                        # Get channel updates
                        updates = await self.get_telegram_channel_updates(channels)
                        
                        if updates:
                            message = f"📢 **Telegram Channel Updates**\n\n"
                            for update in updates[:3]:
                                message += f"📺 **{update['channel']}**\n"
                                message += f"{update['text'][:150]}...\n"
                                message += f"👥 {update['views']} views\n\n"
                            
                            try:
                                await self.bot.send_message(chat_id=user_id, text=message)
                                telegram_sub["last_check"] = datetime.now().isoformat()
                                self.save_subscriptions()
                            except Exception as e:
                                logger.error(f"Failed to send Telegram alert to {user_id}: {e}")
                
                # Check every 20 minutes
                await asyncio.sleep(1200)
                
            except Exception as e:
                logger.error(f"Telegram monitor error: {e}")
                await asyncio.sleep(600)
    
    async def get_telegram_channel_updates(self, channels: List[str]) -> List[Dict]:
        """Get Telegram channel updates - simulated data"""
        try:
            # Mock Telegram data - replace with real channel monitoring
            updates = []
            for channel in channels:
                updates.append({
                    "channel": channel,
                    "text": f"BREAKING: Major announcement from {channel}! New partnership unveiled with significant market implications for crypto investors.",
                    "views": 1250,
                    "timestamp": datetime.now(),
                    "url": f"https://t.me/{channel}/123"
                })
            return updates
            
        except Exception as e:
            logger.error(f"Error getting Telegram updates: {e}")
            return []
    
    def get_social_subscriptions_info(self, user_id: str) -> str:
        """Get formatted info about user's social media subscriptions"""
        try:
            subs = self.subscriptions.get(user_id, {})
            
            if not subs:
                return "📱 You have no active social media monitoring.\n\nUse `/twitter`, `/reddit`, `/channels` to subscribe!"
            
            info = "📱 **Your Social Media Monitoring:**\n\n"
            
            # Twitter subscriptions
            twitter_subs = subs.get("twitter", [])
            active_twitter = [t for t in twitter_subs if t.get("active", True)]
            if active_twitter:
                info += f"🐦 **Twitter Mentions ({len(active_twitter)}):**\n"
                for twitter in active_twitter[:2]:
                    keywords = ", ".join(twitter['keywords'][:3])
                    info += f"• Keywords: {keywords}\n"
                info += "\n"
            
            # Reddit subscriptions
            reddit_subs = subs.get("reddit", [])
            active_reddit = [r for r in reddit_subs if r.get("active", True)]
            if active_reddit:
                info += f"📱 **Reddit Monitoring ({len(active_reddit)}):**\n"
                for reddit in active_reddit[:2]:
                    subreddits = ", ".join(reddit['subreddits'][:3])
                    keywords = ", ".join(reddit['keywords'][:3])
                    info += f"• r/{subreddits}: {keywords}\n"
                info += "\n"
            
            # Telegram subscriptions
            telegram_subs = subs.get("telegram", [])
            active_telegram = [t for t in telegram_subs if t.get("active", True)]
            if active_telegram:
                info += f"📢 **Telegram Channels ({len(active_telegram)}):**\n"
                for telegram in active_telegram[:2]:
                    channels = ", ".join(telegram['channels'][:3])
                    info += f"• Channels: {channels}\n"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting social subscriptions info: {e}")
            return "❌ Error retrieving social media subscriptions."