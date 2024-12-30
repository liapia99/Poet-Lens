import RPi.GPIO as GPIO
import time

# Define the GPIO pins connected to the rotary encoder
pinCLK = 17  # Connected to CLK on the rotary encoder
pinDT = 18   # Connected to DT on the rotary encoder
pinSW = 27   # Connected to SW on the rotary encoder

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

# Messages for specific positions
messages = {
    0: "Position 0: Starting Point",
    5: "Position 5: Five Steps!",
    10: "Position 10: Ten Steps!",
    15: "Position 15: Halfway there!",
    20: "Position 20: Almost Done!",
    25: "Position 25: Almost at the end!"
}

# Function to read the encoder
def read_encoder():
    global encoderPos, lastCLK
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

# Main program loop
try:
    # Initialize the serial communication (print to console in Python)
    print("Rotary Encoder Initialized")
    
    # Initialize lastCLK to the current state of CLK
    lastCLK = GPIO.input(pinCLK)
    
    while True:
        # Check if the encoder has moved
        read_encoder()

        # Ensure the position stays within 0 to 29
        if encoderPos < 0:
            encoderPos = 29  # Wrap around to 29
        elif encoderPos > 29:
            encoderPos = 0  # Wrap around to 0

        # Check if the encoder position has changed and print a message if it's one of the key positions
        if encoderPos != lastEncoderPos:
            if encoderPos in messages:
                print(messages[encoderPos])
            lastEncoderPos = encoderPos
        
        # Check if the button is pressed (confirm selection)
        if GPIO.input(pinSW) == GPIO.LOW:
            # Print a confirmation message for the selected position
            if encoderPos in messages:
                print(f"Selected Position: {encoderPos}")
            # Wait for the button to be released
            while GPIO.input(pinSW) == GPIO.LOW:
                time.sleep(0.01)
        
        # Small delay to debounce the reading
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings on exit
