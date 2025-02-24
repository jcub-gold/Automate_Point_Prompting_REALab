import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from matplotlib import pyplot as plt
import os
from matplotlib.widgets import TextBox, Button
import csv

class VideoFrameSelector:
    """
    Method: __init__
    --------------------------
    Initializes the VideoFrameSelector application. Creates the main window and sets up the initial UI components
    including the title, video selection button, and frame control elements. Initializes all necessary instance
    variables for video handling and frame selection.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Frame Selector")
        self.root.geometry("800x400")
        
        self.video_filename = None
        
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        title = ttk.Label(self.main_frame, text="Video Frame Selector", font=("Helvetica", 16))
        title.pack(pady=20)
        
        self.select_video_btn = ttk.Button(self.main_frame, text="Select Video File", command=self.browse_video)
        self.select_video_btn.pack(pady=10)
        
        self.controls_frame = ttk.Frame(self.main_frame)
        
        self.slider_label = ttk.Label(self.controls_frame, text="Select Frame:")
        self.frame_slider = ttk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        
        self.view_button = ttk.Button(self.controls_frame, text="View Frame", command=self.select_frame)
        
        self.cap = None
        self.frame_count = 0
        self.current_frame = None
        self.selected_points = []
        self.current_fig = None
        self.current_ax = None

    """
    Method: browse_video
    --------------------------
    Opens a file dialog for the user to select a video file. Supports MP4 format and other video formats.
    Once a video is selected, it stores the filename and calls load_video to process the selected file.
    """
    def browse_video(self):
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        if video_path:
            self.video_filename = os.path.basename(video_path)
            self.load_video(video_path)

    """
    Method: load_video
    --------------------------
    Takes a video path as input and loads the video using OpenCV. Releases any previously loaded video,
    initializes the video capture object, and sets up the frame count. If the video fails to load,
    displays an error message.
    """
    def load_video(self, video_path):
        if self.cap is not None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Failed to load video. Check the file path.")
            return
            
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.show_frame_controls()

    """
    Method: show_frame_controls
    --------------------------
    Sets up and displays the frame control interface including the slider, frame entry box, and navigation
    buttons. Configures the slider range based on video frame count and sets up keyboard shortcuts for
    frame navigation.
    """
    def show_frame_controls(self):
        self.frame_slider.configure(to=self.frame_count - 1)
        self.frame_slider.set(0)
        
        self.controls_frame.pack(fill='x', pady=20)
        self.slider_label.pack(pady=5)
        self.frame_slider.pack(fill='x', pady=5)
        
        frame_entry_frame = ttk.Frame(self.controls_frame)
        frame_entry_frame.pack(pady=5)
        
        prev_button = ttk.Button(frame_entry_frame, text="←", width=3, 
                               command=self.previous_frame)
        prev_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_entry_frame, text="Frame:").pack(side=tk.LEFT, padx=5)
        self.frame_entry = ttk.Entry(frame_entry_frame, width=10)
        self.frame_entry.pack(side=tk.LEFT, padx=5)
        self.frame_entry.insert(0, "0")
        
        next_button = ttk.Button(frame_entry_frame, text="→", width=3, 
                               command=self.next_frame)
        next_button.pack(side=tk.LEFT, padx=5)
        
        self.frame_entry.bind('<Return>', self.update_from_entry)
        self.frame_entry.bind('<FocusOut>', self.update_from_entry)
        
        self.view_button.pack(pady=10)
        
        self.frame_slider.configure(command=self.update_frame_number)
        
        self.root.bind('<Left>', lambda e: self.previous_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())

    """
    Method: update_frame_number
    --------------------------
    Updates the frame entry box when the slider value changes. Converts the slider value to an integer
    and updates the display accordingly.
    """
    def update_frame_number(self, value):
        frame_num = int(float(value))
        self.frame_entry.delete(0, tk.END)
        self.frame_entry.insert(0, str(frame_num))

    """
    Method: update_from_entry
    --------------------------
    Handles manual frame number entry validation. Ensures the entered frame number is within valid range
    and updates the slider position. Displays warning messages for invalid inputs.
    """
    def update_from_entry(self, event=None):
        try:
            frame_num = int(self.frame_entry.get())
            if 0 <= frame_num < self.frame_count:
                self.frame_slider.set(frame_num)
            else:
                messagebox.showwarning("Invalid Frame", 
                    f"Please enter a frame number between 0 and {self.frame_count-1}")
                self.frame_entry.delete(0, tk.END)
                self.frame_entry.insert(0, str(int(self.frame_slider.get())))
        except ValueError:
            messagebox.showwarning("Invalid Input", 
                "Please enter a valid number")
            self.frame_entry.delete(0, tk.END)
            self.frame_entry.insert(0, str(int(self.frame_slider.get())))

    """
    Method: select_frame
    --------------------------
    Displays the selected video frame in a matplotlib figure. Sets up the interactive plotting environment
    with object selection tools, color options, and control buttons. Initializes the point selection system
    for marking objects in the frame.
    """
    def select_frame(self):
        if not self.cap:
            messagebox.showerror("Error", "No video loaded")
            return
            
        try:
            frame_num = int(self.frame_slider.get())
            print(f"[INFO] Selected frame: {frame_num}")

            img = self.get_frame(frame_num)
            if img is not None:
                plt.close('all')
                self.current_frame = img
                self.current_fig, self.current_ax = plt.subplots(figsize=(10, 6))
                self.current_ax.imshow(img)
                self.current_ax.set_title(f"Selected Frame: {frame_num}")
                self.current_ax.axis("off")
                
                self.object_points = {}
                self.default_colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow']
                self.current_color = self.default_colors[0]
                self.object_entries = []
                self.object_count = 0
                
                self.toolbar_frame = plt.axes([0.1, 0.01, 0.8, 0.08])
                self.toolbar_frame.axis('off')
                
                self.add_object_entry()
                
                plus_button_ax = plt.axes([0.91, 0.05, 0.03, 0.03])
                plus_button = Button(plus_button_ax, '+')
                plus_button.on_clicked(self.add_object_entry)
                
                save_button_ax = plt.axes([0.825, 0.01, 0.06, 0.03])
                save_button = Button(save_button_ax, 'Save')
                save_button.on_clicked(self.save_points)
                
                clear_button_ax = plt.axes([0.895, 0.01, 0.06, 0.03])
                clear_button = Button(clear_button_ax, 'Clear')
                clear_button.on_clicked(self.clear_points)
                
                self.current_fig.canvas.mpl_connect('button_press_event', self.on_click)
                
                plt.show()
            else:
                messagebox.showerror("Error", "Failed to load selected frame.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    """
    Method: add_object_entry
    --------------------------
    Adds a new object entry to the interface for point selection. Creates text entry and color selection
    buttons for the new object. Manages object colors and ensures only one object is active at a time.
    """
    def add_object_entry(self, event=None):
        self.object_count += 1
        y_pos = 0.05 - (self.object_count - 1) * 0.03
        
        color_index = (self.object_count - 1) % len(self.default_colors)
        self.current_color = self.default_colors[color_index]
        
        entry_ax = plt.axes([0.1, y_pos, 0.4, 0.02])
        entry = TextBox(entry_ax, f'Obj {self.object_count}: ', initial=f'object{self.object_count}')
        entry.label.set_fontsize(8)
        entry.text_disp.set_fontsize(8)
        
        color_ax = plt.axes([0.55, y_pos, 0.1, 0.02])
        color_button = Button(color_ax, 'Color', color=self.current_color)
        
        object_data = {
            'entry': entry,
            'color_button': color_button,
            'color': self.current_color,
            'active': True
        }
        
        for obj in self.object_entries:
            obj['active'] = False
            obj['entry'].label.set_color('black')
        
        self.object_entries.append(object_data)
        
        entry.label.set_color(self.current_color)
        
        color_button.on_clicked(lambda x, obj=object_data: self.choose_color_for_object(obj))
        
        entry.on_submit(lambda x, obj=object_data: self.select_object(obj))
        
        self.current_fig.canvas.draw()

    """
    Method: choose_color_for_object
    --------------------------
    Opens a dialog for selecting the color of an object. Updates the object's color in the interface
    and refreshes the display to reflect the change.
    """
    def choose_color_for_object(self, object_data):
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta']
        color = simpledialog.askstring("Color Selection", 
                                     "Enter color name:\n" + ", ".join(colors))
        if color and color.lower() in colors:
            object_data['color'] = color.lower()
            object_data['color_button'].color = color.lower()
            self.current_fig.canvas.draw()

    """
    Method: select_object
    --------------------------
    Handles object selection in the interface. Deactivates all other objects and highlights the selected
    object with its associated color.
    """
    def select_object(self, selected_obj):
        for obj in self.object_entries:
            obj['active'] = False
            obj['entry'].label.set_color('black')
        
        selected_obj['active'] = True
        selected_obj['entry'].label.set_color(selected_obj['color'])
        
        self.current_fig.canvas.draw()

    """
    Method: on_click
    --------------------------
    Handles mouse click events on the frame. Records clicked coordinates for the active object and
    draws a marker at the selected point. Updates the object_points dictionary with the new coordinates.
    """
    def on_click(self, event):
        if event.inaxes != self.current_ax:
            return

        x, y = event.xdata, event.ydata
        
        active_object = None
        for obj in self.object_entries:
            if obj['active']:
                active_object = obj
                break
                
        if not active_object:
            return
            
        object_name = active_object['entry'].text
        
        if object_name not in self.object_points:
            self.object_points[object_name] = {'points': [], 'color': active_object['color']}
        
        self.object_points[object_name]['points'].append((x, y))
        
        marker_size = 10
        line_width = 1
        color = active_object['color']
        
        self.current_ax.plot([x-marker_size, x+marker_size], [y, y], 
                           color=color, linewidth=line_width)
        self.current_ax.plot([x, x], [y-marker_size, y+marker_size], 
                           color=color, linewidth=line_width)
        
        print(f"Selected point for {object_name}: ({int(x)}, {int(y)})")
        
        self.current_fig.canvas.draw()

    """
    Method: clear_points
    --------------------------
    Clears all points for the currently active object. Redraws the frame and maintains points for other
    objects. Only affects the currently selected object's points.
    """
    def clear_points(self, event):
        active_object = None
        for obj in self.object_entries:
            if obj['active']:
                active_object = obj
                break
        
        if not active_object:
            return
            
        object_name = active_object['entry'].text
        
        if object_name in self.object_points:
            self.object_points[object_name]['points'] = []
        
        self.current_ax.clear()
        self.current_ax.imshow(self.current_frame)
        self.current_ax.axis('off')
        
        for obj_name, obj_data in self.object_points.items():
            if obj_name != object_name:
                for x, y in obj_data['points']:
                    marker_size = 10
                    line_width = 1
                    color = obj_data['color']
                    
                    self.current_ax.plot([x-marker_size, x+marker_size], [y, y], 
                                       color=color, linewidth=line_width)
                    self.current_ax.plot([x, x], [y-marker_size, y+marker_size], 
                                       color=color, linewidth=line_width)
        
        self.current_fig.canvas.draw()

    """
    Method: get_frame
    --------------------------
    Retrieves a specific frame from the video by frame number. Converts the frame from BGR to RGB color
    space and returns it. Prints status messages about frame retrieval.
    """
    def get_frame(self, frame_num):
        print(f"[INFO] Retrieving frame {frame_num}/{self.frame_count}...")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print(f"[WARNING] Frame {frame_num} could not be retrieved.")
        return None

    """
    Method: run
    --------------------------
    Starts the main application loop. Sets up the window close protocol and runs the tkinter main loop.
    """
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    """
    Method: on_closing
    --------------------------
    Handles application shutdown. Prompts for confirmation, releases video resources, and closes the
    application window.
    """
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to close the application?"):
            if self.cap is not None:
                self.cap.release()
            self.root.destroy()

    """
    Method: previous_frame
    --------------------------
    Navigates to the previous frame in the video if available. Updates both the slider position and
    frame number display.
    """
    def previous_frame(self):
        current_frame = int(self.frame_slider.get())
        if current_frame > 0:
            self.frame_slider.set(current_frame - 1)
            self.update_frame_number(current_frame - 1)

    """
    Method: next_frame
    --------------------------
    Navigates to the next frame in the video if available. Updates both the slider position and
    frame number display.
    """
    def next_frame(self):
        current_frame = int(self.frame_slider.get())
        if current_frame < self.frame_count - 1:
            self.frame_slider.set(current_frame + 1)
            self.update_frame_number(current_frame + 1)

    """
    Method: save_points
    --------------------------
    Saves the selected points for all objects to a CSV file. Creates an annotations directory if it
    doesn't exist, handles both new files and updates to existing files. Prevents duplicate entries
    and provides feedback about the save operation.
    """
    def save_points(self, event):
        if not self.object_points:
            messagebox.showinfo("Info", "No points to save.")
            return
            
        try:
            frame_num = int(self.frame_slider.get())
            base_filename = os.path.splitext(self.video_filename)[0]
            dir_path = f'annotations/{base_filename}'
            os.makedirs(dir_path, exist_ok=True)
            csv_filename = f'{dir_path}/points.csv'
            
            existing_entries = set()
            if os.path.exists(csv_filename):
                with open(csv_filename, 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    for row in reader:
                        entry = (row[0], int(row[1]), row[2], int(row[3]), int(row[4]))
                        existing_entries.add(entry)
            
            mode = 'a' if os.path.exists(csv_filename) else 'w'
            new_points_added = 0
            
            with open(csv_filename, mode, newline='') as csvfile:
                writer = csv.writer(csvfile)
                if mode == 'w':
                    writer.writerow(['video_name', 'frame_number', 'object_name', 'x', 'y'])
                
                for obj_name, obj_data in self.object_points.items():
                    for x, y in obj_data['points']:
                        entry = (self.video_filename, frame_num, obj_name, int(x), int(y))
                        if entry not in existing_entries:
                            writer.writerow(list(entry))
                            new_points_added += 1
            
            if new_points_added > 0:
                messagebox.showinfo("Success", f"Added {new_points_added} new points to {csv_filename}")
            else:
                messagebox.showinfo("Info", "No new points to add (all points already exist in file)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save points: {str(e)}")
