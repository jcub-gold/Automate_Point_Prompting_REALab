import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from matplotlib import pyplot as plt
import os
from matplotlib.widgets import TextBox, Button
import csv

class VideoFrameSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Frame Selector")
        self.root.geometry("800x400")
        
        self.video_filename = None  # Add this line
        
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
        
        # View frame button
        self.view_button = ttk.Button(self.controls_frame, text="View Frame", command=self.select_frame)
        
        self.cap = None
        self.frame_count = 0
        self.current_frame = None  # Store the current frame
        self.selected_points = []  # Store selected points
        self.current_fig = None    # Store the current figure
        self.current_ax = None     # Store the current axes

    def browse_video(self):
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        if video_path:
            self.video_filename = os.path.basename(video_path)  # Store the filename
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
        
        # Create frame number entry frame with navigation buttons
        frame_entry_frame = ttk.Frame(self.controls_frame)
        frame_entry_frame.pack(pady=5)
        
        # Previous frame button
        prev_button = ttk.Button(frame_entry_frame, text="←", width=3, 
                               command=self.previous_frame)
        prev_button.pack(side=tk.LEFT, padx=5)
        
        # Frame number label and entry
        ttk.Label(frame_entry_frame, text="Frame:").pack(side=tk.LEFT, padx=5)
        self.frame_entry = ttk.Entry(frame_entry_frame, width=10)
        self.frame_entry.pack(side=tk.LEFT, padx=5)
        self.frame_entry.insert(0, "0")
        
        # Next frame button
        next_button = ttk.Button(frame_entry_frame, text="→", width=3, 
                               command=self.next_frame)
        next_button.pack(side=tk.LEFT, padx=5)
        
        # Bind entry validation and update
        self.frame_entry.bind('<Return>', self.update_from_entry)
        self.frame_entry.bind('<FocusOut>', self.update_from_entry)
        
        # Frame display
        self.view_button.pack(pady=10)
        
        # Bind slider movement
        self.frame_slider.configure(command=self.update_frame_number)
        
        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.previous_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())

    def update_frame_number(self, value):
        frame_num = int(float(value))
        self.frame_entry.delete(0, tk.END)
        self.frame_entry.insert(0, str(frame_num))

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
                self.current_frame = img
                self.current_fig, self.current_ax = plt.subplots(figsize=(10, 6))
                self.current_ax.imshow(img)
                self.current_ax.set_title(f"Selected Frame: {frame_num}")
                self.current_ax.axis("off")
                
                # Initialize object points dictionary and object counter
                self.object_points = {}  # {object_name: {'points': [], 'color': color}}
                self.default_colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow']
                self.current_color = self.default_colors[0]  # Start with red
                self.object_entries = []  # Store object entry widgets
                self.object_count = 0
                
                # Create toolbar for objects (moved lower and made smaller)
                self.toolbar_frame = plt.axes([0.1, 0.01, 0.8, 0.08])
                self.toolbar_frame.axis('off')
                
                # Add initial object
                self.add_object_entry()
                
                # Add '+' button for new objects (adjusted position)
                plus_button_ax = plt.axes([0.91, 0.05, 0.03, 0.03])
                plus_button = Button(plus_button_ax, '+')
                plus_button.on_clicked(self.add_object_entry)
                
                # Add save button next to clear button
                save_button_ax = plt.axes([0.825, 0.01, 0.06, 0.03])
                save_button = Button(save_button_ax, 'Save')
                save_button.on_clicked(self.save_points)
                
                # Add clear button (adjusted position and size)
                clear_button_ax = plt.axes([0.895, 0.01, 0.06, 0.03])
                clear_button = Button(clear_button_ax, 'Clear')
                clear_button.on_clicked(self.clear_points)
                
                # Connect the click event
                self.current_fig.canvas.mpl_connect('button_press_event', self.on_click)
                
                plt.show()
            else:
                messagebox.showerror("Error", "Failed to load selected frame.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_object_entry(self, event=None):
        self.object_count += 1
        y_pos = 0.05 - (self.object_count - 1) * 0.03  # Reduced vertical spacing
        
        # Get next default color
        color_index = (self.object_count - 1) % len(self.default_colors)
        self.current_color = self.default_colors[color_index]
        
        # Create entry box for object name (smaller size)
        entry_ax = plt.axes([0.1, y_pos, 0.4, 0.02])
        entry = TextBox(entry_ax, f'Obj {self.object_count}: ', initial=f'object{self.object_count}')
        entry.label.set_fontsize(8)  # Smaller font for label
        entry.text_disp.set_fontsize(8)  # Smaller font for text
        
        # Create color button for this object (smaller size)
        color_ax = plt.axes([0.55, y_pos, 0.1, 0.02])
        color_button = Button(color_ax, 'Color', color=self.current_color)
        
        # Store the entry and its associated color
        object_data = {
            'entry': entry,
            'color_button': color_button,
            'color': self.current_color,
            'active': True  # New object is active by default
        }
        
        # Deactivate previous objects
        for obj in self.object_entries:
            obj['active'] = False
            obj['entry'].label.set_color('black')  # Reset previous object label color
        
        self.object_entries.append(object_data)
        
        # Highlight active object
        entry.label.set_color(self.current_color)
        
        # Bind color button to color selection for this specific object
        color_button.on_clicked(lambda x, obj=object_data: self.choose_color_for_object(obj))
        
        # Bind click event to the text box for object selection
        entry.on_submit(lambda x, obj=object_data: self.select_object(obj))
        
        # Redraw the figure to show new controls
        self.current_fig.canvas.draw()

    def choose_color_for_object(self, object_data):
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta']
        color = simpledialog.askstring("Color Selection", 
                                     "Enter color name:\n" + ", ".join(colors))
        if color and color.lower() in colors:
            object_data['color'] = color.lower()
            # Update button color (optional visual feedback)
            object_data['color_button'].color = color.lower()
            self.current_fig.canvas.draw()

    def select_object(self, selected_obj):
        # Deactivate all objects and reset label colors
        for obj in self.object_entries:
            obj['active'] = False
            obj['entry'].label.set_color('black')
        
        # Activate selected object and highlight its label
        selected_obj['active'] = True
        selected_obj['entry'].label.set_color(selected_obj['color'])
        
        # Refresh the display
        self.current_fig.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.current_ax:
            return

        x, y = event.xdata, event.ydata
        
        # Get the currently active object
        active_object = None
        for obj in self.object_entries:
            if obj['active']:
                active_object = obj
                break
                
        if not active_object:
            return
            
        object_name = active_object['entry'].text
        
        # Initialize object if it doesn't exist
        if object_name not in self.object_points:
            self.object_points[object_name] = {'points': [], 'color': active_object['color']}
        
        # Add point to object
        self.object_points[object_name]['points'].append((x, y))
        
        # Plot cross (horizontal and vertical lines) at click position
        marker_size = 10
        line_width = 1
        color = active_object['color']
        
        # Draw the cross using two lines
        self.current_ax.plot([x-marker_size, x+marker_size], [y, y], 
                           color=color, linewidth=line_width)
        self.current_ax.plot([x, x], [y-marker_size, y+marker_size], 
                           color=color, linewidth=line_width)
        
        # Print coordinates
        print(f"Selected point for {object_name}: ({int(x)}, {int(y)})")
        
        # Refresh the plot
        self.current_fig.canvas.draw()

    def clear_points(self, event):
        # Find active object
        active_object = None
        for obj in self.object_entries:
            if obj['active']:
                active_object = obj
                break
        
        if not active_object:
            return
            
        object_name = active_object['entry'].text
        
        # Clear only the active object's points
        if object_name in self.object_points:
            self.object_points[object_name]['points'] = []
        
        # Redraw the frame with all points except the cleared object
        self.current_ax.clear()
        self.current_ax.imshow(self.current_frame)
        self.current_ax.axis('off')
        
        # Redraw remaining points for all objects
        for obj_name, obj_data in self.object_points.items():
            if obj_name != object_name:  # Skip the cleared object
                for x, y in obj_data['points']:
                    marker_size = 10
                    line_width = 1
                    color = obj_data['color']
                    
                    # Draw the cross using two lines
                    self.current_ax.plot([x-marker_size, x+marker_size], [y, y], 
                                       color=color, linewidth=line_width)
                    self.current_ax.plot([x, x], [y-marker_size, y+marker_size], 
                                       color=color, linewidth=line_width)
        
        self.current_fig.canvas.draw()

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

    def previous_frame(self):
        current_frame = int(self.frame_slider.get())
        if current_frame > 0:
            self.frame_slider.set(current_frame - 1)
            self.update_frame_number(current_frame - 1)

    def next_frame(self):
        current_frame = int(self.frame_slider.get())
        if current_frame < self.frame_count - 1:
            self.frame_slider.set(current_frame + 1)
            self.update_frame_number(current_frame + 1)

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
            
            # Read existing entries to avoid duplicates
            existing_entries = set()
            if os.path.exists(csv_filename):
                with open(csv_filename, 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        # Create a tuple of the key fields to check for duplicates
                        entry = (row[0], int(row[1]), row[2], int(row[3]), int(row[4]))
                        existing_entries.add(entry)
            
            # Open file in append mode if it exists, write mode if it doesn't
            mode = 'a' if os.path.exists(csv_filename) else 'w'
            new_points_added = 0
            
            with open(csv_filename, mode, newline='') as csvfile:
                writer = csv.writer(csvfile)
                if mode == 'w':  # Only write header for new files
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
