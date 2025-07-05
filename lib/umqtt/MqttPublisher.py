import network
import time
import ubinascii
import machine
from umqtt.simple import MQTTClient
import ujson as json

class MqttPublisher:
    def __init__(self, mqtt_config, connect_wifi=False, wifi_config=None):
        self.mqtt_config = mqtt_config
        self.wifi_config = wifi_config
        self.wlan = None
        self.client = None
        
        if connect_wifi and wifi_config:
            self.wifi_connect(wifi_config["ssid"], wifi_config["password"])
        
        self.client = self.init_mqtt_client(mqtt_config)
        self.connect_mqtt()
        print("MQTT connected")

    def wifi_connect(self, ssid, password):
        """Connect to Wi-Fi with a timeout."""
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print("Connecting to Wi-Fi...")
            self.wlan.connect(ssid, password)
            timeout = 10  # 10-second timeout
            start = time.time()
            while not self.wlan.isconnected() and (time.time() - start) < timeout:
                print("Waiting for Wi-Fi...")
                time.sleep(1)
            if not self.wlan.isconnected():
                raise RuntimeError("Failed to connect to Wi-Fi")
        print("Wi-Fi connected:", self.wlan.ifconfig())

    def check_wifi(self):
        """Check if Wi-Fi is connected."""
        return self.wlan and self.wlan.isconnected()

    def init_mqtt_client(self, config):
        """Initialize MQTT client."""
        client_id = ubinascii.hexlify(machine.unique_id())
        return MQTTClient(
            client_id,
            config["broker"],
            port=config.get("port", 1883),
            user=config.get("user", None),
            password=config.get("password", None),
            keepalive=config.get("keepalive", 60)
        )

    def connect_mqtt(self):
        """Connect to MQTT broker."""
        try:
            self.client.connect()
            print(f"Connected to MQTT broker {self.mqtt_config['broker']}")
        except Exception as e:
            print(f"Failed to connect to MQTT: {e}")
            self.client = None
            raise

    def reconnect(self):
        """Reconnect to Wi-Fi and MQTT if necessary."""
        print("Attempting to reconnect...")
        try:
            if self.wifi_config and not self.check_wifi():
                print("Wi-Fi disconnected, reconnecting...")
                self.wifi_connect(self.wifi_config["ssid"], self.wifi_config["password"])
            
            if self.client is None:
                self.client = self.init_mqtt_client(self.mqtt_config)
            
            self.connect_mqtt()
            print("Reconnection successful")
            return True
        except Exception as e:
            print(f"Reconnection failed: {e}")
            self.client = None
            return False

    def publish(self, topic, payload):
        """Publish a message with reconnection handling."""
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        
        # Check connections
        if self.wifi_config and not self.check_wifi():
            print("Wi-Fi disconnected, attempting to reconnect...")
            if not self.reconnect():
                return False
        
        if self.client is None:
            print("MQTT client not initialized, attempting to reconnect...")
            if not self.reconnect():
                return False
        
        try:
            self.client.publish(topic.encode(), payload.encode())
            print(f"Published to {topic}: {payload}")
            return True
        except Exception as e:
            print(f"Failed to publish to {topic}: {e}")
            self.client = None  # Mark client as disconnected
            return False

    def disconnect(self):
        """Disconnect from MQTT and Wi-Fi."""
        try:
            if self.client:
                self.client.disconnect()
                print("MQTT disconnected")
        except Exception as e:
            print(f"Error disconnecting MQTT: {e}")
        finally:
            self.client = None
        
        if self.wlan and self.wlan.isconnected():
            self.wlan.disconnect()
            self.wlan.active(False)
            print("Wi-Fi disconnected")