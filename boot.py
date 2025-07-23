import webrepl
import network
from secrets import SSID, PASSWORD
from machine import Pin
import time

BOOT = False

def boot():
    status_led = Pin(0, Pin.OUT)
    status_led.off()

    def blink_led():
        DELAY = 0.5
        status_led.value(1)
        time.sleep(DELAY)
        status_led.value(0)
        time.sleep(DELAY)

    wlan = network.WLAN(network.STA_IF)
    wlan.config(pm = 0xa11140)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    retries = 20

    while not wlan.isconnected() and retries > 0:
        blink_led()
        retries -= 1
        print("Status:", wlan.status())

    if not wlan.isconnected():
        print("Failed to connect to WiFi")
        status_led.value(0)
        raise RuntimeError("Could not connect to WiFi")

    status_led.on()
    print("Connected to WiFi:", wlan.ifconfig())

    webrepl.start()

if BOOT:
    boot()
