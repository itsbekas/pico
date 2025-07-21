import webrepl
import network
from secrets import SSID, PASSWORD
from machine import Pin
import time

status_led = Pin(0, Pin.OUT)
status_led.off()

def blink_led():
    status_led.value(1)
    time.sleep(0.5)
    status_led.value(0)
    time.sleep(0.5)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    blink_led()

status_led.on()
print("Connected to WiFi:", wlan.ifconfig())

webrepl.start()
