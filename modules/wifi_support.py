import asyncio
import network
import ujson
import os
import time
from machine import Pin

class WiFiManager:
    def __init__(self):
        self.led = Pin("LED", Pin.OUT)
        self.connected_to_wifi = False
        self.wifi_config_file = "wifi_config.json"
        self.wlan = None
        self.ap = None
        self.ip_address = None
        self.max_retries = 3
        self.retry_delay = 2

    async def led_blink_task(self):
        """Async task to handle LED blinking when not connected"""
        try:
            print("LED blinking task started")
            while not self.connected_to_wifi:
                self.led.on()
                await asyncio.sleep(0.1)
                self.led.off()
                await asyncio.sleep(1.9)
            self.led.on()
            print("LED blinking task stopped due to Wi-Fi connection")
        except Exception as e:
            print(f"LED task error: {e}")
            self.led.off()

    def scan_ssids(self):
        """Scan for available Wi-Fi SSIDs"""
        try:
            # Initialize WLAN if not already initialized
            if self.wlan is None:
                self.wlan = network.WLAN(network.STA_IF)
                self.wlan.active(True)
            
            print("Scanning for Wi-Fi networks...")
            # Perform the scan
            scan_results = self.wlan.scan()
            
            # Extract SSIDs from scan results
            ssids = [network[0].decode() for network in scan_results]
            unique_ssids = sorted(list(set(ssids)))  # Remove duplicates and sort
            
            if unique_ssids:
                print("Available Wi-Fi SSIDs:", unique_ssids)
            else:
                print("No Wi-Fi networks found.")
            
            return unique_ssids
        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")
            return []
        finally:
            # Optionally deactivate WLAN to save power if not connecting
            if self.wlan and not self.connected_to_wifi:
                self.wlan.active(False)

    def load_wifi_config(self):
        """Load Wi-Fi credentials from config file (synchronous)"""
        try:
            with open(self.wifi_config_file, "r") as f:
                return ujson.load(f)
        except (OSError, ValueError) as e:
            print(f"Failed to load Wi-Fi config: {e}")
            return None

    def save_wifi_config(self, ssid, password):
        """Save Wi-Fi credentials to config file (synchronous)"""
        try:
            config = {"ssid": ssid, "password": password}
            with open(self.wifi_config_file, "w") as f:
                ujson.dump(config, f)
        except (OSError, ValueError) as e:
            print(f"Failed to save Wi-Fi config: {e}")

    async def disconnect_wifi(self):
        """Disconnect from any existing Wi-Fi connection"""
        try:
            if self.wlan:
                if self.wlan.active() and self.wlan.isconnected():
                    self.wlan.disconnect()
                    print("Disconnected from Wi-Fi")
                if self.wlan.active():
                    self.wlan.active(False)
                    print("Wi-Fi interface deactivated")
                self.connected_to_wifi = False
                self.ip_address = None
        except Exception as e:
            print(f"Error disconnecting Wi-Fi: {e}")
            self.led.off()
        finally:
            self.wlan = None

    async def connect_to_wifi(self, ssid, password):
        """Attempt to connect to Wi-Fi network with retries"""
        try:           
            for attempt in range(self.max_retries):
                try:
                    if not self.wlan:
                        self.wlan = network.WLAN(network.STA_IF)
                    if not self.wlan.active():
                        self.wlan.active(True)
                    
                    print(f"Attempting to connect to Wi-Fi (attempt {attempt + 1}/{self.max_retries})...")
                    self.wlan.connect(ssid, password)
                    
                    max_wait = 15
                    start_time = time.time()
                    while time.time() - start_time < max_wait:
                        status = self.wlan.status()
                        if status < 0 or status >= 3:
                            break
                        await asyncio.sleep(0.5)
                    
                    if self.wlan.isconnected():
                        self.connected_to_wifi = True
                        self.ip_address = self.wlan.ifconfig()[0]
                        print("Connected to Wi-Fi")
                        print("IP Address:", self.ip_address)
                        await self.stop_ap_mode()
                        return True, self.ip_address
                    else:
                        print(f"Connection attempt {attempt + 1} failed, status: {status}")
                        if attempt < self.max_retries - 1:
                            print(f"Retrying in {self.retry_delay} seconds...")
                            await asyncio.sleep(self.retry_delay)
                except Exception as e:
                    print(f"Error during connection attempt {attempt + 1}: {e}")
                    if "do_ioctl" in str(e) and "timeout" in str(e):
                        print("CYW43 ioctl timeout detected")
                    if attempt < self.max_retries - 1:
                        print(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
            
            self.connected_to_wifi = False
            print("Failed to connect to Wi-Fi after all retries")
            return False, None
        except Exception as e:
            print(f"Critical error connecting to Wi-Fi: {e}")
            self.connected_to_wifi = False
            self.led.off()
            return False, None
        finally:
            if not self.connected_to_wifi:
                await self.disconnect_wifi()

    async def start_ap_mode(self):
        """Start Access Point mode with retries"""
        try:
            await self.disconnect_wifi()
            
            for attempt in range(self.max_retries):
                try:
                    if not self.ap:
                        self.ap = network.WLAN(network.AP_IF)
                    if not self.ap.active():
                        self.ap.active(True)
                        self.ap.config(essid="PicoW-Setup", password="picow1234")
                    
                    print("Access Point started")
                    print("IP Address:", self.ap.ifconfig()[0])
                    return self.ap
                except Exception as e:
                    print(f"Error starting AP mode (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if "do_ioctl" in str(e) and "timeout" in str(e):
                        print("CYW43 ioctl timeout detected")
                    if attempt < self.max_retries - 1:
                        print(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
            
            print("Failed to start AP mode after all retries")
            self.led.off()
            return None
        except Exception as e:
            print(f"Critical error starting AP mode: {e}")
            self.led.off()
            return None

    async def stop_ap_mode(self):
        """Stop Access Point mode"""
        try:
            if self.ap:
                was_active = self.ap.active()
                if was_active:
                    self.ap.active(False)
                    print("Access Point stopped")
                else:
                    print("Access Point was already stopped")
            else:
                print("No AP interface available to stop")
        except AttributeError as e:
            print(f"AP interface error: {e}")
            self.led.off()
        except OSError as e:
            print(f"OS error while stopping AP: {e}")
            self.led.off()
        except Exception as e:
            print(f"Unexpected error while stopping AP: {e}")
            self.led.off()
        finally:
            if self.ap and not self.ap.active():
                self.ap = None