import time
import time
time.sleep(5)
import busio
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

import digitalio
fan = digitalio.DigitalInOut(board.GP16)
fan.direction = digitalio.Direction.OUTPUT

fan.value = False
keyboard = Keyboard(usb_hid.devices)
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.1)
print("pico on")
def send_keypress(input_string):
    input_string = input_string.strip().lower()

    if input_string == "f11":
        keyboard.press(Keycode.F11)
    elif input_string == "pause":
        keyboard.press(Keycode.SPACEBAR)
    elif input_string == "blow":
        fan.value = True
    elif input_string == "suck":
        fan.value = False
    elif input_string == "next_r":
        keyboard.press(Keycode.RIGHT_ARROW)
    elif input_string == "next_l":
        keyboard.press(Keycode.LEFT_ARROW)
    elif input_string == "tab":
        keyboard.press(Keycode.TAB)
    else:
        print(f"Typing: {input_string}")
        for char in input_string:
            if char.isalpha():
                key = getattr(Keycode, char.upper())
                keyboard.press(key)
                time.sleep(0.05)
                keyboard.release(key)
            elif char == " ":
                keyboard.press(Keycode.SPACEBAR)
                time.sleep(0.05)
                keyboard.release(Keycode.SPACEBAR)
            # Optional: add digits and symbols here
    keyboard.release_all()
    time.sleep(0.1)

while True:
    data = uart.readline()
    if data:
        try:
            input_string = data.decode("utf-8")
            send_keypress(input_string)
        except UnicodeDecodeError:
            print("Bad data")
