from time import sleep
from machine import Pin, PWM
import random
import asyncio

class RGBLEDController:
    def __init__(self, red_pin=22, blue_pin=21, green_pin=20, onboard_led_pin="LED"):
        # Initialize onboard LED
        self.led = Pin(onboard_led_pin, Pin.OUT)
        self.led.value(1)  # Turn on to indicate power-on
        
        self.current_rgb='rgb(0,0,0)'

        # Initialize RGB LED pins with PWM
        self.red = PWM(Pin(red_pin))
        self.blue = PWM(Pin(blue_pin))
        self.green = PWM(Pin(green_pin))

        # Set PWM frequency (1000 Hz is suitable for LEDs)
        self.red.freq(1000)
        self.blue.freq(1000)
        self.green.freq(1000)

        # Task state
        self.rgb_task = None
        self.is_running = False

    def set_random_color(self):
        """Generate random RGB values (0-255)."""
        red_value = random.randint(0, 255)
        blue_value = random.randint(0, 255)
        green_value = random.randint(0, 255)
        return red_value, blue_value, green_value

    def get_color_name(self, red_value, blue_value, green_value):
        """Determine color name based on RGB values (for debugging)."""
        
        self.current_rgb=f'rgb({red_value},{green_value},{blue_value})'
        if red_value == 0 and blue_value == 0 and green_value == 0:
            return "Off"
        return f"RGB({red_value}, {blue_value}, {green_value})"

    async def fade_in_out(self, red_value, blue_value, green_value, sleep_time=1):
        """Fade in and out for a given RGB color."""
        steps = 100  # Number of steps for smooth fading
        max_duty = 65535  # Maximum PWM duty cycle (16-bit resolution)

        # Convert 0-255 RGB values to PWM duty cycle range (0-65535)
        red_duty_max = int(red_value * max_duty / 255)
        blue_duty_max = int(blue_value * max_duty / 255)
        green_duty_max = int(green_value * max_duty / 255)

        # Fade in
        for i in range(steps + 1):
            duty_factor = i / steps
            self.red.duty_u16(int(red_duty_max * duty_factor))
            self.blue.duty_u16(int(blue_duty_max * duty_factor))
            self.green.duty_u16(int(green_duty_max * duty_factor))
            await asyncio.sleep(sleep_time / steps)  # Total fade-in time = sleep_time

        # Fade out
        for i in range(steps, -1, -1):
            duty_factor = i / steps
            self.red.duty_u16(int(red_duty_max * duty_factor))
            self.blue.duty_u16(int(blue_duty_max * duty_factor))
            self.green.duty_u16(int(green_duty_max * duty_factor))
            await asyncio.sleep(sleep_time / steps)  # Total fade-out time = sleep_time

    async def run_rgb_led(self, optional='', sleep_time=1,show_color=False):
        """Run the RGB LED task with random colors and fading."""
        self.is_running = True
        try:
            while True:
                try:
                    # Get random RGB color
                    red_value, blue_value, green_value = self.set_random_color()
                    
                    # Print the current color for debugging
                    color_name = self.get_color_name(red_value, blue_value, green_value)
                    if show_color: print(f"Color: {color_name}")
                    
                    # Fade in and out for the selected color
                    await self.fade_in_out(red_value, blue_value, green_value, sleep_time=sleep_time)
                
                except OSError as e:
                    print(f"Error: {e}")
                    await asyncio.sleep(1)
                    self.led.value(1)  # Indicate retry
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break

        except asyncio.CancelledError:
            # Turn off RGB LED and onboard LED on task cancellation
            self.red.duty_u16(0)
            self.blue.duty_u16(0)
            self.green.duty_u16(0)
            self.is_running = False
            print("RGB task cancelled")
            raise
