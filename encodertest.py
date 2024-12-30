from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont

# Initialize the TFT display
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, gpio_BACKLIGHT=18)
device = st7735(serial, width=128, height=160)

# Create a blank image for the display
image = Image.new("RGB", (128, 160), "black")  # Black background
draw = ImageDraw.Draw(image)

# Load a font (use a default PIL font or custom font)
font = ImageFont.load_default()

# Define text and color
text = "Julia"
text_color = (255, 182, 193)  # Light pink (RGB)

# Get the text size to center it
text_width, text_height = draw.textsize(text, font=font)
x = (128 - text_width) // 2  # Center horizontally
y = (160 - text_height) // 2  # Center vertically

# Draw the text on the image
draw.text((x, y), text, fill=text_color, font=font)

# Display the image on the TFT
device.display(image)
