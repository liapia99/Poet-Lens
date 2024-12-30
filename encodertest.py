from PIL import Image, ImageDraw, ImageFont
import ST7735

# Initialize the TFT display
disp = ST7735.ST7735(
    port=0,          # SPI port
    cs=0,            # Chip-select pin
    dc=24,           # Data/Command pin
    backlight=18,    # Backlight pin
    spi_speed_hz=4000000,
    rst=25,          # Reset pin
    width=128,       # Width of the display
    height=160       # Height of the display
)
disp.begin()

# Create a blank image for the display
image = Image.new("RGB", (128, 160), "black")  # Black background
draw = ImageDraw.Draw(image)

# Load a font (use a default PIL font)
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
disp.display(image)
