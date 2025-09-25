import os, time, signal, socket
from gpiozero import LED, Button, RotaryEncoder
from PIL import Image, ImageDraw, ImageFont
import ST7789  # pip install st7789

#########################
# GPIO Setup
#########################
# LEDs
led_shutter = LED(5)   # LED for shutter press
led_wifi = LED(6)      # LED for WiFi status

# Shutter button
shutter_button = Button(16, hold_time=2)

# Rotary encoder with push
# (Adjust pins to your wiring)
rotary = RotaryEncoder(a=20, b=21, max_steps=7)  
rotary_button = Button(26)

#########################
# LCD Setup (ST7789)
#########################
# Create ST7789 display instance
disp = ST7789.ST7789(
    height=240,
    width=240,
    rotation=180,
    port=0,
    cs=0,
    dc=25,
    backlight=24,
    spi_speed_hz=80 * 1000 * 1000
)
disp.begin()

# Pillow setup
image = Image.new("RGB", (240, 240), "black")
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def lcd_message(text, clear=True):
    """Write message to LCD."""
    global image, draw
    if clear:
        draw.rectangle((0, 0, 240, 240), outline=0, fill=0)
    draw.text((10, 120), text, font=font, fill=(255, 255, 255))
    disp.display(image)

#########################
# Functions
#########################
def check_wifi():
    """Return True if Pi is connected to WiFi."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def update_wifi_led():
    """Update WiFi LED status."""
    if check_wifi():
        led_wifi.on()
        lcd_message("WiFi: Connected")
    else:
        led_wifi.off()
        lcd_message("WiFi: Not Connected")

def handle_pressed():
    print("Shutter pressed")
    led_shutter.on()
    lcd_message("Shutter Pressed")

def handle_held():
    print("Shutter held")
    lcd_message("Shutter Held")

def handle_released():
    print("Shutter released")
    led_shutter.off()
    lcd_message("Shutter Released")

def handle_rotary_change():
    """Show rotary position (0–7)."""
    pos = rotary.steps
    print(f"Rotary: {pos}")
    lcd_message(f"Option {pos}")

def handle_rotary_button():
    """Confirm rotary option."""
    pos = rotary.steps
    print(f"Rotary button pressed -> Option {pos}")
    lcd_message(f"Selected {pos}")

def handle_keyboard_interrupt(sig, frame):
    print("Ctrl+C received, stopping script")
    led_shutter.off()
    led_wifi.off()
    lcd_message("Exiting...")
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGUSR1)

#########################
# Event bindings
#########################
shutter_button.when_pressed = handle_pressed
shutter_button.when_held = handle_held
shutter_button.when_released = handle_released

rotary.when_rotated = handle_rotary_change
rotary_button.when_pressed = handle_rotary_button

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

#########################
# Main Loop
#########################
lcd_message("System Start", clear=True)
time.sleep(1)

while True:
    update_wifi_led()
    time.sleep(5)  # check wifi every 5 seconds
