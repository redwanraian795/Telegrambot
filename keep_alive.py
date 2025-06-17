import threading
import time
import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class KeepAlive:
    """Keep the Replit app alive on free tier by self-pinging"""
    
    def __init__(self, url=None, interval=60):  # 1 minute - very aggressive
        self.url = url or "http://localhost:8080"
        self.interval = interval  # seconds
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the keep-alive service"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
            self.thread.start()
            logger.info(f"Keep-alive service started, pinging every {self.interval} seconds")
    
    def stop(self):
        """Stop the keep-alive service"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Keep-alive service stopped")
    
    def _keep_alive_loop(self):
        """Main keep-alive loop"""
        while self.running:
            try:
                response = requests.get(self.url, timeout=10)
                if response.status_code == 200:
                    logger.debug(f"Keep-alive ping successful: {response.text.strip()}")
                else:
                    logger.warning(f"Keep-alive ping returned status {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Keep-alive ping failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in keep-alive: {e}")
            
            # Wait for next ping
            time.sleep(self.interval)

# Global instance
keep_alive_service = KeepAlive()

def start_keep_alive():
    """Start the keep-alive service"""
    keep_alive_service.start()

def stop_keep_alive():
    """Stop the keep-alive service"""
    keep_alive_service.stop()