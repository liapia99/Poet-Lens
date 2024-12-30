import RPi.GPIO as GPIO
import time
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import ST7735
import spidev

# Setup GPIO for rotary encoder
pinCLK = 17
pinDT = 18
pinSW = 1

# Initialize the TFT display
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 4000000

# Initialize the TFT screen (ST7735)
disp = ST7735.ST7735(spi=spi, width=240, height=320, rotate=90)
disp.begin()

# Create a Pillow image object for drawing on TFT
image = Image.new("RGB", (240, 320), color=(255, 255, 255))  # White background
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Draw initial background and text
draw.text((10, 10), "Rotary Encoder GUI", font=font, fill=(0, 0, 0))  # Title text

# Define the number of buttons
num_buttons = 5
button_names = [f"Button {i+1}" for i in range(num_buttons)]

# Create a simple Tkinter window for the main monitor
root = tk.Tk()
root.title("Rotary Encoder Button Selector")

# Button callback for the main monitor's GUI
def button_action(button_idx):
    print(f"Selected {button_names[button_idx]}")

# Create Tkinter buttons for main screen
buttons = []
default_bg_color = "lightgray"
highlight_bg_color = "lightblue"

for i in range(num_buttons):
    btn = tk.Button(root, text=button_names[i], width=20, bg=default_bg_color, command=lambda idx=i: button_action(idx))
    btn.grid(row=i, column=0)
    buttons.append(btn)

# Function to draw on the TFT screen
def update_tft_gui(encoder_pos):
    # Clear the TFT screen
    draw.rectangle((0, 0, 240, 320), outline=(255, 255, 255), fill=(255, 255, 255))
    
    # Draw the current button names and highlight the selected one
    for i in range(num_buttons):
        y_position = 40 + i * 50
        text = button_names[i]
        if i == encoder_pos:
            draw.rectangle((0, y_position, 240, y_position + 40), outline=(0, 0, 0), fill=(173, 216, 230))  # Highlight color
        draw.text((10, y_position), text, font=font, fill=(0, 0, 0))
    
    # Display the image on the TFT
    disp.display(image)

# Initialize the lastCLK for rotary encoder
lastCLK = GPIO.input(pinCLK)

# Function to read the encoder
def read_encoder():
    global encoder_pos, lastCLK
    currentCLK = GPIO.input(pinCLK)
    
    if currentCLK != lastCLK:
        if GPIO.input(pinDT) != currentCLK:
            encoder_pos += 1
        else:
            encoder_pos -= 1
    lastCLK = currentCLK

# Main loop to handle both GUI and encoder
encoder_pos = 0

try:
    while True:
        # Read the encoder position
        read_encoder()
        
        # Update the TFT GUI with the selected position
        update_tft_gui(encoder_pos)

        # Handle button presses on the main GUI
        if GPIO.input(pinSW) == GPIO.LOW:
            button_action(encoder_pos)
            while GPIO.input(pinSW) == GPIO.LOW:
                time.sleep(0.01)

        # Update Tkinter window for the main monitor
        root.update()

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()
    root.quit()
