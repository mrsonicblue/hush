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

dot = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.05)

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

button = digitalio.DigitalInOut(board.D4)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Rotary encoder inputs with pullup on D1 & D2
encoder = rotaryio.IncrementalEncoder(board.D1, board.D2)

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
button_pressed = False
last_position = encoder.position

while True:
    #kbd.send(Keycode.SHIFT, Keycode.K)

    if button_pressed:
        if button.value:
            print("Button released!")
            button_pressed = False
    else:
        if not button.value:
            print("Button pressed!")
            cc.send(ConsumerControlCode.MUTE)
            button_pressed = True

    dot[0] = wheel(color_pos)
    color_pos = (color_pos + 1) % 256

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
  
    time.sleep(0.05)