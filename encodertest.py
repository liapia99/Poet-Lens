import RPi.GPIO as GPIO
import time

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins connected to the rotary encoder
clk_pin = 17  # Clock Pin (rotation)
dt_pin = 18   # Data Pin (rotation)
btn_pin = 27  # Button Pin (press action)

# Set up the pins as input with pull-up resistors
GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button press

# Initialize last known state and rotation counter
last_state = GPIO.input(clk_pin)
counter = 0  # Track number of pulses

# Define a number of steps per full revolution (e.g., 360 steps for 360 degrees)
steps_per_revolution = 360

# List of messages for specific spots on the unit circle (e.g., angles)
messages = {
    0: "You are at 0° - Starting Point!",
    90: "You are at 90° - Right Angle!",
    180: "You are at 180° - Halfway there!",
    270: "You are at 270° - Three-quarters!",
}

# Map the counter to the angle on the unit circle
def get_angle(counter, steps_per_revolution):
    angle = (counter % steps_per_revolution) * (360 / steps_per_revolution)
    return angle

# Callback for rotation detection
def encoder_callback(channel):
    global last_state, counter
    
    # Read the current state of the encoder's clock pin
    current_state = GPIO.input(clk_pin)

    # If the current state is different from the last state, rotation occurred
    if current_state != last_state:
        if GPIO.input(dt_pin) != current_state:
            # Turning in one direction (clockwise)
            counter += 1
        else:
            # Turning in the other direction (counterclockwise)
            counter -= 1
        
        # Map counter to an angle on the unit circle
        angle = get_angle(counter, steps_per_revolution)
        
        # Check if the angle matches any of our specific spots
        for key_angle in messages.keys():
            if int(angle) == key_angle:
                print(messages[key_angle])

    last_state = current_state

# Set up the event detection for the clock pin (rotation)
GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=encoder_callback, bouncetime=200)

try:
    print("Rotary Encoder is ready. Start turning!")
    while True:
        time.sleep(0.1)  # Main loop does nothing but waits for events
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings on exit
