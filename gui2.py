from picamera2 import Picamera2
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading

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

    def start_stream(self):
        self.picam2.start()
        while True:
            frame = self.picam2.capture_array()
            if frame is not None:
                cv2.imshow("Live Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiCameraApp(root)
    root.mainloop()
