from machine import Pin
import time

button = Pin(16, Pin.IN, Pin.PULL_UP)

while True:
    if not button.value():  # Button pressed
        print("Button pressed!")
        time.sleep(0.5)  # Debounce delay
    time.sleep(0.1)  # Polling delay