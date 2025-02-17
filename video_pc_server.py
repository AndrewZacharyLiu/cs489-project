import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import base64
import time
import numpy as np
from headtracking.mediapipe_copy import ForeheadTracking  # Your class from the first part

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

tracker = ForeheadTracking()

@app.route('/')
def index():
    return render_template('index.html')

def generate_video():
    while True:
        frame, command = tracker.track_forehead()
        if frame is None:
            print("[WARN] No frame captured")
            continue
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('video_stream', {'image': jpg_as_text})
        eventlet.sleep(0.02)  # 20 FPS cap

if __name__ == '__main__':
    eventlet.spawn(generate_video)
    print("starting run")
    socketio.run(app, host='0.0.0.0', port=5000)
