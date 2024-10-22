from picamera2 import Picamera2
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import threading
import time
import wifi
import os

class PiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi GUI")

        # Progress bar setup
        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Label for camera feed
        self.label = tk.Label(root)
        self.label.pack(pady=20)

        # Frame for network buttons
        self.network_frame = tk.Frame(root)
        self.network_frame.pack(pady=20)

        # Known networks and passwords (modify this dictionary to fit your known networks)
        self.known_networks = {
            "MyHomeWiFi": "password123",
            "WorkWiFi": "workpassword456",
            "GuestWiFi": "guestpass789"
        }

        # Start loading and scanning in a separate thread to avoid freezing GUI
        self.progress_thread = threading.Thread(target=self.load_and_scan)
        self.progress_thread.start()

    def load_and_scan(self):
        # Simulate a loading process with a progress bar
        for i in range(101):
            self.progress['value'] = i
            time.sleep(0.03)  # Simulate loading time
            self.root.update_idletasks()

        # Scan for Wi-Fi networks
        networks = self.scan_networks()
        print("Available Networks: ", networks)

        # Create buttons for each scanned network
        for network in networks:
            button = tk.Button(self.network_frame, text=network, command=lambda net=network: self.connect_to_network(net))
            button.pack(pady=5)

        # Start the camera feed after loading completes
        self.start_camera()

    def scan_networks(self):
        # Scan for available Wi-Fi networks (using wifi library)
        networks = wifi.Cell.all('wlan0')
        network_names = [cell.ssid for cell in networks]
        return network_names

    def connect_to_network(self, ssid):
        # Check if network has a predefined password
        if ssid in self.known_networks:
            password = self.known_networks[ssid]
            print(f"Attempting to connect to {ssid} with password {password}...")
            connect_command = f'nmcli dev wifi connect "{ssid}" password "{password}"'
        else:
            print(f"Attempting to connect to {ssid} (no saved password)...")
            connect_command = f'nmcli dev wifi connect "{ssid}"'

        # Execute the command to connect
        result = os.system(connect_command)

        if result == 0:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect to {ssid}")

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
