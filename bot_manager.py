import os
import logging
import asyncio
import time
import signal
import sys
from datetime import datetime
from telegram.error import Conflict, TimedOut, NetworkError
from telegram.ext import Application

logger = logging.getLogger(__name__)

class BotManager:
    """Manages bot instance lifecycle and ensures 24/7 uptime"""
    
    def __init__(self, application: Application):
        self.application = application
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.last_restart = None
        
    async def ensure_single_instance(self):
        """Ensure only one bot instance is running"""
        try:
            # Clear any existing webhooks that might conflict
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Cleared any existing webhooks")
            
            # Wait a moment to let any other instances shut down
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Error ensuring single instance: {e}")
            return False
    
    async def start_with_recovery(self):
        """Start bot with automatic recovery on failures"""
        while self.restart_count < self.max_restarts:
            try:
                logger.info(f"Starting bot (attempt {self.restart_count + 1}/{self.max_restarts})")
                
                # Ensure we're the only instance
                if not await self.ensure_single_instance():
                    raise Exception("Failed to ensure single instance")
                
                # Start the application
                await self.application.initialize()
                await self.application.start()
                
                logger.info("Bot started successfully - beginning polling")
                self.running = True
                
                # Start polling with conflict handling
                await self._poll_with_recovery()
                
            except Conflict as e:
                self.restart_count += 1
                logger.error(f"Bot conflict detected: {e}")
                await self._handle_restart(conflict=True)
                
            except (TimedOut, NetworkError) as e:
                self.restart_count += 1
                logger.error(f"Network error: {e}")
                await self._handle_restart(network_issue=True)
                
            except Exception as e:
                self.restart_count += 1
                logger.error(f"Unexpected error: {e}")
                await self._handle_restart()
            
            finally:
                if self.running:
                    await self._cleanup()
        
        logger.error(f"Max restart attempts ({self.max_restarts}) reached. Bot stopping.")
    
    async def _poll_with_recovery(self):
        """Poll for updates with automatic recovery"""
        update_id = None
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running and consecutive_errors < max_consecutive_errors:
            try:
                # Get updates with proper timeout handling
                updates = await self.application.bot.get_updates(
                    offset=update_id,
                    timeout=30,
                    allowed_updates=['message', 'callback_query']
                )
                
                # Reset error counter on successful request
                consecutive_errors = 0
                
                # Process updates
                for update in updates:
                    update_id = update.update_id + 1
                    try:
                        await self.application.process_update(update)
                    except Exception as e:
                        logger.error(f"Error processing update {update.update_id}: {e}")
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(0.1)
                
            except Conflict:
                logger.error("Polling conflict - another instance detected")
                raise  # Let the parent handler deal with this
                
            except (TimedOut, NetworkError) as e:
                consecutive_errors += 1
                logger.warning(f"Network issue during polling (error {consecutive_errors}/{max_consecutive_errors}): {e}")
                await asyncio.sleep(min(consecutive_errors * 2, 10))  # Exponential backoff
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Polling error (error {consecutive_errors}/{max_consecutive_errors}): {e}")
                await asyncio.sleep(min(consecutive_errors, 5))
        
        if consecutive_errors >= max_consecutive_errors:
            raise Exception("Too many consecutive polling errors")
    
    async def _handle_restart(self, conflict=False, network_issue=False):
        """Handle bot restart with appropriate delays"""
        self.last_restart = datetime.now()
        
        if conflict:
            delay = 15  # Longer delay for conflicts
            logger.info(f"Waiting {delay} seconds before restart due to conflict...")
        elif network_issue:
            delay = 5   # Shorter delay for network issues
            logger.info(f"Waiting {delay} seconds before restart due to network issue...")
        else:
            delay = 10  # Default delay
            logger.info(f"Waiting {delay} seconds before restart...")
        
        await self._cleanup()
        await asyncio.sleep(delay)
    
    async def _cleanup(self):
        """Clean up bot resources"""
        self.running = False
        try:
            if self.application.running:
                await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)