from flask import Flask
import subprocess
import threading
import time
import os

app = Flask(__name__)

# Global variable to track if bot is started
bot_started = False

def start_bot_once():
    """Start the bot only once"""
    global bot_started
    if not bot_started:
        bot_started = True
        time.sleep(1)  # Brief delay
        subprocess.Popen(['python', 'main.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

@app.route('/')
def home():
    start_bot_once()
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
    # Start the Flask app for external access
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)