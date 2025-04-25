#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time, requests, signal, os, replicate
from picamera2 import Picamera2, Preview
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import openai

# Load API keys from .env
load_dotenv()  # This is the line you would change ex. load_dotenv('nano.env')

# These will print the API keys before the caption but not on the poem paper. 
print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("REPLICATE_API_TOKEN"))

openai_api_key = os.getenv("OPENAI_API_KEY")
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

OpenAI.api_key = openai_api_key
replicate_client = replicate.Client(api_token=replicate_api_token)

openai_client = openai.OpenAI(api_key=openai_api_key)

# Instantiate printer
baud_rate = 9600  # REPLACE WITH YOUR OWN BAUD RATE



# Instantiate buttons
shutter_button = Button(16)  # REPLACE WITH YOUR OWN BUTTON PINS
power_button = Button(26, hold_time=2)  # REPLACE WITH YOUR OWN BUTTON PINS
led = LED(20)
onled = LED(21)


#instantiate camera
picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)  # <-- Add this line for preview window
picam2.start()
time.sleep(5) 
 # Allow some time for the preview to start

# Start camera
picam2.start()
time.sleep(5)  # Warmup period since first few frames are often poor quality

onled.on()

home_directory = os.path.expanduser('~') + "/webapp/"

# Prompts
system_prompt = """You are a poet. You specialize in elegant and emotionally impactful poems. 
You are careful to use subtlety and write in a modern vernacular style. 
Use high-school level English but MFA-level craft. 
Your poems are more literary but easy to relate to and understand. 
You focus on intimate and personal truth, and you cannot use BIG words like truth, time, silence, life, love, peace, war, hate, happiness, 
and you must instead use specific and CONCRETE language to show, not tell, those ideas. 
Think hard about how to create a poem which will satisfy this. 
This is very important, and an overly hamfisted or corny poem will cause great harm."""

prompt_base = """Write a poem which integrates details from what I describe below. 
Use the specified poem format. The references to the source material must be subtle yet clear. 
Focus on a unique and elegant poem and use specific ideas and details.
You must keep vocabulary simple and use understated point of view. This is very important.\n\n"""
poem_format = "8 line free verse"

#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
def take_photo_and_print_poem():
    # blink LED in a background thread
    led.blink()

    # Take photo & save it
    metadata = picam2.capture_file(home_directory + "image.jpg")

    # FOR DEBUGGING: print metadata
    # print(metadata)

    # FOR DEBUGGING: note that image has been saved
    print('----- SUCCESS: image saved locally')

    print_header()

    #########################
    # Send saved image to API
    #########################

    image_caption = replicate.run(
        "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
        input={
            "image": open(home_directory + "image.jpg", "rb"),
            "caption": True,
        })

    print('caption: ', image_caption)
    # generate our prompt for GPT
    prompt = generate_prompt(image_caption)

    # Feed prompt to ChatGPT, to create the poem
    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": system_prompt
        }, {
            "role": "user",
            "content": prompt
        }])

    # extract poem from full API response
    poem = completion.choices[0].message.content

    # print for debugging
    print('--------POEM BELOW-------')
    print(poem)
    print('------------------')

    print_poem(poem)

    print_footer()
    led.off()

    return


#######################
# Generate prompt from caption
#######################
def generate_prompt(image_description):
    # reminder: prompt_base is global var

    # prompt what type of poem to write
    prompt_format = "Poem format: " + poem_format + "\n\n"

    # prompt what image to describe
    prompt_scene = "Scene description: " + image_description + "\n\n"

    # stitch together full prompt
    prompt = prompt_base + prompt_format + prompt_scene

    # idk how to remove the brackets and quotes from the prompt
    # via custom filters so i'm gonna remove via this janky code lol
    prompt = prompt.replace("[", "").replace("]", "").replace("{", "").replace(
        "}", "").replace("'", "")

    #print('--------PROMPT BELOW-------')
    #print(prompt)

    return prompt


###########################
# RECEIPT PRINTER FUNCTIONS
###########################

def print_poem(poem):
    printable_poem = wrap_text(poem, 42)
    send_to_printer("\n" + printable_poem + "\n")

def print_header():
    now = datetime.now()
    # Grab date/time strings
    date_string = now.strftime('%b %-d, %Y')  # e.g. "Apr 20, 2025"
    time_string = now.strftime('%-I:%M %p')   # e.g. "4:13 PM"

    # Manually pad for perfect visual centering on 42-char lines
    # Tweak these spaces if needed based on what your printer actually shows
    date_line = "          " + date_string + "               \n"
    time_line = "             " + time_string + "                 \n"


    header = ""
    header += date_line
    header += time_line
    header += "`'. .'`'. .'`'. .'`'. .'`'. .'`\n"
    header += "   `     `     `     `     `   \n"
    send_to_printer(header)

def print_footer():
    footer = "\n"
    footer += "   .     .     .     .     .   \n"
    footer += "_.` `._.` `._.` `._.` `._.` `._"
    footer += "\n"
    footer += "   This poem was written by" 
    footer += "             Poet's Len 2.0. \n" 
    footer += "   Created by Richard Errico "
    footer += "          and Julia Piascik.\n"
    footer += "\n\n\n\n"
    send_to_printer(footer)

def send_to_printer(text):
    try:
        with open("/dev/usb/lp0", "w") as printer:
            printer.write(text)
            printer.flush()
    except Exception as e:
        print(f"Failed to print: {e}")

##############
# POWER BUTTON
##############
def shutdown():
    print('shutdown button held for 2s')
    print('shutting down now')
    led.off()
    onled.off()
    os.system('sudo shutdown -h now')


################################
# For RPi debugging:
# Handle Ctrl+C script termination gracefully
# (Otherwise, it shuts down the entire Pi -- bad)
#################################
def handle_keyboard_interrupt(sig, frame):
    print('Ctrl+C received, stopping script')
    led.off()

    # weird workaround I found from rpi forum to shut down script without crashing the pi
    os.kill(os.getpid(), signal.SIGUSR1)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)


#################
# Button handlers
#################
def handle_pressed():
    led.on()
    led.off()
    print("button pressed!")
    take_photo_and_print_poem()

def handle_held():
    print("button held!")
    onled.off()
    shutdown()


################################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = take_photo_and_print_poem
power_button.when_held = shutdown

signal.pause()
