import asyncio
import os
import time
import dht
from machine import Pin, Timer
from umqtt.MqttPublisher import MqttPublisher
from ota.ota import OTAUpdater
from microdot import Microdot, Response
from modules.wifi_support import WiFiManager
from modules.html_template import SUCCESS_HTML,CONFIG_HTML,STATUS_HTML,CONTROL_HTML
from modules.rgb_led_module import RGBLEDController
from modules.pir_motion_sensor import PIRSensor
from modules.photocell_monitor import PhotocellSensor
from modules.ha_connection import update_state_entity
# Initialize Microdot app (async version)
app = Microdot()

#Initiate Updater
firmware_url = "https://raw.githubusercontent.com/Lilydales/pico_mobile_sensor/"
ota_updater = OTAUpdater(firmware_url)
                    
# --------- Configuration ---------
MQTT_BROKER = "192.168.86.52"  # IP of your Home Assistant / MQTT broker
MQTT_PORT = 1883
MQTT_USER = "System"
MQTT_PASSWORD = "@N1w4t0r1"
MQTT_TOPIC = b"pico/sensor/temperaturenhumidity"
# --------- Set up MQTT ---------
MQTT_CONFIG={
    'user':MQTT_USER,
    'password':MQTT_PASSWORD,
    'broker':MQTT_BROKER,
    'port':MQTT_PORT
    }
# --------- Set up DHT11 Sensor ---------
sensor = dht.DHT11(Pin(17))

# Create instance
wifi_manager = WiFiManager()

#Publish DHT11 Data
async def pushlishing_temp_humid_mqtt(mqtt,interval=30):
    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            mqtt.publish("pico/sensor/temperaturenhumidity", {
                "temperature": temp,
                "humidity": hum
            })
        except OSError as e:
            print("Sensor error:", e)
            
        await asyncio.sleep(interval)
# Start PIR sensor
async def start_pir_sensor():
    sensor = PIRSensor(pir_pin=16)
    
    # Activate the sensor
    task = asyncio.create_task(sensor.activate_pir())
    
    # Let it run for 5 seconds
    # await asyncio.sleep(5)
    
    # Deactivate the sensor
    sensor.deactivate_pir()
    
    # Wait for the task to complete
    await task

async def update_area_brightness_to_HA(interval=5):
    sensor = PhotocellSensor(adc_pin=26, fixed_resistor=10000,voltage=5)            
    
    while True:
        try:
            lux=sensor.get_lux_value()
            print("Current brightness:",lux)
            mqtt.publish("pico/sensor/brightnessdetector", {
                "brightness": lux,
            })
        except OSError as e:
            print("Sensor error:", e)
        await asyncio.sleep(interval)    
    
# Web routes (now async)
@app.route('/')
async def index(request):
    if wifi_manager.connected_to_wifi:
        return Response(body=SUCCESS_HTML.replace('{{ ip_address }}', wifi_manager.ip_address),
                        headers={'Content-Type': 'text/html'})
    status_message = "Connect to 'PicoW-Setup' network<br>if you're seeing this page"
    ssid_list=wifi_manager.scan_ssids()
    ssid_message=''
    for ssid in ssid_list:
        ssid_message+=f'<option value="{ssid}"></option>'
    return Response(body=CONFIG_HTML.replace('{{ status_message }}', status_message).replace('{{ ssid }}', ssid_message),
                    headers={'Content-Type': 'text/html'})

def check_and_create_file(action):
    if f'{action}.txt' not in os.listdir():
        with open(f'{action}.txt', 'w') as f:
            f.write('')  # or write some initial content
        print(f"✅ File {action}.txt created.")
        return f"✅ File {action}.txt created."
    else:
        print(f"ℹ️ File {action}.txt already exists.")
        return f"ℹ️ File {action}.txt already exists."

@app.route('/system')
async def system_manipulation(request):
    if request.method == 'GET':
        action = request.args.get('action','')
        if action=='no_auto_run':
            response=check_and_create_file(action)
            return Response(body=response)
        if action=='to_be_updated':
            response=check_and_create_file(action)
            return Response(body=response)
        if action=='reset':
            machine.reset()
        if action=='check_update':
            check_update=OTAUpdater(firmware_url)
            response=f'New version ({check_update.latest_version}) is available.<br>Current version: {check_update.current_version}' if check_update.check_for_updates() else f'No new updates available.<br>Current version: {check_update.current_version}'
            return Response(body=response)
            
            
# Initialize RGB LED controller
rgb_controller = RGBLEDController()

# Control endpoint for GET and POST requests
@app.route('/control', methods=['GET', 'POST'])
async def control_page(request):
    if request.method == 'GET':
        attr_param = request.args.get('attribute','')
        if attr_param=='current_rgb':
            return Response(body=rgb_controller.current_rgb)
        else:
            return Response(body=CONTROL_HTML.replace("{{ activate-status }}",''), headers={'Content-Type': 'text/html'})
    if request.method == 'POST':
        if rgb_controller.is_running:
            # If task is running, cancel it
            if rgb_controller.rgb_task is not None:
                rgb_controller.rgb_task.cancel()
                rgb_controller.rgb_task = None
                return Response(body="RGB task stopped")
            else:
                return Response(body="No RGB task running")
        else:
            # Start the RGB task with sleep_time=2
            rgb_controller.rgb_task = asyncio.create_task(rgb_controller.run_rgb_led(sleep_time=2))
            return Response(body="RGB task started")
        


