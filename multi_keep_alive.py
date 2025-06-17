import threading
import time
import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiKeepAlive:
    """Multiple keep-alive strategies to prevent Replit sleep"""
    
    def __init__(self):
        self.running = False
        self.threads = []
        self.base_url = "http://localhost:8080"
        self.external_urls = [
            "https://httpbin.org/delay/1",  # External ping service
            "https://api.github.com",       # GitHub API (always available)
            "https://www.google.com",       # Google (reliable)
        ]
    
    def start(self):
        """Start all keep-alive strategies"""
        if not self.running:
            self.running = True
            
            # Strategy 1: Aggressive self-ping every 15 seconds
            thread1 = threading.Thread(target=self._self_ping_loop, daemon=True)
            thread1.start()
            self.threads.append(thread1)
            
            # Strategy 2: External requests every 30 seconds
            thread2 = threading.Thread(target=self._external_ping_loop, daemon=True)
            thread2.start()
            self.threads.append(thread2)
            
            # Strategy 3: Activity simulation every 20 seconds
            thread3 = threading.Thread(target=self._activity_simulation, daemon=True)
            thread3.start()
            self.threads.append(thread3)
            
            # Strategy 4: Health check server activity every 25 seconds
            thread4 = threading.Thread(target=self._health_check_activity, daemon=True)
            thread4.start()
            self.threads.append(thread4)
            
            # Strategy 5: Ultra-aggressive pinging every 10 seconds
            thread5 = threading.Thread(target=self._ultra_aggressive_ping, daemon=True)
            thread5.start()
            self.threads.append(thread5)
            
            logger.info("Multi-layer keep-alive system started with 5 strategies")
    
    def stop(self):
        """Stop all keep-alive strategies"""
        self.running = False
        logger.info("Multi-layer keep-alive system stopped")
    
    def _self_ping_loop(self):
        """Strategy 1: Aggressive ping own server every 15 seconds"""
        while self.running:
            try:
                response = requests.get(f"{self.base_url}/", timeout=5)
                logger.debug(f"Self-ping successful: {response.status_code}")
            except Exception as e:
                logger.debug(f"Self-ping failed: {e}")
            time.sleep(15)
    
    def _external_ping_loop(self):
        """Strategy 2: Make external requests every 30 seconds to keep network active"""
        while self.running:
            try:
                for url in self.external_urls:
                    try:
                        response = requests.get(url, timeout=5)
                        logger.debug(f"External ping to {url}: {response.status_code}")
                        break  # Success, no need to try others
                    except:
                        continue
            except Exception as e:
                logger.debug(f"External ping failed: {e}")
            time.sleep(30)
    
    def _activity_simulation(self):
        """Strategy 3: Simulate various activities"""
        while self.running:
            try:
                # Simulate file operations
                timestamp = datetime.now().isoformat()
                activity_data = {
                    "timestamp": timestamp,
                    "activity": "keep_alive_simulation",
                    "status": "active"
                }
                
                # Write activity log
                with open("activity_log.json", "w") as f:
                    json.dump(activity_data, f)
                
                # Simulate memory usage
                temp_data = "x" * 1000  # Small memory allocation
                del temp_data
                
                logger.debug("Activity simulation completed")
            except Exception as e:
                logger.debug(f"Activity simulation failed: {e}")
            time.sleep(20)
    
    def _health_check_activity(self):
        """Strategy 4: Regular health check pings"""
        while self.running:
            try:
                # Multiple rapid pings to simulate user activity
                for i in range(3):
                    response = requests.get(f"{self.base_url}/", timeout=3)
                    time.sleep(2)
                logger.debug("Health check activity completed")
            except Exception as e:
                logger.debug(f"Health check activity failed: {e}")
            time.sleep(25)
    
    def _ultra_aggressive_ping(self):
        """Strategy 5: Ultra-aggressive pinging every 10 seconds to prevent any sleep"""
        while self.running:
            try:
                # Multiple rapid pings with different endpoints
                endpoints = ["/", "/health", "/status"]
                for endpoint in endpoints:
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=2)
                        logger.debug(f"Ultra-aggressive ping to {endpoint}: {response.status_code}")
                    except:
                        pass
                    time.sleep(1)
                
                # Also ping external services rapidly
                for url in self.external_urls[:1]:  # Only first URL for speed
                    try:
                        requests.get(url, timeout=2)
                        break
                    except:
                        pass
                        
            except Exception as e:
                logger.debug(f"Ultra-aggressive ping failed: {e}")
            time.sleep(10)

# Global instance
multi_keep_alive = MultiKeepAlive()

def start_multi_keep_alive():
    """Start the multi-layer keep-alive system"""
    multi_keep_alive.start()

def stop_multi_keep_alive():
    """Stop the multi-layer keep-alive system"""
    multi_keep_alive.stop()