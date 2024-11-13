import os
import badger2040
from badger2040 import HEIGHT, WIDTH
import badger_os
import jpegdec
import pngdec

# Turn the act LED on as soon as possible
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)

png = pngdec.PNG(display.display)

# Remove state since we're only showing one image
state = {
    "show_info": False
}

def show_badge():
    try:
        png.open_file("/badges/badge.png")
        png.decode()
    except (OSError, RuntimeError) as e:
        display.set_pen(15)
        display.clear()
        display.set_pen(0)
        display.text("Error loading badge", 20, HEIGHT // 2, WIDTH, 1.0)
        print(f"Error: {e}")

    display.update()

# Initial display of the badge
show_badge()

while True:
    # Sometimes a button press or hold will keep the system powered *through* HALT, so latch the power back on.
    display.keepalive()

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
