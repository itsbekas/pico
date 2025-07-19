from machine import Pin, I2C
import time
from lib_pico_i2c_lcd import I2cLcd
import random

FRAMERATE = 0.1
STEP = 25

lcd_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
I2C_ADDR = lcd_i2c.scan()
if not I2C_ADDR:
    raise Exception("I2C address not found. Check your connections.")
I2C_ADDR = I2C_ADDR[0]  # Use the first found address

lcd = I2cLcd(lcd_i2c, I2C_ADDR, 2, 16)

chars = {
    "A": [
        0b11110,
        0b10001,
        0b10001,
        0b11111,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
    ],
    "B": [
        0b11110,
        0b10001,
        0b10001,
        0b11110,
        0b10001,
        0b10001,
        0b10001,
        0b11110,
    ],
    "D": [
        0b11110,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b11110,
    ],
    "E": [
        0b11111,
        0b10000,
        0b10000,
        0b11110,
        0b10000,
        0b10000,
        0b10000,
        0b11111,
    ],
    "N": [
        0b10001,
        0b11001,
        0b10101,
        0b10011,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
    ],
    "O": [
        0b01110,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b10001,
        0b01110,
    ],
    "R": [
        0b11110,
        0b10001,
        0b10001,
        0b11110,
        0b10010,
        0b10001,
        0b10001,
        0b10001,
    ],
}

text = "BERNARDO"

# Map the characters to a custom char.
# TODO: Handle max character limit of the LCD (8)
char_map = {
    letter: i
    for i, letter in enumerate(set(text))
}

# Starting point for the custom chars
state = {
    char: [0] * 8
    for char in char_map
}

# Get the bits for each character
bits = {
    char: [
        (x, y)
        for x in range(8)
        for y in range(5)
        if (chars[char][x] & (1 << y)) != 0
    ]
    for char in char_map
}

def shuffle(array):
    "Fisher-Yates shuffle"
    for i in range(len(array)-1, 0, -1):
        j = random.randrange(i+1)
        array[i], array[j] = array[j], array[i]

bit_list = [
    (char, x, y)
    for char, bit_list in bits.items()
    for x, y in bit_list
]

shuffle(bit_list)

# Initialize the custom characters
for char in char_map:
    lcd.clear()
    lcd.custom_char(char_map[char], state[char])

for char in text:
    lcd.putchar(chr(char_map[char]))

changed = []
for i, bit in enumerate(bit_list):
    char, x, y = bit
    state[char][x] |= (1 << y)
    if char not in changed:
        changed.append(char)
    if i % STEP == 0:
        for c in changed:
            lcd.custom_char(char_map[c], state[c])
        changed = []
        time.sleep(FRAMERATE)

for c in changed:
    lcd.custom_char(char_map[c], state[c])