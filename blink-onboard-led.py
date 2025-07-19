from machine import Pin
import time

# Define the onboard LED pin (GP25 on Pico)
led = Pin("LED", Pin.OUT)

while True:
    led.toggle()  # Turns the LED on/off
    time.sleep(0.5) # Waits for 0.5 seconds
