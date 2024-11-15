import os
import badger2040
from badger2040 import HEIGHT, WIDTH
import badger_os
import jpegdec
import pngdec


TOTAL_IMAGES = 0


# Turn the act LED on as soon as possible
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)

jpeg = jpegdec.JPEG(display.display)
png = pngdec.PNG(display.display)


# Load images from /images
try:
    IMAGES = [f for f in os.listdir("/images") if f.endswith(".jpg") or f.endswith(".png")]
    TOTAL_IMAGES = len(IMAGES)
except OSError:
    pass


state = {
    "current_image": 0,
    "show_info": False #start with show_info Off until Button_A is pressed
}


def show_image(n):
    file = IMAGES[n]
    name, ext = file.split(".")

    try:
        png.open_file("/images/{}".format(file))
        png.decode()
    except (OSError, RuntimeError):
        jpeg.open_file("/images/{}".format(file))
        jpeg.decode()

    if state["show_info"]:
        label = f"{name} ({ext})"
        name_length = display.measure_text(label, 0.5)
        display.set_pen(0)
        display.rectangle(0, HEIGHT - 21, name_length + 11, 21)
        display.set_pen(15)
        display.rectangle(0, HEIGHT - 20, name_length + 10, 20)
        display.set_pen(0)
        display.text(label, 5, HEIGHT - 10, WIDTH, 0.5)

        for i in range(TOTAL_IMAGES):
            x = 286
            y = int((128 / 2) - (TOTAL_IMAGES * 10 / 2) + (i * 10))
            display.set_pen(0)
            display.rectangle(x, y, 8, 8)
            if state["current_image"] != i:
                display.set_pen(15)
                display.rectangle(x + 1, y + 1, 6, 6)

    display.update()


if TOTAL_IMAGES == 0:
    raise RuntimeError("To run this demo, upload some 1bit 296x128 pixel images to the /images directory.")


badger_os.state_load("image", state)

changed = True


while True:
    # Sometimes a button press or hold will keep the system powered *through* HALT, so latch the power back on.
    display.keepalive()

    if display.pressed(badger2040.BUTTON_UP):
        state["current_image"] = (state["current_image"] - 1)
        if state["current_image"] < 0:
            state["current_image"] = TOTAL_IMAGES - 1
        changed = True

    if display.pressed(badger2040.BUTTON_DOWN):
        state["current_image"] = (state["current_image"] + 1)
        if state["current_image"] >= TOTAL_IMAGES:
            state["current_image"] = 0
        changed = True

    if display.pressed(badger2040.BUTTON_A):
        state["show_info"] = not state["show_info"]
        changed = True

    if changed:
        show_image(state["current_image"])
        badger_os.state_save("image", state)
        changed = False

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
