import badger2040
import time
import os

# Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

# Initialize display
display = badger2040.Badger2040()
display.led(128)

# Create /images directory if it doesn't exist
try:
    os.mkdir("/images")
except OSError:
    pass

def write_bitmap_file(filename):
    """Write a 1-bit bitmap file"""
    # Bitmap file header (14 bytes)
    file_header = bytearray([
        0x42, 0x4D,           # Signature 'BM'
        0x3E, 0x0E, 0x00, 0x00,  # File size (3646 bytes for 296x128 1-bit)
        0x00, 0x00,           # Reserved
        0x00, 0x00,           # Reserved
        0x3E, 0x00, 0x00, 0x00   # Pixel data offset (62 bytes)
    ])
    
    # Bitmap info header (40 bytes)
    info_header = bytearray([
        0x28, 0x00, 0x00, 0x00,  # Header size (40 bytes)
        0x28, 0x01, 0x00, 0x00,  # Width (296 pixels)
        0x80, 0x00, 0x00, 0x00,  # Height (128 pixels)
        0x01, 0x00,           # Planes (1)
        0x01, 0x00,           # Bits per pixel (1)
        0x00, 0x00, 0x00, 0x00,  # Compression (none)
        0x00, 0x0E, 0x00, 0x00,  # Image size (3584 bytes)
        0x00, 0x00, 0x00, 0x00,  # X pixels per meter
        0x00, 0x00, 0x00, 0x00,  # Y pixels per meter
        0x02, 0x00, 0x00, 0x00,  # Colors used (2)
        0x02, 0x00, 0x00, 0x00   # Important colors (2)
    ])
    
    # Color table (8 bytes)
    color_table = bytearray([
        0xFF, 0xFF, 0xFF, 0x00,  # White
        0x00, 0x00, 0x00, 0x00   # Black
    ])
    
    try:
        with open(filename, 'wb') as f:
            # Write headers
            f.write(file_header)
            f.write(info_header)
            f.write(color_table)
            
            # Write pixel data (1 bit per pixel, padded to 4 bytes per row)
            row_size = ((WIDTH + 31) // 32) * 4  # Round up to nearest 4 bytes
            
            # Create temporary buffer for the row
            row = bytearray(row_size)
            
            # Read display content pixel by pixel
            for y in range(HEIGHT - 1, -1, -1):  # BMP is bottom-up
                # Clear row buffer
                for i in range(row_size):
                    row[i] = 0
                    
                # Read one row of pixels
                for x in range(WIDTH):
                    # Test pixel by drawing a small dot
                    old_pen = display.pen
                    display.set_pen(0)  # Black pen
                    display.pixel(x, y)
                    is_black = (display.pen == 0)  # If pen is still 0, pixel was white
                    display.set_pen(old_pen)
                    
                    # Set bit in row buffer if pixel was black
                    if is_black:
                        row[x // 8] |= (0x80 >> (x % 8))
                
                # Write row to file
                f.write(row)
                
        return True
    except Exception as e:
        print(f"Bitmap write error: {e}")
        return False

def take_screenshot():
    try:
        # Generate timestamp for unique filename
        timestamp = time.time()
        filename = f"/images/screen_{int(timestamp)}.bmp"
        
        # Update display to ensure buffer is current
        display.update()
        
        if write_bitmap_file(filename):
            # Flash LED for feedback
            curr_led = display.led()
            for _ in range(3):
                display.led(0)
                time.sleep(0.1)
                display.led(128)
                time.sleep(0.1)
            display.led(curr_led)
            
            # Show success message
            display.set_pen(15)
            display.rectangle(10, HEIGHT - 40, WIDTH - 20, 30)
            display.set_pen(0)
            display.text(f"Saved: {filename}", 20, HEIGHT - 30, WIDTH, 0.5)
            display.update()
            time.sleep(1)
        else:
            raise Exception("Failed to write bitmap")
            
    except Exception as e:
        print(f"Screenshot error: {e}")
        # Show error message
        display.set_pen(15)
        display.rectangle(10, HEIGHT - 40, WIDTH - 20, 30)
        display.set_pen(0)
        display.text("Screenshot failed!", 20, HEIGHT - 30, WIDTH, 0.5)
        display.update()
        time.sleep(2)
    
    finally:
        # Redraw UI
        draw_ui()

def draw_ui():
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    
    # Draw title
    display.set_font("bitmap8")
    display.text("Screenshot Utility", 10, 20, WIDTH, 1)
    
    # Draw instructions
    display.set_font("sans")
    display.text("Press B + UP to take a screenshot", 10, 50, WIDTH, 0.6)
    display.text("Screenshots save to /images", 10, 70, WIDTH, 0.6)
    display.text("LED will flash when complete", 10, 90, WIDTH, 0.6)
    
    display.update()

# Initial UI draw
draw_ui()

while True:
    display.keepalive()
    
    if display.pressed(badger2040.BUTTON_B) and display.pressed(badger2040.BUTTON_UP):
        take_screenshot()
        # Wait for buttons to be released
        while display.pressed(badger2040.BUTTON_B) or display.pressed(badger2040.BUTTON_UP):
            time.sleep(0.1)
    
    # Halt the Badger to save power
    display.halt()