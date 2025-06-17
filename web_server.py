from flask import Flask
import os
import subprocess
import threading
import time

app = Flask(__name__)

def start_telegram_bot():
    """Start the Telegram bot in a separate process"""
    time.sleep(2)  # Give Flask a moment to start
    subprocess.Popen(['python', 'main.py'])

@app.route('/')
def home():
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
    # Start Telegram bot in background
    threading.Thread(target=start_telegram_bot, daemon=True).start()
    
    # Start Flask server for external access
    app.run(host='0.0.0.0', port=5000, debug=False)