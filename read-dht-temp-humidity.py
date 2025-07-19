import dht
from machine import Pin
import time

dht_sensor_pin = Pin(20)
dht_sensor = dht.DHT22(dht_sensor_pin)

time.sleep(2)

dht_sensor.measure()
temperature = dht_sensor.temperature()
humidity = dht_sensor.humidity()

print("Temperature: {:.1f}C".format(temperature))
print("Humidity: {:.1f}%".format(humidity))
