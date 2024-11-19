import threading
import queue
import cv2
import os
import http.server
import socketserver
import supervision as sv
from ultralytics import YOLO
from datetime import datetime, timedelta
import time
import logging


# Global variables
recording_flag = threading.Event()  # Shared flag for recording
frame_queue = queue.Queue(maxsize=10)  # Frame queue for detection
record_until = None  # Timer to ensure recording lasts at least 3 seconds

# Check the DEBUG environment variable
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Suppress YOLO logging
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# Load YOLO model
model = YOLO('yolov8n.pt')

# Initialize VideoWriter settings
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30.0  # Adjust to your camera's actual FPS

# Directory to save videos
video_dir = os.path.abspath("videos")  # Use an absolute path
os.makedirs(video_dir, exist_ok=True)


def detection_thread():
    """Thread for performing YOLO detection."""
    global record_until
    recording_state = False  # Track the current recording state to avoid repeated logs
    frame_counter = 0  # Counter to process every 10th frame

    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame_counter += 1

            # Skip frames for detection
            if frame_counter % 10 != 0:
                continue

            results = model(frame)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Check if a dog (class_id 16) is detected
            if 16 in detections.class_id:
                if DEBUG and not recording_state:
                    print("Dog detected!")
                record_until = datetime.now() + timedelta(seconds=3)  # Extend recording time
                recording_flag.set()
                recording_state = True  # Update the state to indicate recording

            elif record_until and datetime.now() > record_until:
                # Stop recording if the timer expires
                if DEBUG and recording_state:
                    print("No dog detected. Stopping recording.")
                recording_flag.clear()
                recording_state = False  # Update the state to indicate not recording


def recording_thread():
    """Thread for real-time video recording."""
    cap = cv2.VideoCapture(0)
    out = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Push frame to the queue for detection
        if frame_queue.qsize() < frame_queue.maxsize:
            frame_queue.put(frame)

        # Start recording if the flag is set
        if recording_flag.is_set():
            if out is None:  # Initialize VideoWriter
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = os.path.join(video_dir, f'dog_detected_{timestamp}.mp4')  # Use absolute path
                out = cv2.VideoWriter(filepath, fourcc, fps, (frame.shape[1], frame.shape[0]))
                if DEBUG:
                    print(f"Recording started: {filepath}")
            out.write(frame)
        else:
            # Stop recording if the flag is cleared
            if out is not None:
                if DEBUG:
                    print("Recording stopped.")
                out.release()
                out = None

    # Cleanup
    cap.release()
    if out is not None:
        out.release()


def server_thread():
    """Thread for serving the video directory."""
    os.chdir(video_dir)  # Change directory to the video folder
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", 8000), handler) as httpd:
        print("Serving videos on http://0.0.0.0:8000")
        httpd.serve_forever()


# Start threads
detection = threading.Thread(target=detection_thread, daemon=True)
recording = threading.Thread(target=recording_thread, daemon=True)
server = threading.Thread(target=server_thread, daemon=True)

detection.start()
recording.start()
server.start()

# Let threads run indefinitely
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping threads.")

