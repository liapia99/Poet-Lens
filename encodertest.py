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

# Initialize last known state
last_state = GPIO.input(clk_pin)

# List of messages to print when the encoder is turned or pressed
messages = [
    "Message 1: Rotary Encoder turned!",
    "Message 2: Keep turning!",
    "Message 3: Good job!",
    "Message 4: You're on the move!",
    "Message 5: Keep it up!"
]
msg_index = 0

# Callback for rotation detection
def encoder_callback(channel):
    global last_state, msg_index
    
    # Read the current state of the encoder's clock pin
    current_state = GPIO.input(clk_pin)

    # If the current state is different from the last state, rotation occurred
    if current_state != last_state:
        if GPIO.input(dt_pin) != current_state:
            # Turning in one direction (clockwise)
            print(messages[msg_index % len(messages)])
        else:
            # Turning in the other direction (counterclockwise)
            print(messages[msg_index % len(messages)])

        # Update message index after each turn
        msg_index += 1
        
    last_state = current_state

# Callback for button press detection
def button_callback(channel):
    print("Button pressed!")

# Set up the event detection for the clock pin (rotation) and button pin (press)
GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=encoder_callback, bouncetime=200)
GPIO.add_event_detect(btn_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    print("Rotary Encoder is ready. Start turning or press the button!")
    while True:
        time.sleep(0.1)  # Main loop does nothing but waits for events
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings on exit
