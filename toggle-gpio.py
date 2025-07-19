from machine import Pin
import time

GPIO_PIN = 0
pin = Pin(GPIO_PIN, Pin.OUT)

while True:
    pin.value(1)
    time.sleep(3)
    pin.value(0)
    time.sleep(1)
    print("Toggled GPIO pin", GPIO_PIN)
    time.sleep(1)  # Additional delay to avoid rapid toggling
