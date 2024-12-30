import RPi.GPIO as GPIO
import time
import tkinter as tk

# Define the GPIO pins connected to the rotary encoder
pinCLK = 17  # Connected to CLK on the rotary encoder
pinDT = 18   # Connected to DT on the rotary encoder
pinSW = 1   # Connected to SW on the rotary encoder

# Variables to hold the current and last encoder position
encoderPos = 0
lastEncoderPos = 0

# Variables to keep track of the state of the pins
lastCLK = 0
currentCLK = 0

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set up the pins as input with pull-up resistors
GPIO.setup(pinCLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinDT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinSW, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button press

# Define the number of buttons
num_buttons = 5
button_names = [f"Button {i+1}" for i in range(num_buttons)]

# Create a simple Tkinter window
root = tk.Tk()
root.title("Rotary Encoder Button Selector")

# A function to handle button presses
def button_action(button_idx):
    print(f"Selected {button_names[button_idx]}")

# Create a list of buttons
buttons = []
default_bg_color = "lightgray"  # Default background color for the buttons
highlight_bg_color = "lightblue"  # Color when a button is selected

for i in range(num_buttons):
    btn = tk.Button(root, text=button_names[i], width=20, bg=default_bg_color, command=lambda idx=i: button_action(idx))
    btn.grid(row=0, column=i)
    buttons.append(btn)

# Function to read the encoder and update the selected button
def read_encoder():
    global encoderPos, lastCLK  # Make sure to reference the global variable
    currentCLK = GPIO.input(pinCLK)
    
    # If the current state of CLK is different from the last state, a pulse occurred
    if currentCLK != lastCLK:
        # If the DT state is different from the CLK state, it's clockwise
        if GPIO.input(pinDT) != currentCLK:
            encoderPos += 1
        else:
            # Otherwise, it's counterclockwise
            encoderPos -= 1
    lastCLK = currentCLK

# Highlight the selected button based on encoder position
def update_selected_button():
    global encoderPos  # Make sure to reference the global variable

    # Ensure the position stays within the range of buttons
    if encoderPos < 0:
        encoderPos = num_buttons - 1  # Wrap around to the last button
    elif encoderPos >= num_buttons:
        encoderPos = 0  # Wrap around to the first button

    # Remove highlight from all buttons
    for button in buttons:
        button.config(bg=default_bg_color)  # Default background color

    # Highlight the selected button
    buttons[encoderPos].config(bg=highlight_bg_color)  # Highlight color

# Main program loop
try:
    # Initialize the lastCLK to the current state of CLK
    lastCLK = GPIO.input(pinCLK)
    
    # Main loop to handle rotary encoder and button interactions
    while True:
        # Read the encoder to update the selected position
        read_encoder()

        # Update the selected button on the GUI based on encoder position
        update_selected_button()

        # Check if the button is pressed (confirm selection)
        if GPIO.input(pinSW) == GPIO.LOW:
            # Perform the action for the selected button
            button_action(encoderPos)
            # Wait for the button to be released (debounce)
            while GPIO.input(pinSW) == GPIO.LOW:
                time.sleep(0.01)

        # Small delay to debounce the reading
        time.sleep(0.01)

        # Update the Tkinter window
        root.update()

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings on exit
    root.quit()  # Exit the Tkinter window
