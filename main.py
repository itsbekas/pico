import uasyncio as asyncio
import umqtt.simple as mqtt

from blib_moisture import MoistureSensor
from blib_dht import read_dht
from mqtt_secrets import MQTT_SERVER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD
from machine import Pin
import dht

# GPIO PINS
DHT_PIN = 18
MOISTURE_PIN = 26
RELAY_PIN = 2

#* CALIBRATION VALUES - RUN calibrate-moisture-sensor.py TO SET THESE
AIR_MOISTURE = 52127
WATER_MOISTURE = 21064

# OPERATION DELAYS
CHECK_MSG_DELAY = 10 # 10 seconds
WATER_CHECK_DELAY = 60 * 15 # 15 minutes
DHT_CHECK_DELAY = 60 * 15 # 15 minutes
WATER_DURATION = 2 # 2 seconds

#! DO NOT EDIT BELOW THIS LINE
dht_pin = dht.DHT22(Pin(DHT_PIN))
moisture_sensor = MoistureSensor(pin=MOISTURE_PIN, air_moisture=AIR_MOISTURE, water_moisture=WATER_MOISTURE)
relay_pin = Pin(RELAY_PIN, Pin.OUT)

mqtt_client = mqtt.MQTTClient("mosquitto", MQTT_SERVER, port=MQTT_PORT, user=MQTT_USERNAME, password=MQTT_PASSWORD)


def create_timed_task(f, freq):
    async def wrapper():
        while True:
            f()
            await asyncio.sleep(freq)
    asyncio.create_task(wrapper())

def sub_callback(encoded_topic, encoded_msg):
    topic = encoded_topic.decode()
    msg = encoded_msg.decode()
    print(f"Received message on {topic}: {msg}")
    if topic == "command/water":
        water_plant()
    elif topic == "command/read_moisture":
        log_moisture()
    elif topic == "command/read_dht":
        log_dht()


async def _water_plant():
    relay_pin.on()
    await asyncio.sleep(WATER_DURATION)
    relay_pin.off()
    mqtt_client.publish("event/hedera-helix/watering", WATER_DURATION)

# Sync wrapper for the async function
def water_plant():
    asyncio.create_task(_water_plant())

def log_moisture():
    moisture = moisture_sensor.read_moisture()
    mqtt_client.publish("sensor/hedera-helix/moisture", str(moisture))

def log_dht():
    temperature, humidity = read_dht(dht_pin)
    mqtt_client.publish("sensor/bedroom/temperature", str(temperature))
    mqtt_client.publish("sensor/bedroom/humidity", str(humidity))

def setup_mqtt() -> mqtt.MQTTClient:
    mqtt_client.connect()
    mqtt_client.set_callback(sub_callback)
    mqtt_client.subscribe("command/hedera-helix/water")
    return mqtt_client

async def main():
    mqtt_client = setup_mqtt()
    create_timed_task(mqtt_client.check_msg, CHECK_MSG_DELAY)
    create_timed_task(log_moisture, WATER_CHECK_DELAY)
    create_timed_task(log_dht, DHT_CHECK_DELAY)
    print("Initialized MQTT client and scheduled tasks.")

    # Let the main loop run indefinitely while everything else
    # runs in the background.
    while True:
        await asyncio.sleep(30)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program interrupted by user.")
