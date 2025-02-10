import eventlet
eventlet.monkey_patch()

import cv2
import base64
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit


# Flask setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# OpenCV video capture (Use 0 for USB camera, or change based on your setup)
cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def generate_video():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        # Apply OpenCV processing (optional)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Example: Convert to grayscale

        # Encode frame as base64 for sending
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to clients
        socketio.emit('video_stream', {'image': jpg_as_text})

        eventlet.sleep(0.05)  # Small delay to control frame rate

@socketio.on('motor_control')
def handle_motor_control(data):
    direction = data['direction']
    state = data['state']  # 'press' or 'release'

    print(f"Motor command: {direction} - {state}")

    # Here you would add actual motor control logic
    # Example:
    # if direction == "up" and state == "press":
    #     move_motor_up()
    # elif direction == "up" and state == "release":
    #     stop_motor()

@socketio.on('mouse_move')
def handle_mouse_move(data):
    print(f"Mouse moved: {data}")  # Logs mouse movement
    # socketio.emit('mouse_position', data)  # Broadcast position to all clients if needed


if __name__ == "__main__":
    eventlet.spawn(generate_video)  # Run video stream in a separate thread
    socketio.run(app, host="0.0.0.0", port=5000)
