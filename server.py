#!/usr/bin/env python3
import os
import subprocess
import threading
import time
from flask import Flask
from waitress import serve

app = Flask(__name__)

# Track if bot is started
bot_process = None

def start_telegram_bot():
    """Start the Telegram bot in background"""
    global bot_process
    if bot_process is None:
        bot_process = subprocess.Popen(['python', 'main.py'], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)

@app.route('/')
def home():
    # Start bot on first request
    if bot_process is None:
        threading.Thread(target=start_telegram_bot, daemon=True).start()
        time.sleep(1)  # Brief delay for bot startup
    return "Bot is alive!"

@app.route('/health')
def health():
    return "Bot is alive!"

@app.route('/status')
def status():
    return "Bot is alive!"

@app.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Use Waitress for production deployment
    serve(app, host='0.0.0.0', port=port)