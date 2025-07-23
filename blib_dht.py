import dht

def read_dht(sensor: dht.DHT22) -> tuple:
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    return temperature, humidity