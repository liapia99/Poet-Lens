from picamera2 import Picamera2, Preview
import tkinter as tk
from tkinter import ttk, messagebox
import os, time, requests, signal
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
import openai, replicate
import numpy as np
import cv2
import threading

# Load API keys from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
openai.api_key = openai_api_key

# Printer setup
baud_rate = 9600
printer = Adafruit_Thermal('/dev/serial0', baud_rate, timeout=5)

# Button and LED setup
shutter_button = Button(16)
power_button = Button(26, hold_time=2)
led = LED(20)
onled = LED(21)

# Home directory for image saving
home_directory = os.path.expanduser('~') + "/Poet-Lens3/"

# prompts
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


# Function to generate a poem from an image description
def generate_prompt(image_description):
    prompt_format = "Poem format: " + poem_format + "\n\n"
    prompt_scene = "Scene description: " + image_description + "\n\n"
    prompt = prompt_base + prompt_format + prompt_scene
    return prompt.replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("'", "")

# Function to print the poem using the thermal printer
def print_poem(poem):
    printable_poem = wrap_text(poem, 42)
    printer.justify('L')
    printer.println(printable_poem)
    
def take_photo_and_print_poem(picam2):  # Accept picam2 as an argument
    led.blink()
    
    try:
        metadata = picam2.capture_file(home_directory + "image.jpg")
        print('----- SUCCESS: image saved locally')

        # Send saved image to API
        image_caption = replicate.run(
            "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
            input={"image": open(home_directory + "image.jpg", "rb"), "caption": True})

        print('caption: ', image_caption)

        # Generate our prompt for GPT
        prompt = generate_prompt(image_caption)

        # Feed prompt to OpenAI to create the poem
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        )

        poem = completion.choices[0].message.content

        print('--------POEM BELOW-------')
        print(poem)
        print('------------------')

        print_poem(poem)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        led.off()

# Tkinter GUI class for the WiFi connection and camera stream
class WiFiCameraApp:
    def __init__(self, master):
        self.master = master
        master.title("Poetry Camera - WiFi Setup")

        self.progress_label = tk.Label(master, text="Loading...")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(master, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        self.progress['value'] = 0

        self.networks = {"IDEALab": "makerspace", "Richard E": "qjftmxqu2se8", "julka":"march33/33"}
        self.network_frame = tk.Frame(master)
        self.network_frame.pack()

        self.create_network_buttons()

        # Button to start camera stream
        self.stream_button = tk.Button(master, text="Start Camera Stream", command=self.start_camera_stream)
        self.stream_button.pack(pady=10)

    def create_network_buttons(self):
        for ssid, password in self.networks.items():
            button = tk.Button(self.network_frame, text=ssid,
                               command=lambda s=ssid, p=password: self.connect_to_wifi(s, p))
            button.pack(pady=5)

        self.progress_label.config(text="Select a network to connect.")

    def connect_to_wifi(self, ssid, password):
        self.progress['value'] = 50
        self.progress_label.config(text="Connecting to " + ssid + "...")
        connect_command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        os.system(connect_command)
        time.sleep(3)
        connection_status = os.popen("nmcli -t -f WIFI g").read().strip()
        if connection_status == "enabled":
            self.progress['value'] = 100
            self.progress_label.config(text=f"Connected to {ssid}!")
            messagebox.showinfo("Connection", f"Connected to {ssid} successfully!")
            self.hide_network_ui()
        else:
            messagebox.showerror("Connection", f"Failed to connect to {ssid}. Please try again.")
            self.progress['value'] = 0
            self.progress_label.config(text="Select a network to connect.")

    def hide_network_ui(self):
        self.network_frame.pack_forget()
        self.progress.pack_forget()
        self.progress_label.pack_forget()
        
    def start_camera_stream(self):
        camera_streamer = CameraStreamer()
        camera_streamer.start_stream()
        
class CameraStreamer:
    def __init__(self):
        self.picam2 = Picamera2()
        self.lock = threading.Lock()
        preview_config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
        self.picam2.configure(preview_config)

    def start_stream(self):
        self.picam2.start()
        
        while True:
            frame = self.picam2.capture_array()  # Make sure this line is indented correctly
            if frame is not None:
                cv2.imshow("Live Stream", frame)
                key = cv2.waitKey(1) & 0xFF

                # Check for the shutter button press
                if shutter_button.is_pressed:
                    take_photo_and_print_poem(self.picam2)

                # Quit the stream if 'q' is pressed
                if key == ord('q'):
                    break

        self.picam2.stop()
        cv2.destroyAllWindows()

# Main code to run the Tkinter app and listen for button presses
if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCameraApp(root)
    root.mainloop()

    shutter_button.when_pressed = take_photo_and_print_poem
    power_button.when_held = shutdown
    signal.pause()
