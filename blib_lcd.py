import time
import uasyncio
from machine import Pin, I2C
from lib_pico_i2c_lcd import I2cLcd

def get_lcd(scl_pin, sda_pin, id=0, freq=400000, custom_chars={}):
    i2c = I2C(id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
    i2c_addr = i2c.scan()
    if not i2c_addr:
        raise Exception("I2C address not found. Check your connections.")
    i2c_addr = i2c_addr[0]  # Use the first found address
    lcd = I2cLcd(i2c, i2c_addr, 2, 16)
    for char_index, char in custom_chars.items():
        lcd.custom_char(char_index, char)
    return lcd

class TextScroller:
    def __init__(self, lcd, text, prefix="", row=0):
        self.lcd = lcd
        self.original_text = text
        self.text = text
        self.prefix = prefix
        self.row = row

        self.prefix_len = len(prefix)
        self.step = 0
        self.size = lcd.num_columns - self.prefix_len
    
    def start(self):
        self.lcd.move_to(0, self.row)
        self.lcd.putstr(self.prefix)
        self.lcd.putstr(self.text[:self.size])

    def next(self):
        self.lcd.move_to(self.prefix_len, self.row)
        if self.step % self.size == 0:
            self.text += " " * 5 + self.original_text
        
        self.lcd.putstr(self.text[:self.size])
        self.text = self.text[1:]
        self.step += 1

def locked(func):
    def wrapper(self, *args, **kwargs):
        was_stopped = self._stop
        if not was_stopped:
            self.stop()
        result = func(self, *args, **kwargs)
        if not was_stopped:
            self.resume()
        return result
    return wrapper

class DoubleTextScroller:
    _stop = False
    _task = None

    def __init__(self, lcd, text_top, text_bottom, prefix_top="", prefix_bottom="", delay=200):
        self.lcd = lcd
        self.original_text = [text_top, text_bottom]
        self.text = [text_top, text_bottom]
        self.prefix = [prefix_top, prefix_bottom]
        self.delay = delay

        self.prefix_len = [len(prefix_top), len(prefix_bottom)]
        self.size = [lcd.num_columns - len(prefix_top), lcd.num_columns - len(prefix_bottom)]

        self.scroll_index = [0, 0]
        self.pause_counter = [0, 0]
    
    def initialize(self):
        self.lcd.clear()
        for i in range(2):
            self.lcd.move_to(0, i)
            self.lcd.putstr(self.prefix[i])
            self.lcd.putstr(self.text[i][:self.size[i]])

    def start(self):
        self._task = uasyncio.create_task(self.run())    

    async def run(self):
        self.initialize()
        while True:
            self.next()
            await uasyncio.sleep_ms(self.delay)
    
    def stop(self):
        self._stop = True
    
    def resume(self):
        self._stop = False

    def next(self):
        if self._stop:
            print("Scroller is stopped, not updating text.")
            return

        for i in range(2):
            if len(self.original_text[i]) <= self.size[i]:
                continue

            if self.pause_counter[i] > 0:
                print(f"Row {i} is paused for {self.pause_counter[i]} more iterations.")
                self.pause_counter[i] -= 1
                continue

            if (self.scroll_index[i] - 5) == len(self.original_text[i]):
                self.scroll_index[i] = 0
                self.pause_counter[i] = 40

            self.lcd.move_to(self.prefix_len[i], i)
            if len(self.text[i]) == self.size[i]:
                self.text[i] += " " * 5 + self.original_text[i]

            self.lcd.putstr(self.text[i][:self.size[i]])
            self.text[i] = self.text[i][1:]

            self.scroll_index[i] += 1

    @locked
    def change_prefix(self, row, new_prefix):
        if row < 0 or row >= len(self.prefix):
            raise ValueError("Row index out of range")
    
        self.prefix[row] = new_prefix
        self.lcd.move_to(0, row)
        self.lcd.putstr(new_prefix)

    @locked
    def change_text(self, row, new_text):
        if row < 0 or row >= len(self.text):
            raise ValueError("Row index out of range")

        self.original_text[row] = new_text
        self.text[row] = new_text
        self.lcd.move_to(len(self.prefix[row]), row)
        self.lcd.putstr(self.text[row][:self.size[row]] + " " * (self.size[row] - len(self.text[row])))
