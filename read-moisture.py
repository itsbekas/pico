from machine import ADC, Pin
import time

soil_sensor = ADC(Pin(26))

while True:
    moisture_level = soil_sensor.read_u16()  # Read the moisture level
    print(f"Soil Moisture Level: {moisture_level / 65535 * 100:.2f}%")  # Convert to percentage
    time.sleep(2)  # Wait for 2 seconds before the next reading