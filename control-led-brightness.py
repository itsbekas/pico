from machine import Pin, PWM
import time

LED_PIN = 0
led = Pin(LED_PIN, Pin.OUT)
led.value(0)
pwm = PWM(led)
pwm.freq(1000)

def dim_led_smoothly():
    # Fade in (0 to 65535, 16-bit resolution)
    for duty_cycle in range(0, 65536, 128): # Step by 128 for a smoother but faster fade
        pwm.duty_u16(duty_cycle)
        time.sleep(0.005) # Small delay for visual effect

    # Fade out
    for duty_cycle in range(65535, -1, -128): # Step down
        pwm.duty_u16(duty_cycle)
        time.sleep(0.005)


while True:
    print("Fading LED...")
    dim_led_smoothly()
    time.sleep(1) # Wait a bit before repeating
