import uasyncio as asyncio
from machine import Pin

from modules.ha_connection import toggle_entity
from modules.rgb_led_module import RGBLEDController
rgb_controller=RGBLEDController()

class PIRSensor:
    def __init__(self, pir_pin=16):
        """Initialize PIR sensor with the specified pin."""
        self.pir = Pin(pir_pin, Pin.IN)
        self._is_active = False
        self._is_running=False
        self._running = asyncio.Event()
        
    async def activate_pir(self):
        """Start the PIR sensor detection loop."""
        if self._is_active:
            print("PIR sensor is already active")
            return
        
        self._is_active = True
        self._running.set()
        print("PIR sensor activated")
        
        while self._running.is_set():
            if self.pir.value() == 1:
                if self._is_running is not True:
                    if rgb_controller.is_running is False:
                        toggle_entity(domain='input_boolean',entity='input_boolean.mobile_motion_sensor',action='turn_on')
                        rgb_controller.rgb_task = asyncio.create_task(rgb_controller.run_rgb_led(sleep_time=2))
                    print("Motion detected!")
                    self._is_running=True
            else:
                if self._is_running:
                    if rgb_controller.rgb_task is not None:
                        rgb_controller.rgb_task.cancel()
                        rgb_controller.rgb_task = None
                        toggle_entity(domain='input_boolean',entity='input_boolean.mobile_motion_sensor',action='turn_off')
                        print("No motion")
                    self._is_running=False
            await asyncio.sleep(0.5)  # Check every 500ms
        
        self._is_active = False
        print("PIR sensor deactivated")
    
    def deactivate_pir(self):
        """Stop the PIR sensor detection loop."""
        if not self._is_active:
            print("PIR sensor is already deactivated")
            return
        self._running.clear()