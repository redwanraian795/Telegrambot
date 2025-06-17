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

class SmartHomeService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.devices = self.load_devices()
        self.automations = self.load_automations()
        self.sensor_data = self.load_sensor_data()
        self.running = False
        
    def load_devices(self) -> Dict[str, Any]:
        """Load smart home devices configuration"""
        try:
            if os.path.exists("smart_devices.json"):
                with open("smart_devices.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading smart devices: {e}")
        return {}
    
    def save_devices(self):
        """Save smart home devices configuration"""
        try:
            with open("smart_devices.json", 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving smart devices: {e}")
    
    def load_automations(self) -> Dict[str, Any]:
        """Load automation rules"""
        try:
            if os.path.exists("automations.json"):
                with open("automations.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading automations: {e}")
        return {}
    
    def save_automations(self):
        """Save automation rules"""
        try:
            with open("automations.json", 'w', encoding='utf-8') as f:
                json.dump(self.automations, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving automations: {e}")
    
    def load_sensor_data(self) -> Dict[str, Any]:
        """Load sensor data history"""
        try:
            if os.path.exists("sensor_data.json"):
                with open("sensor_data.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sensor data: {e}")
        return {}
    
    def save_sensor_data(self):
        """Save sensor data history"""
        try:
            with open("sensor_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.sensor_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving sensor data: {e}")
    
    async def start_monitoring(self):
        """Start smart home monitoring"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting smart home monitoring...")
        
        # Start monitoring tasks
        asyncio.create_task(self.sensor_monitor())
        asyncio.create_task(self.automation_engine())
        asyncio.create_task(self.device_health_monitor())
        
    async def stop_monitoring(self):
        """Stop smart home monitoring"""
        self.running = False
        logger.info("Stopping smart home monitoring...")
    
    def register_device(self, user_id: str, device_name: str, device_type: str, device_id: str) -> bool:
        """Register a new smart home device"""
        try:
            if user_id not in self.devices:
                self.devices[user_id] = {}
            
            device = {
                "name": device_name,
                "type": device_type,  # "light", "thermostat", "sensor", "camera", "lock", "speaker"
                "device_id": device_id,
                "status": "online",
                "state": "off" if device_type in ["light", "speaker"] else "unknown",
                "last_seen": datetime.now().isoformat(),
                "registered_at": datetime.now().isoformat()
            }
            
            self.devices[user_id][device_name] = device
            self.save_devices()
            return True
            
        except Exception as e:
            logger.error(f"Device registration error: {e}")
            return False
    
    def control_device(self, user_id: str, device_name: str, action: str, value: Optional[str] = None) -> bool:
        """Control a smart home device"""
        try:
            if user_id not in self.devices or device_name not in self.devices[user_id]:
                return False
            
            device = self.devices[user_id][device_name]
            device_type = device["type"]
            
            # Execute device control based on type
            if device_type == "light":
                if action == "on":
                    device["state"] = "on"
                elif action == "off":
                    device["state"] = "off"
                elif action == "brightness" and value:
                    device["state"] = f"on_{value}%"
                elif action == "color" and value:
                    device["state"] = f"on_{value}"
                    
            elif device_type == "thermostat":
                if action == "set_temperature" and value:
                    device["state"] = f"{value}°C"
                elif action == "mode" and value:
                    device["state"] = value  # "heat", "cool", "auto", "off"
                    
            elif device_type == "lock":
                if action == "lock":
                    device["state"] = "locked"
                elif action == "unlock":
                    device["state"] = "unlocked"
                    
            elif device_type == "speaker":
                if action == "play":
                    device["state"] = f"playing_{value}" if value else "playing"
                elif action == "pause":
                    device["state"] = "paused"
                elif action == "stop":
                    device["state"] = "stopped"
                elif action == "volume" and value:
                    device["state"] = f"volume_{value}%"
            
            device["last_seen"] = datetime.now().isoformat()
            self.save_devices()
            
            # Send confirmation to real device via API (simulate)
            self.send_device_command(device["device_id"], action, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Device control error: {e}")
            return False
    
    def send_device_command(self, device_id: str, action: str, value: Optional[str]):
        """Send command to actual IoT device"""
        try:
            # Integration with popular IoT platforms:
            # - Philips Hue API
            # - Nest API
            # - SmartThings API
            # - Home Assistant API
            # - MQTT broker for custom devices
            
            # Example for Philips Hue lights
            if device_id.startswith("hue_"):
                hue_bridge_ip = "192.168.1.100"  # User's Hue bridge IP
                hue_api_key = "your_hue_api_key"  # User's Hue API key
                light_id = device_id.replace("hue_", "")
                
                if action == "on":
                    payload = {"on": True}
                elif action == "off":
                    payload = {"on": False}
                elif action == "brightness":
                    payload = {"on": True, "bri": int(float(value) * 2.54)}
                elif action == "color":
                    # Convert color name to hue value
                    color_map = {"red": 0, "green": 25500, "blue": 46920}
                    payload = {"on": True, "hue": color_map.get(value, 14922)}
                else:
                    return
                
                url = f"http://{hue_bridge_ip}/api/{hue_api_key}/lights/{light_id}/state"
                requests.put(url, json=payload, timeout=5)
            
            # Example for smart thermostats via MQTT
            elif device_id.startswith("thermostat_"):
                # MQTT publish to device topic
                topic = f"smartthings/devices/{device_id}/command"
                payload = {"action": action, "value": value}
                # mqtt_client.publish(topic, json.dumps(payload))
            
            logger.info(f"Command sent to device {device_id}: {action} {value}")
            
        except Exception as e:
            logger.error(f"Error sending device command: {e}")
    
    def create_automation(self, user_id: str, name: str, trigger: Dict, actions: List[Dict]) -> bool:
        """Create automation rule"""
        try:
            if user_id not in self.automations:
                self.automations[user_id] = {}
            
            automation = {
                "name": name,
                "trigger": trigger,  # {"type": "time", "value": "18:00"} or {"type": "sensor", "device": "motion_sensor", "condition": "motion_detected"}
                "actions": actions,  # [{"device": "living_room_light", "action": "on"}]
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_triggered": None
            }
            
            self.automations[user_id][name] = automation
            self.save_automations()
            return True
            
        except Exception as e:
            logger.error(f"Automation creation error: {e}")
            return False
    
    async def sensor_monitor(self):
        """Monitor environmental sensors"""
        while self.running:
            try:
                for user_id, user_devices in self.devices.items():
                    for device_name, device in user_devices.items():
                        if device["type"] == "sensor":
                            # Read sensor data
                            sensor_data = await self.read_sensor_data(device["device_id"])
                            
                            if sensor_data:
                                # Store sensor data
                                if user_id not in self.sensor_data:
                                    self.sensor_data[user_id] = {}
                                if device_name not in self.sensor_data[user_id]:
                                    self.sensor_data[user_id][device_name] = []
                                
                                self.sensor_data[user_id][device_name].append({
                                    "timestamp": datetime.now().isoformat(),
                                    "data": sensor_data
                                })
                                
                                # Keep only last 100 readings
                                if len(self.sensor_data[user_id][device_name]) > 100:
                                    self.sensor_data[user_id][device_name] = self.sensor_data[user_id][device_name][-100:]
                                
                                self.save_sensor_data()
                                
                                # Check for alerts
                                await self.check_sensor_alerts(user_id, device_name, sensor_data)
                
                # Check sensors every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Sensor monitor error: {e}")
                await asyncio.sleep(60)
    
    async def read_sensor_data(self, device_id: str) -> Optional[Dict]:
        """Read data from environmental sensors"""
        try:
            # Simulate sensor readings - replace with real sensor APIs
            sensor_type = device_id.split("_")[0]
            
            if sensor_type == "temperature":
                return {
                    "temperature": 22.5,
                    "humidity": 45.2,
                    "unit": "celsius"
                }
            elif sensor_type == "motion":
                return {
                    "motion_detected": False,
                    "last_motion": "2025-06-17T02:15:30"
                }
            elif sensor_type == "door":
                return {
                    "status": "closed",
                    "last_opened": "2025-06-17T01:45:12"
                }
            elif sensor_type == "smoke":
                return {
                    "smoke_level": 0.02,
                    "status": "normal",
                    "battery": 95
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading sensor data: {e}")
            return None
    
    async def check_sensor_alerts(self, user_id: str, device_name: str, sensor_data: Dict):
        """Check sensor data for alert conditions"""
        try:
            alerts = []
            
            # Temperature alerts
            if "temperature" in sensor_data:
                temp = sensor_data["temperature"]
                if temp > 30:
                    alerts.append(f"High temperature alert: {temp}°C")
                elif temp < 10:
                    alerts.append(f"Low temperature alert: {temp}°C")
            
            # Motion alerts
            if sensor_data.get("motion_detected"):
                alerts.append(f"Motion detected by {device_name}")
            
            # Smoke alerts
            if "smoke_level" in sensor_data:
                smoke_level = sensor_data["smoke_level"]
                if smoke_level > 0.1:
                    alerts.append(f"SMOKE ALERT: Level {smoke_level}")
            
            # Door/window alerts
            if sensor_data.get("status") == "open":
                alerts.append(f"{device_name} opened")
            
            # Send alerts to user
            if alerts:
                message = f"🏠 **Smart Home Alert**\n\n"
                for alert in alerts:
                    message += f"⚠️ {alert}\n"
                message += f"\n📅 Time: {datetime.now().strftime('%H:%M:%S')}"
                
                try:
                    await self.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    logger.error(f"Failed to send sensor alert to {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking sensor alerts: {e}")
    
    async def automation_engine(self):
        """Process automation rules"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for user_id, user_automations in self.automations.items():
                    for automation_name, automation in user_automations.items():
                        if not automation.get("enabled", True):
                            continue
                        
                        trigger = automation["trigger"]
                        
                        # Check if trigger conditions are met
                        if await self.check_trigger(user_id, trigger, current_time):
                            # Execute automation actions
                            success = await self.execute_automation_actions(user_id, automation["actions"])
                            
                            if success:
                                automation["last_triggered"] = current_time.isoformat()
                                self.save_automations()
                                
                                # Notify user
                                message = f"🤖 **Automation Triggered**\n\n"
                                message += f"📋 **Rule**: {automation_name}\n"
                                message += f"⏰ **Time**: {current_time.strftime('%H:%M:%S')}"
                                
                                try:
                                    await self.bot.send_message(chat_id=user_id, text=message)
                                except Exception as e:
                                    logger.error(f"Failed to send automation notification to {user_id}: {e}")
                
                # Check automations every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Automation engine error: {e}")
                await asyncio.sleep(300)
    
    async def check_trigger(self, user_id: str, trigger: Dict, current_time: datetime) -> bool:
        """Check if automation trigger conditions are met"""
        try:
            trigger_type = trigger.get("type")
            
            if trigger_type == "time":
                trigger_time = trigger.get("value")  # "18:00"
                if trigger_time:
                    hour, minute = map(int, trigger_time.split(":"))
                    return current_time.hour == hour and current_time.minute == minute
            
            elif trigger_type == "sensor":
                device_name = trigger.get("device")
                condition = trigger.get("condition")
                
                if device_name and condition and user_id in self.sensor_data:
                    device_data = self.sensor_data[user_id].get(device_name, [])
                    if device_data:
                        latest_data = device_data[-1]["data"]
                        
                        if condition == "motion_detected":
                            return latest_data.get("motion_detected", False)
                        elif condition == "temperature_high":
                            return latest_data.get("temperature", 0) > 25
                        elif condition == "door_opened":
                            return latest_data.get("status") == "open"
            
            elif trigger_type == "device_state":
                device_name = trigger.get("device")
                state = trigger.get("state")
                
                if device_name and state and user_id in self.devices:
                    device = self.devices[user_id].get(device_name)
                    if device:
                        return device.get("state") == state
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trigger: {e}")
            return False
    
    async def execute_automation_actions(self, user_id: str, actions: List[Dict]) -> bool:
        """Execute automation actions"""
        try:
            for action in actions:
                device_name = action.get("device")
                device_action = action.get("action")
                value = action.get("value")
                
                if device_name and device_action:
                    success = self.control_device(user_id, device_name, device_action, value)
                    if not success:
                        logger.error(f"Failed to execute action on {device_name}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing automation actions: {e}")
            return False
    
    async def device_health_monitor(self):
        """Monitor device health and connectivity"""
        while self.running:
            try:
                for user_id, user_devices in self.devices.items():
                    offline_devices = []
                    
                    for device_name, device in user_devices.items():
                        last_seen = datetime.fromisoformat(device["last_seen"])
                        if datetime.now() - last_seen > timedelta(hours=1):
                            device["status"] = "offline"
                            offline_devices.append(device_name)
                        else:
                            device["status"] = "online"
                    
                    if offline_devices:
                        message = f"🏠 **Device Status Alert**\n\n"
                        message += f"📴 **Offline Devices**:\n"
                        for device in offline_devices:
                            message += f"• {device}\n"
                        message += f"\nCheck device connectivity and power status."
                        
                        try:
                            await self.bot.send_message(chat_id=user_id, text=message)
                        except Exception as e:
                            logger.error(f"Failed to send device health alert to {user_id}: {e}")
                
                self.save_devices()
                
                # Check device health every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Device health monitor error: {e}")
                await asyncio.sleep(600)
    
    def get_device_status(self, user_id: str) -> str:
        """Get formatted device status information"""
        try:
            user_devices = self.devices.get(user_id, {})
            
            if not user_devices:
                return "🏠 No smart home devices registered.\n\nUse `/register_device` to add devices!"
            
            status = "🏠 **Smart Home Status**\n\n"
            
            online_count = 0
            offline_count = 0
            
            for device_name, device in user_devices.items():
                device_status = device.get("status", "unknown")
                device_state = device.get("state", "unknown")
                device_type = device.get("type", "unknown")
                
                status_emoji = "🟢" if device_status == "online" else "🔴"
                type_emoji = {
                    "light": "💡",
                    "thermostat": "🌡️",
                    "sensor": "📊",
                    "camera": "📹",
                    "lock": "🔒",
                    "speaker": "🔊"
                }.get(device_type, "📱")
                
                status += f"{status_emoji} {type_emoji} **{device_name}**\n"
                status += f"   Status: {device_status} | State: {device_state}\n\n"
                
                if device_status == "online":
                    online_count += 1
                else:
                    offline_count += 1
            
            status += f"📊 **Summary**: {online_count} online, {offline_count} offline"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return "❌ Error retrieving device status."
    
    def get_sensor_summary(self, user_id: str) -> str:
        """Get sensor data summary"""
        try:
            user_sensors = self.sensor_data.get(user_id, {})
            
            if not user_sensors:
                return "📊 No sensor data available.\n\nRegister sensors with `/register_device` first!"
            
            summary = "📊 **Environmental Summary**\n\n"
            
            for sensor_name, readings in user_sensors.items():
                if readings:
                    latest = readings[-1]["data"]
                    timestamp = readings[-1]["timestamp"]
                    
                    summary += f"🌡️ **{sensor_name}**\n"
                    
                    if "temperature" in latest:
                        summary += f"   Temperature: {latest['temperature']}°C\n"
                    if "humidity" in latest:
                        summary += f"   Humidity: {latest['humidity']}%\n"
                    if "motion_detected" in latest:
                        motion_status = "Yes" if latest["motion_detected"] else "No"
                        summary += f"   Motion: {motion_status}\n"
                    if "status" in latest:
                        summary += f"   Status: {latest['status']}\n"
                    
                    summary += f"   Last Update: {timestamp[:16]}\n\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting sensor summary: {e}")
            return "❌ Error retrieving sensor data."