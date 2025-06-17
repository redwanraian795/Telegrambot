import logging
import asyncio
import os
import threading
import time
import signal
import sys
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand
from telegram.error import Conflict, TimedOut, NetworkError
from bot_handlers import BotHandlers, realtime_service, group_surveillance, admin_controls
from realtime_service import RealTimeService
from group_surveillance_service import GroupSurveillanceService
from admin_controls_service import AdminControlsService
from config import TELEGRAM_TOKEN, COMMANDS
from utils import clean_old_downloads
from keep_alive import start_keep_alive
from multi_keep_alive import start_multi_keep_alive

# Flask app for web interface and external access
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health_check():
    from flask import request
    # Simple admin verification using secret parameter
    admin_secret = request.args.get('admin')
    if admin_secret != "admin_access_2025":
        return "Access denied", 403
    return "Bot is alive!"

@app.route('/status')
def status():
    from flask import request
    # Simple admin verification using secret parameter
    admin_secret = request.args.get('admin')
    if admin_secret != "admin_access_2025":
        return "Access denied", 403
    return "Bot is alive!"

def run_flask():
    """Run Flask server for external access"""
    port = int(os.environ.get('PORT', 8080))
    # Force production-ready configuration for UptimeRobot compatibility
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def set_bot_commands(application):
    """Set bot commands for the menu"""
    commands = []
    for cmd, desc in COMMANDS.items():
        commands.append(BotCommand(cmd, desc))
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again later."
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

def main():
    """Main function to run the bot"""
    logger.info("Starting Telegram Bot...")
    
    # Start Flask server in background thread for external access
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Flask server started for external access")
    
    # Start enhanced keep-alive services for guaranteed 24/7 uptime
    start_keep_alive()
    start_multi_keep_alive()
    logger.info("Enhanced multi-layer keep-alive system started for guaranteed 24/7 uptime")
    
    # Create application with job queue
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Create bot handlers instance
    handlers = BotHandlers()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("chat", handlers.chat_command))
    application.add_handler(CommandHandler("wiki", handlers.wiki_command))
    application.add_handler(CommandHandler("study", handlers.study_command))
    application.add_handler(CommandHandler("download", handlers.download_command))
    application.add_handler(CommandHandler("translate", handlers.translate_command))
    application.add_handler(CommandHandler("accessibility", handlers.accessibility_command))
    application.add_handler(CommandHandler("speak", handlers.speak_command))
    application.add_handler(CommandHandler("broadcast", handlers.broadcast_command))
    application.add_handler(CommandHandler("contact", handlers.contact_command))
    application.add_handler(CommandHandler("stats", handlers.stats_command))
    # SMS services disabled per user request
    # application.add_handler(CommandHandler("sms", handlers.sms_command))
    # application.add_handler(CommandHandler("sms_bulk", handlers.sms_bulk_command))
    # application.add_handler(CommandHandler("sms_stats", handlers.sms_stats_command))
    # application.add_handler(CommandHandler("sms_countries", handlers.sms_countries_command))
    # application.add_handler(CommandHandler("free_sms", handlers.free_sms_command))
    # application.add_handler(CommandHandler("free_sms_stats", handlers.free_sms_stats_command))
    # application.add_handler(CommandHandler("free_sms_countries", handlers.free_sms_countries_command))
    application.add_handler(CommandHandler("grant_access", handlers.grant_access_command))
    application.add_handler(CommandHandler("temp_access", handlers.temp_access_command))
    application.add_handler(CommandHandler("revoke_access", handlers.revoke_access_command))
    application.add_handler(CommandHandler("check_access", handlers.check_access_command))
    application.add_handler(CommandHandler("list_access", handlers.list_access_command))
    application.add_handler(CommandHandler("settings", handlers.settings_command))
    application.add_handler(CommandHandler("admin", handlers.admin_panel_command))
    application.add_handler(CommandHandler("reply", handlers.reply_command))
    application.add_handler(CommandHandler("logs", handlers.logs_command))
    application.add_handler(CommandHandler("crypto", handlers.crypto_command))
    application.add_handler(CommandHandler("cryptopredict", handlers.cryptopredict_command))
    application.add_handler(CommandHandler("portfolio", handlers.portfolio_command))
    
    # Real-time commands
    application.add_handler(CommandHandler("alert", handlers.alert_command))
    application.add_handler(CommandHandler("live", handlers.live_command))
    application.add_handler(CommandHandler("subscriptions", handlers.subscriptions_command))
    
    # Character customization and help system
    application.add_handler(CommandHandler("character", handlers.character_command))
    application.add_handler(CommandHandler("personality", handlers.personality_command))
    application.add_handler(CommandHandler("help_bubbles", handlers.help_bubbles_command))
    
    # Add callback query handler for admin panel
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(handlers.handle_admin_callback))
    
    # Add message handler for all messages (text, photos, videos, etc.)
    application.add_handler(MessageHandler(~filters.COMMAND, handlers.handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Set bot commands and run
    async def startup():
        await set_bot_commands(application)
        logger.info("Bot is running...")
        
        # Initialize global services with bot instance
        global realtime_service, group_surveillance, admin_controls
        from bot_handlers import realtime_service, group_surveillance, admin_controls
        
        # Initialize services
        if not realtime_service:
            realtime_service = RealTimeService(application.bot)
            await realtime_service.start_realtime_services()
            logger.info("Real-time service started")
        
        if not group_surveillance:
            group_surveillance = GroupSurveillanceService(application.bot)
            logger.info("Group surveillance service initialized")
        
        if not admin_controls:
            admin_controls = AdminControlsService(application.bot)
            logger.info("Admin controls service initialized")
        
        # Update global references in bot_handlers
        import bot_handlers
        bot_handlers.realtime_service = realtime_service
        bot_handlers.group_surveillance = group_surveillance
        bot_handlers.admin_controls = admin_controls
        
        # Schedule periodic cleanup
        async def periodic_cleanup():
            while True:
                await asyncio.sleep(3600)  # Clean every hour
                clean_old_downloads()
                logger.info("Performed periodic cleanup")
        
        # Start cleanup task
        asyncio.create_task(periodic_cleanup())
    
    # Initialize bot manager for 24/7 uptime
    from bot_manager import BotManager
    
    async def run_bot():
        await startup()
        bot_manager = BotManager(application)
        bot_manager.setup_signal_handlers()
        await bot_manager.start_with_recovery()
    
    # Run the bot with comprehensive recovery
    try:
        asyncio.get_event_loop().run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot manager crashed: {e}")
        # In production, this could trigger a container restart

if __name__ == "__main__":
    main()
