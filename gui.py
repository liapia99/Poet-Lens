from picamera2 import Picamera2
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import threading
import time
import wifi
import os

class WiFiCameraApp:
    def __init__(self, master):
        self.master = master
        master.title("WiFi Camera App")

        self.progress_label = tk.Label(master, text="Loading...")
        self.progress_label.pack()

        self.progress = ttk.Progressbar(master, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        self.progress.start()

        # Define your networks and their passwords
        self.networks = {
            "YourNetworkSSID1": "YourPassword1",
            "YourNetworkSSID2": "YourPassword2",
            "YourNetworkSSID3": "YourPassword3"
        }

        # Create buttons for predefined networks
        self.create_network_buttons()

        self.video_frame = tk.Frame(master)
        self.video_frame.pack()

        self.picam2 = Picamera2()
        self.stream_thread = threading.Thread(target=self.start_stream)
        self.stream_thread.start()

    def create_network_buttons(self):
        for ssid, password in self.networks.items():
            button = tk.Button(self.master, text=ssid, command=lambda s=ssid, p=password: self.connect_to_wifi(s, p))
            button.pack(pady=5)

        self.progress.stop()
        self.progress_label.config(text="Select a network to connect.")

    def connect_to_wifi(self, ssid, password):
        connect_command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        os.system(connect_command)
        messagebox.showinfo("Connection", f"Connecting to {ssid}...")

    def start_camera(self):
        # Initialize picamera2 after progress bar completes
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration())
        self.picam2.start()

        # Start updating camera feed
        self.update_camera()

    def update_camera(self):
        # Capture frame-by-frame from the camera
        frame = self.picam2.capture_array()

        # Convert the frame to ImageTk format for Tkinter
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

        # Update the camera feed every 10 ms
        self.label.after(10, self.update_camera)

    def on_close(self):
        if hasattr(self, 'picam2'):
            self.picam2.close()
        self.root.destroy()

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    app = PiGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
