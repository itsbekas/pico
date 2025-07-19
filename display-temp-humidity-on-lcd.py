import dht
from machine import Pin, I2C
import time
from lib_pico_i2c_lcd import I2cLcd

dht_sensor_pin = Pin(15)
dht_sensor = dht.DHT22(dht_sensor_pin)

lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = lcd_i2c.scan()
if not I2C_ADDR:
    raise Exception("I2C address not found. Check your connections.")
I2C_ADDR = I2C_ADDR[0]  # Use the first found address

lcd = I2cLcd(lcd_i2c, I2C_ADDR, 2, 16)

def read_dht_sensor():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print("Error reading DHT sensor:", e)
        return None, None

def main():
    while True:
        temperature, humidity = read_dht_sensor()
        if temperature is not None and humidity is not None:
            lcd.clear()
            lcd.putstr("Temp: {:.1f}C\n".format(temperature))
            lcd.putstr("Humidity: {:.1f}%".format(humidity))
        time.sleep(2)

if __name__ == "__main__":
    main()
