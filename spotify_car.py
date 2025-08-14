import uasyncio
import urequests
import time
import random
import network
from machine import Pin

import time
import json

from blib_lcd import get_lcd, TextScroller, DoubleTextScroller
from secrets import SSID, PASSWORD
from spotify_secrets import SPOTIFY_CAR_BASE_URL, SPOTIFY_CAR_ID
import os
import blib_chars as chars

SPOTIFY_ACCESS_TOKEN_FILE = ".spotify_access_token"
SPOTIFY_REFRESH_TOKEN_FILE = ".spotify_refresh_token"

MUSIC_CHAR = 0
USER_CHAR = 1
PAUSE_CHAR = 2

lcd = get_lcd(1, 0, custom_chars={MUSIC_CHAR: chars.music, USER_CHAR: chars.user, PAUSE_CHAR: chars.pause})  # SCL=1, SDA=0

pico_id = SPOTIFY_CAR_ID
session_hash = random.randint(0, 9999999)
button = Pin(16, Pin.IN, Pin.PULL_UP)


def setup_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.config(pm = 0xa11140)
    wlan.active(True)

    return wlan


def connect_wifi(wlan, ssid, password):
    retries = 21

    lcd.clear()
    lcd.move_to(3, 0)
    lcd.putstr("Connecting")
    lcd.move_to(3, 1)
    lcd.putstr("to WiFi...")
    wlan.connect(ssid, password)

    while not wlan.isconnected() and retries > 0:
        retries -= 1
        time.sleep(1)
        lcd.move_to(10, 1)
        lcd.putstr("." * (3 - retries % 3) + "  ")
        print("Status:", wlan.status())

    if not wlan.isconnected():
        print("Failed to connect to WiFi")
        lcd.clear()
        lcd.putstr("Can't connect")
        ts = TextScroller(lcd, "Press play to retry", row=1)
        ts.start()
        while True:
            ts.next()
            time.sleep(0.2)
            if not button.value():
                connect_wifi(wlan, ssid, password)
                return


def register_pico():
    lcd.clear()
    lcd.putstr("Registering your car...")
    res = urequests.post(
        f"{SPOTIFY_CAR_BASE_URL}/register?pico_id={pico_id}&session_hash={session_hash}"
    )

    if res.status_code != 200:
        print("Failed to register pico")
        print("Status code:", res.status_code)
        print("Response:", res.text)
        lcd.clear()
        lcd.putstr("Register failed")
        ts = TextScroller(lcd, "Press play to retry", row=1)
        ts.start()
        while True:
            ts.next()
            time.sleep(0.2)
            if not button.value():
                register_pico()
                return
    else:
        lcd.clear()
        ts = TextScroller(lcd, "Tap your phone on the device and login to proceed. When done, press play.", row=0)
        ts.start()
        while True:
            ts.next()
            time.sleep(0.2)
            if not button.value():
                return

def get_token():
    res = urequests.get(
        f"{SPOTIFY_CAR_BASE_URL}/token?pico_id={pico_id}&session_hash={session_hash}"
    )

    if res.status_code != 200:
        print("Failed to register pico")
        print("Status code:", res.status_code)
        print("Response:", res.text)
        lcd.clear()
        ts0 = TextScroller(lcd, "Token failed", row=0)
        ts1 = TextScroller(lcd, "Press play to retry", row=1)
        ts0.start()
        ts1.start()
        while True:
            ts0.next()
            ts1.next()
            time.sleep(0.2)
            if not button.value():
                get_token()
                return
    else:
        lcd.clear()
        lcd.putstr("Token received! Setup complete")
        print(res.text)
        json_data = json.loads(res.text)
        with open(SPOTIFY_ACCESS_TOKEN_FILE, "w") as f:
            f.write(json_data.get("access_token", "").strip())
        with open(SPOTIFY_REFRESH_TOKEN_FILE, "w") as f:
            f.write(json_data.get("refresh_token", "").strip())

def refresh_token():
    with open(SPOTIFY_REFRESH_TOKEN_FILE, "r") as f:
        refresh_token = f.read().strip()
    
    print(refresh_token)

    res = urequests.get(
        f"{SPOTIFY_CAR_BASE_URL}/refresh?refresh_token={refresh_token}"
    )

    if res.status_code != 200:
        print("Failed to refresh token")
        print("Status code:", res.status_code)
        print("Response:", res.text)
        return None
    else:
        json_data = json.loads(res.text)

        access_token = json_data.get("access_token", "").strip()
        with open(SPOTIFY_ACCESS_TOKEN_FILE, "w") as f:
            f.write(access_token)

        refresh_token = json_data.get("refresh_token", "").strip()
        if refresh_token:
            with open(SPOTIFY_REFRESH_TOKEN_FILE, "w") as f:
                f.write(json_data.get("refresh_token", "").strip())

        return access_token

def read_token():
    # read .spotify_token file. if it doesn't exist, return None
    if SPOTIFY_ACCESS_TOKEN_FILE not in os.listdir():
        return None
    
    with open(SPOTIFY_ACCESS_TOKEN_FILE, "r") as f:
        token = f.read().strip()
    return token

def get_current_track(token):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    res = urequests.get(
        f"https://api.spotify.com/v1/me/player/currently-playing",
        headers=headers
    )

    if res.status_code == 204:
        print("No track is currently playing")
        return None, False
    if res.status_code == 401:
        print("Token expired, refreshing...")
        token = refresh_token()
        if not token:
            return None, False
        return get_current_track(token)
    elif res.status_code != 200:
        print("Failed to get current track")
        print("Status code:", res.status_code)
        print("Response:", res.text)
        return None, False
    else:
        data = res.json()
        if not data or "item" not in data:
            print("No track is currently playing")
            return None, False
        return data["item"], data["is_playing"]

async def start_spotify(token):
    DELAY = 1

    ts = DoubleTextScroller(lcd, "", "", prefix_top=chr(MUSIC_CHAR) + " ", prefix_bottom=chr(USER_CHAR) + " ", delay=100)
    ts.start()
    _track = None
    _is_playing = True

    while True:
        track, is_playing = get_current_track(token)

        if _track and track and _track['id'] == track['id']:
            if _is_playing != is_playing:
                _is_playing = is_playing
                if is_playing:
                    ts.change_prefix(0, chr(MUSIC_CHAR) + " ")
                else:
                    ts.change_prefix(0, chr(PAUSE_CHAR) + " ")
            print("Track is still playing, waiting for next update...")
            await uasyncio.sleep(DELAY)
            continue

        if track:
            ts.change_text(0, track['name'])
            ts.change_text(1, ", ".join(artist['name'] for artist in track['artists']))
            print(f"Playing: {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
        else:
            ts.stop()
            lcd.clear()
            lcd.putstr("No track playing")
            print("No track playing")
        
        _track = track

        await uasyncio.sleep(DELAY)


async def _main():
    wlan = setup_wlan()
    connect_wifi(wlan, SSID, PASSWORD)

    if token := read_token():
        lcd.clear()
        lcd.putstr("Play anything to start")
    else:
        register_pico()
        token = get_token()
    
    await start_spotify(token)

def main():
    try:
        uasyncio.run(_main())
    except KeyboardInterrupt:
        print("Exiting...")
        lcd.clear()
        lcd.putstr("Exiting...")
        time.sleep(1)
        lcd.clear()

if __name__ == "__main__":
    main()
