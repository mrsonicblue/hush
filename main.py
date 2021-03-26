import adafruit_dotstar
import board
import digitalio
import rotaryio
import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# dot = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.05)

# Keyboard emulation
kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# Reset button
reset_button = digitalio.DigitalInOut(board.D4)
reset_button.direction = digitalio.Direction.INPUT
reset_button.pull = digitalio.Pull.UP

# User button
user_button = digitalio.DigitalInOut(board.D3)
user_button.direction = digitalio.Direction.INPUT
user_button.pull = digitalio.Pull.UP

# Mute button
mute_button = digitalio.DigitalInOut(board.D0)
mute_button.direction = digitalio.Direction.INPUT
mute_button.pull = digitalio.Pull.UP

# Volume knob
encoder = rotaryio.IncrementalEncoder(board.D2, board.D1)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return (0, 0, 0)
    if (pos > 255):
        return (0, 0, 0)
    if (pos < 85):
        return (int(pos * 3), int(255 - (pos * 3)), 0)
    elif (pos < 170):
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

color_pos = 0
mute_button_pressed = False
user_button_pressed = False
reset_button_pressed = False
last_position = encoder.position

while True:
    if mute_button_pressed:
        if mute_button.value:
            mute_button_pressed = False
    else:
        if not mute_button.value:
            cc.send(ConsumerControlCode.MUTE)
            mute_button_pressed = True

    if user_button_pressed:
        if user_button.value:
            kbd.release(Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.RIGHT_ALT)
            user_button_pressed = False
    else:
        if not user_button.value:
            kbd.press(Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.RIGHT_ALT)
            user_button_pressed = True

    if reset_button_pressed:
        if reset_button.value:
            kbd.release(Keycode.LEFT_SHIFT, Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.RIGHT_ALT)
            reset_button_pressed = False
    else:
        if not reset_button.value:
            kbd.press(Keycode.LEFT_SHIFT, Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.RIGHT_ALT)
            reset_button_pressed = True

    # dot[0] = wheel(color_pos)
    # color_pos = (color_pos + 1) % 256

    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        print(current_position)
    elif position_change < 0:
        for _ in range(-position_change):
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        print(current_position)
    last_position = current_position
  
    time.sleep(0.01)