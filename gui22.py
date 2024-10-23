from picamera2 import Picamera2
import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
from PIL import Image, ImageTk
import cv2

class WiFiCameraApp:
    def __init__(self, master):
        self.master = master
        master.title("WiFi Camera App")

        self.progress_label = tk.Label(master, text="Loading...")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(master, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        self.progress['value'] = 0

        # Define your networks and their passwords
        self.networks = {
                "IDEALab" : "makerspace",
                "Richard E": "qjftmxqu2se8"
        }

        # Create a frame for the network buttons
        self.network_frame = tk.Frame(master)
        self.network_frame.pack()

        # Create buttons for predefined networks
        self.create_network_buttons()

        self.picam2 = Picamera2()
        self.streaming = False  # Flag for tracking if streaming has started
        self.camera_label = tk.Label(master)
        self.camera_label.pack()

        # Configure camera settings
        self.configure_camera()

    def configure_camera(self):
        """Configure camera settings for better image quality."""
        self.picam2.set_controls({
        "AwbMode": "daylight",            # Automatic white balance
        "Brightness": 1.0,            # Adjust brightness (0.0 to 1.0)
        "Sharpness": 1,               # Adjust sharpness
        "ExposureValue": 10.0,         # Adjust exposure

        "Saturation": 1               # Adjust saturation
        })
        
    # Fetch the preview configuration without the transform
        camera_config = self.picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
        self.picam2.configure(camera_config)

    def create_network_buttons(self):
        for ssid, password in self.networks.items():
            button = tk.Button(self.network_frame, text=ssid, command=lambda s=ssid, p=password: self.connect_to_wifi(s, p))
            button.pack(pady=5)

        self.progress_label.config(text="Select a network to connect.")

    def connect_to_wifi(self, ssid, password):
        self.progress['value'] = 50
        self.progress_label.config(text="Connecting to " + ssid + "...")

        # Connect to Wi-Fi using nmcli
        connect_command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        os.system(connect_command)

        # Simulate connection time
        time.sleep(3)
        connection_status = os.popen("nmcli -t -f WIFI g").read().strip()

        if connection_status == "enabled":
            # Full progress bar and success message
            self.progress['value'] = 100
            self.progress_label.config(text=f"Connected to {ssid}!")
            messagebox.showinfo("Connection", f"Connected to {ssid} successfully!")
            self.hide_network_ui()
            self.start_stream()
        else:
            messagebox.showerror("Connection", f"Failed to connect to {ssid}. Please try again.")
            self.progress['value'] = 0
            self.progress_label.config(text="Select a network to connect.")

    def hide_network_ui(self):
        """Hide the network buttons and progress bar once connected."""
        self.network_frame.pack_forget()
        self.progress.pack_forget()
        self.progress_label.pack_forget()

    def start_stream(self):
        """Start the camera stream once connected."""
        if not self.streaming:
            self.picam2.start()
            self.streaming = True
            self.update_camera()

    def update_camera(self):
        """Update the camera image in the GUI."""
        # Get the camera frame
        frame = self.picam2.capture_array()

        # Convert the frame from BGR (default) to RGB (correct color representation)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the image to PIL format to display in Tkinter
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the Tkinter label with the new image
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)

        # Update the camera feed every 10ms
        self.master.after(10, self.update_camera)


if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCameraApp(root)
    root.mainloop()
