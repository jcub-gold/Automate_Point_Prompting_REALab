# Automate_Point_Prompting_REALab
Assignment #2: Automating Point Prompting For Video Segmentation 

## Video Frame Selector

A Python application for selecting and annotating frames from video files built with Tkinter and Matplotlib. Users can navigate through video frames, mark points on objects, and save the annotations to CSV files.

## Technical Components

- **Python 3.x**
- **OpenCV (cv2)**: Video processing and frame extraction
- **Tkinter**: Main GUI framework
- **Matplotlib**: Interactive frame display and point annotation
- **NumPy**: Image processing support
- **CSV**: Data storage for annotations

## Features

- Load and navigate through video files
- Frame-by-frame navigation using slider or arrow keys
- Add multiple objects with customizable colors
- Mark points on objects in frames
- Save annotations to CSV files
- Clear points for individual objects
- Automatic duplicate entry prevention

## Installation

1. Clone the repository
2. Install required packages:

## Usage

1. Run the application:
```bash
python app.py
```

2. Click "Select Video File" to load a video
3. Use the slider or arrow keys to navigate through frames
4. Click "View Frame" to open the annotation window
5. Add objects using the '+' button
6. Select points by clicking on the frame
7. Save annotations using the 'Save' button

## Output

Annotations are saved in `annotations/<video_name>/points.csv` with the following format:
- video_name
- frame_number
- object_name
- x
- y