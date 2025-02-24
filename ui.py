import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib import pyplot as plt
import os

class VideoFrameSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Frame Selector")
        self.root.geometry("800x400")
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        # Title
        title = ttk.Label(self.main_frame, text="Video Frame Selector", font=("Helvetica", 16))
        title.pack(pady=20)
        
        # Video selection button
        self.select_video_btn = ttk.Button(self.main_frame, text="Select Video File", command=self.browse_video)
        self.select_video_btn.pack(pady=10)
        
        # Frame selection controls (initially hidden)
        self.controls_frame = ttk.Frame(self.main_frame)
        
        # Frame slider
        self.slider_label = ttk.Label(self.controls_frame, text="Select Frame:")
        self.frame_slider = ttk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.frame_number = ttk.Label(self.controls_frame, text="Frame: 0")
        
        # View frame button
        self.view_button = ttk.Button(self.controls_frame, text="View Frame", command=self.select_frame)
        
        self.cap = None
        self.frame_count = 0

    def browse_video(self):
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        if video_path:
            self.load_video(video_path)

    def load_video(self, video_path):
        # Release previous video if any
        if self.cap is not None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Failed to load video. Check the file path.")
            return
            
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Show frame selection controls
        self.show_frame_controls()

    def show_frame_controls(self):
        # Configure and show slider
        self.frame_slider.configure(to=self.frame_count - 1)
        self.frame_slider.set(0)
        
        # Pack all controls
        self.controls_frame.pack(fill='x', pady=20)
        self.slider_label.pack(pady=5)
        self.frame_slider.pack(fill='x', pady=5)
        self.frame_number.pack(pady=5)
        self.view_button.pack(pady=10)
        
        # Bind slider movement
        self.frame_slider.configure(command=self.update_frame_number)

    def update_frame_number(self, value):
        frame_num = int(float(value))
        self.frame_number.configure(text=f"Frame: {frame_num}")

    def select_frame(self):
        if not self.cap:
            messagebox.showerror("Error", "No video loaded")
            return
            
        try:
            frame_num = int(self.frame_slider.get())
            print(f"[INFO] Selected frame: {frame_num}")

            img = self.get_frame(frame_num)
            if img is not None:
                plt.close('all')  # Close any existing plot windows
                plt.figure(figsize=(10, 6))
                plt.imshow(img)
                plt.title(f"Selected Frame: {frame_num}")
                plt.axis("off")
                plt.show()
            else:
                messagebox.showerror("Error", "Failed to load selected frame.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def get_frame(self, frame_num):
        print(f"[INFO] Retrieving frame {frame_num}/{self.frame_count}...")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        print(f"[WARNING] Frame {frame_num} could not be retrieved.")
        return None

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to close the application?"):
            if self.cap is not None:
                self.cap.release()
            self.root.destroy()

if __name__ == "__main__":
    app = VideoFrameSelector()
    app.run()
