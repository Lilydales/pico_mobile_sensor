import uasyncio as asyncio
from machine import ADC, Pin

class PhotocellSensor:
    def __init__(self, adc_pin=26, fixed_resistor=10000,voltage=3.3):
        """Initialize photocell sensor with ADC pin and fixed resistor value (ohms)."""
        self.adc = ADC(Pin(adc_pin))
        self.fixed_resistor = fixed_resistor
        # Calibration constants (adjust based on your photocell and testing)
        self.lux_k = 128383  # Empirical constant for lux estimation
        self.exp=1.137
        self.voltage=voltage
    
    def read_adc(self):
        """Read ADC value (0–65535)."""
        return self.adc.read_u16()
    
    def calculate_resistance(self, adc_value):
        """Calculate photocell resistance from ADC value."""
        if adc_value == 0:
            return float('inf')  # Avoid division by zero
        # ADC value to voltage (3.3V reference, 16-bit ADC)
        voltage = adc_value * self.voltage / 65535
        # Voltage divider: V_out = V_in * R_fixed / (R_LDR + R_fixed)
        # Rearrange to solve for R_LDR
        if voltage >= self.voltage:
            return 0.0  # Avoid division by zero
        r_ldr = self.fixed_resistor * (self.voltage / voltage - 1)
        return r_ldr
    
    def estimate_lux(self, r_ldr):
        """Estimate lux from photocell resistance."""
        if r_ldr==0:
            return 10000
        lux = (self.lux_k/r_ldr)**self.exp
        return max(0, lux)  # Ensure non-negative lux
    
    def get_lux_value(self):
        adc_value = self.read_adc()
        r_ldr = self.calculate_resistance(adc_value)
        lux=round(self.estimate_lux(r_ldr))
        
        return lux
    async def monitor_light(self,show_lux_only=True):
        """Asynchronously monitor light levels."""
        while True:
            if show_lux_only:
                lux=self.get_lux_value()
                print(lux)
            else:         
                adc_value = self.read_adc()
                r_ldr = self.calculate_resistance(adc_value)
                lux=self.estimate_lux(r_ldr)
                print(f"ADC: {adc_value}, R_LDR: {r_ldr:.0f}Ω, lux: {lux}")
            await asyncio.sleep(0.5)  # Check every 500ms

