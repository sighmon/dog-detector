# Dog detector

A Python Supervision/Open CV/YOLO dog detector, which records videos when it sees dogs walking by.

## Usage

* Build and run: `make`
* Run: `make run`
* Delete your `venv` folder: `make clean`

To run with debug output: `DEBUG=true python app.py`

Sample output:

```bash
Serving videos on http://0.0.0.0:8000
Dog detected!
Recording started: /home/pi/code/dog/videos/dog_detected_20241119_222621.mp4
No dog detected. Stopping recording.
Recording stopped.
```

## Videos

When a dog is detected a video will be recorded in `videos/` for 3 seconds after the dog has gone.

You can visit your videos at: http://raspberrypi.local:8000

