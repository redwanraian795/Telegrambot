import os
import subprocess
import threading
import time
from flask import Flask

app = Flask(__name__)

# Track bot status
bot_started = False

def start_bot():
    """Start the Telegram bot in background"""
    global bot_started
    if not bot_started:
        bot_started = True
        # Start bot in separate process
        subprocess.Popen(['python', 'main.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)

@app.route('/')
def home():
    if not bot_started:
        threading.Thread(target=start_bot, daemon=True).start()
        time.sleep(2)  # Allow bot startup
    return "Bot is alive!"

@app.route('/health')
def health():
    return "Bot is alive!"

@app.route('/status') 
def status():
    return "Bot is alive!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)