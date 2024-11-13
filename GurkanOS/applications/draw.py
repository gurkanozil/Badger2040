import badger2040
import badger_os
import time
#import struct
import os

# Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

# Initialize display
display = badger2040.Badger2040()
display.led(128)

# App state
state = {
    "cursor_x": WIDTH // 2,
    "cursor_y": HEIGHT // 2,
    "brush_size": 2,
    "mode": "vertical",  # vertical or horizontal movement
    "show_ui": True,
    "drawing": False,    # New state to track if we're drawing
    "save_count": 0
}

# Load previous state and get latest save number
badger_os.state_load("draw", state)
try:
    existing_files = [f for f in os.listdir("/images") if f.startswith("drawing") and f.endswith(".png")]
    if existing_files:
        last_num = max([int(f.split("_")[1].split(".")[0]) for f in existing_files])
        state["save_count"] = last_num + 1
except OSError:
    pass

def draw_cursor():
    if state["drawing"]:  # Don't show cursor while drawing
        return
        
    display.set_update_speed(badger2040.UPDATE_FAST)
    
    # Clear previous cursor area with a tiny region
    display.set_pen(15)  # White
    display.rectangle(
        max(0, state["cursor_x"] - 4),
        max(0, state["cursor_y"] - 4),
        8, 8
    )
    
    # Draw new cursor (just a small plus)
    display.set_pen(0)  # Black
    x, y = state["cursor_x"], state["cursor_y"]
    display.line(x - 2, y, x + 2, y)
    display.line(x, y - 2, x, y + 2)
    
    # Update tiny cursor area
    display.partial_update(
        max(0, x - 4),
        max(0, y - 4),
        8, 8
    )

def draw_ui():
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(15)  # White
    display.clear()
    display.set_pen(0)   # Black
    
    # Draw instructions
    display.text("Drawing App", 5, 5, WIDTH, 1)
    display.text("A: Draw/Toggle UI", 5, HEIGHT - 60, WIDTH, 0.6)
    display.text("B: " + state["mode"].upper(), 5, HEIGHT - 45, WIDTH, 0.6)
    display.text("C: Size " + str(state["brush_size"]), 5, HEIGHT - 30, WIDTH, 0.6)
    display.text("UP/DOWN: Move", 5, HEIGHT - 15, WIDTH, 0.6)
    
    display.update()

def draw_point():
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(0)  # Black
    x, y = state["cursor_x"], state["cursor_y"]
    size = state["brush_size"]
    
    # Draw filled circle at cursor position
    display.circle(x, y, size)
    
    # Update only the drawn area
    display.partial_update(
        max(0, x - size - 1),
        max(0, y - size - 1),
        (size + 1) * 2,
        (size + 1) * 2
    )

def save_drawing():
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    
    filename = f"/images/drawing_{state['save_count']}.png"
    try:
        # First invert the display buffer since we want white background
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pixel = display.pixel(x, y)
                display.pixel(x, y, 15 - pixel)  # Invert pixel value
        
        # Save the current display buffer
        display.save(filename)
        
        # Invert back to original state
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pixel = display.pixel(x, y)
                display.pixel(x, y, 15 - pixel)
        
        state["save_count"] += 1
        
        # Show save confirmation
        display.set_pen(15)
        display.rectangle(WIDTH//4, HEIGHT//3, WIDTH//2, 30)
        display.set_pen(0)
        display.text(f"Saved as {filename}", WIDTH//4 + 5, HEIGHT//3 + 10, WIDTH, 0.6)
        display.update()
        time.sleep(1)
        
        # Restore previous state
        if state["show_ui"]:
            draw_ui()
        else:
            display.set_pen(15)
            display.rectangle(WIDTH//4, HEIGHT//3, WIDTH//2, 30)
            display.update()
            
    except OSError as e:
        # Show error
        display.set_pen(15)
        display.rectangle(WIDTH//4, HEIGHT//3, WIDTH//2, 30)
        display.set_pen(0)
        display.text("Save failed!", WIDTH//4 + 5, HEIGHT//3 + 10, WIDTH, 0.6)
        display.update()
        time.sleep(1)

def handle_input():
    move_speed = 3
    
    # Check for save combination (B + UP)
    b_pressed = display.pressed(badger2040.BUTTON_B)
    up_pressed = display.pressed(badger2040.BUTTON_UP)
    if b_pressed and up_pressed:
        save_drawing()
        return True
        
    if display.pressed(badger2040.BUTTON_UP):
        if state["mode"] == "vertical":
            state["cursor_y"] = max(0, state["cursor_y"] - move_speed)
        else:
            state["cursor_x"] = min(WIDTH, state["cursor_x"] + move_speed)
        state["drawing"] = False  # Not drawing while moving
        draw_cursor()
        return True
        
    if display.pressed(badger2040.BUTTON_DOWN):
        if state["mode"] == "vertical":
            state["cursor_y"] = min(HEIGHT, state["cursor_y"] + move_speed)
        else:
            state["cursor_x"] = max(0, state["cursor_x"] - move_speed)
        state["drawing"] = False  # Not drawing while moving
        draw_cursor()
        return True
        
    if display.pressed(badger2040.BUTTON_A):
        if display.pressed(badger2040.BUTTON_UP):  # Clear screen if A+UP pressed
            state["drawing"] = False
            draw_ui()
        else:
            if state["show_ui"]:  # Toggle UI visibility
                state["show_ui"] = False
                draw_ui()
            state["drawing"] = True  # Now drawing
            draw_point()
        return True
        
    if display.pressed(badger2040.BUTTON_B):
        state["mode"] = "horizontal" if state["mode"] == "vertical" else "vertical"
        if state["show_ui"]:
            draw_ui()
        return True
        
    if display.pressed(badger2040.BUTTON_C):
        state["brush_size"] = (state["brush_size"] % 5) + 1
        if state["show_ui"]:
            draw_ui()
        return True
    
    return False

# Initial draw
draw_ui()

while True:
    display.keepalive()
    
    if handle_input():
        badger_os.state_save("draw", state)
    
    display.halt()