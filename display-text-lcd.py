from machine import Pin, I2C
import time
from lib_pico_i2c_lcd import I2cLcd


lcd_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
I2C_ADDR = lcd_i2c.scan()
if not I2C_ADDR:
    raise Exception("I2C address not found. Check your connections.")
I2C_ADDR = I2C_ADDR[0]  # Use the first found address

lcd = I2cLcd(lcd_i2c, I2C_ADDR, 2, 16)

lcd.putchar(chr(247))

# lcd.display_on()
# lcd.clear()
# lcd.putstr("Hello, World!\n")