from picamera2 import Picamera2
import tkinter as tk
from tkinter import ttk, messagebox
import os, time, requests
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
import openai, replicate

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

# Camera setup
picam2 = Picamera2()

# Home directory for image saving
home_directory = os.path.expanduser('~') + "/poetry-camera/"

# Prompt for the poem generation
system_prompt = """You are a poet ... [content shortened for brevity]"""
prompt_base = "Write a poem ... [content shortened for brevity]"
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


# Function to take a photo, generate a poem, and print it
def take_photo_and_print_poem():
    led.blink()
    metadata = picam2.capture_file(home_directory + "image.jpg")
    image_caption = replicate.run(
        "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
        input={"image": open(home_directory + "image.jpg", "rb"), "caption": True}
    )
    prompt = generate_prompt(image_caption)
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    )
    poem = completion.choices[0].message.content
    print_poem(poem)
    led.off()


# Shutdown function for power button
def shutdown():
    led.off()
    onled.off()
    os.system('sudo shutdown -h now')


# Tkinter GUI class for the WiFi connection
class WiFiCameraApp:
    def __init__(self, master):
        self.master = master
        master.title("Poetry Camera - WiFi Setup")

        self.progress_label = tk.Label(master, text="Loading...")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(master, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        self.progress['value'] = 0

        self.networks = {"IDEALab": "makerspace", "Richard E": "qjftmxqu2se8"}
        self.network_frame = tk.Frame(master)
        self.network_frame.pack()

        self.create_network_buttons()

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


# Main code to run the Tkinter app and listen for button presses
if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCameraApp(root)
    root.mainloop()

    shutter_button.when_pressed = take_photo_and_print_poem
    power_button.when_held = shutdown