@app.route('/config', methods=['GET'])
async def config_page(request):
    status_message = 'Enter new Wi-Fi credentials<div><a href="/" class="link">Back to Home</a></div>'
    return Response(body=CONFIG_HTML.replace('{{ status_message }}', status_message),
                    headers={'Content-Type': 'text/html'})

@app.route('/config', methods=['POST'])
async def configure_wifi(request):
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    
    ssid_list=wifi_manager.scan_ssids()
    ssid_message=''
    for ssid in ssid_list:
        ssid_message+=f'<option value="{ssid}"></option>'
        
    if ssid and password:
        wifi_manager.save_wifi_config(ssid, password)
        connected, ip_address = await wifi_manager.connect_to_wifi(ssid, password)
        
        if connected:
            return Response(body=SUCCESS_HTML.replace('{{ ip_address }}', ip_address),
                            headers={'Content-Type': 'text/html'})
        else:
            status_message = "Failed to connect. Please try again.<br>Connect to 'PicoW-Setup' network"
            return Response(body=CONFIG_HTML.replace('{{ status_message }}', status_message).replace('{{ ssid }}', ssid_message),
                            headers={'Content-Type': 'text/html'})
    return Response(status=400)

@app.route('/status')
async def status(request):
    if wifi_manager.connected_to_wifi:
        wifi_config = wifi_manager.load_wifi_config()
        check_update=OTAUpdater(firmware_url)
        status_html = STATUS_HTML.replace('{{ ip_address }}', wifi_manager.ip_address)
        status_html = status_html.replace('{{ ssid }}', wifi_config['ssid'] if wifi_config else 'Unknown')
        status_html = status_html.replace('{{ status }}', 'Connected')
        status_html = status_html.replace('{{ version }}', f'Current version: {check_update.current_version}')
        return Response(body=status_html, headers={'Content-Type': 'text/html'})
    return Response(status=404)

@app.route('/success')
async def success(request):
    if wifi_manager.connected_to_wifi:
        return Response(body=SUCCESS_HTML.replace('{{ ip_address }}', wifi_manager.ip_address),
                        headers={'Content-Type': 'text/html'})
    wifi_config = wifi_manager.load_wifi_config()
    if wifi_config:
        connected, ip_address = await wifi_manager.connect_to_wifi(wifi_config["ssid"], wifi_config["password"])
        if connected:
            return Response(body=SUCCESS_HTML.replace('{{ ip_address }}', ip_address),
                            headers={'Content-Type': 'text/html'})
    return Response(status=404)



async def main():
    try:
        # Start LED blinking task
        asyncio.create_task(wifi_manager.led_blink_task())
        
        # Try to load existing Wi-Fi configuration
        wifi_config = wifi_manager.load_wifi_config()
        
        # If config exists, try to connect
        if wifi_config:
            print("Found Wi-Fi configuration, attempting to connect...")
            connected, ip_address = await wifi_manager.connect_to_wifi(wifi_config["ssid"], wifi_config["password"])
            if connected:
                #Check if the file no_auto_run.txt is exist, if yes then turn off the machine
                if 'no_auto_run.txt' in os.listdir():
                    print("No auto run command found. Shut down...")
                    machine.disable_irq()
                    return
                #Check if the file to_be_updated.txt is exist, if yes then update the machine
                if 'to_be_updated.txt' in os.listdir():
                    print("Machine will be updated")
                    update=ota_updater.download_and_install_update_if_available('to_be_updated.txt')
                    if 'No new updates available' in update:
                        print('Removing to_be_update file...')
                        os.remove('to_be_updated.txt')
                
                #Set up mqtt connection
                mqtt = MqttPublisher(MQTT_CONFIG)
                print("Starting success page server...")
                asyncio.create_task(start_pir_sensor())
                asyncio.create_task(update_area_brightness_to_HA(interval=10))
                asyncio.create_task(pushlishing_temp_humid_mqtt(mqtt,interval=30))
                await app.run(port=80)
                return
        
        # If no config or connection failed, start AP mode
        print("Starting configuration mode...")
        await wifi_manager.start_ap_mode()
        await app.run(port=80)
    except Exception as e:
        print(f"Fatal error in main: {e}")
        wifi_manager.led.off()
        await wifi_manager.stop_ap_mode()
        await wifi_manager.disconnect_wifi()
        await wifi_manager.start_ap_mode()
        await app.run(port=80)
    except:
        print(f"Unknown error!")
        wifi_manager.led.off()
        await wifi_manager.stop_ap_mode()
        await wifi_manager.disconnect_wifi()

if __name__ == "__main__":
    asyncio.run(main())


