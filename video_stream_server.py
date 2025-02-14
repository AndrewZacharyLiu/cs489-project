import eventlet
eventlet.monkey_patch()

#import cv2
import base64
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

from servo.servo_control import ContinuousServoController

last_mouse_move_time = None
MOUSE_TIMEOUT = 0.15


# Flask setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# OpenCV video capture (Use 0 for USB camera, or change based on your setup)
#cap = cv2.VideoCapture(0)

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


    if direction == "left" or direction == "right":
        if state == "release":
            motorX.stop()
        else:
            if direction == "left":
                direction = "backward"
            else:
                direction = "forward"
            motorX.move(direction, 0.5)
    else:
        if state == "release":
            #motorY.stop()
            pass
        else:
            if direction == "down":
                direction = "backward"
            else:
                direction = "forward"
            #motorY.move(direction, 0.5)


@socketio.on('mouse_move')
def handle_mouse_move(data):
    #print(f"Mouse moved: {data}")  # Logs mouse movement
    # socketio.emit('mouse_position', data)  # Broadcast position to all clients if needed

    global last_mouse_move_time
    last_mouse_move_time = time.time()
#    last_mouse_move_time = time.monotonic()

    if data['x'] == motorX.lastPos:
        motorX.stop()
    else:
        if motorX.lastPos >= 0:
            dif = motorX.lastPos - data['x']
            print(dif)
            if dif > 0:
                direction = "forward"
            else:
                direction = "backward"

            dif = abs(dif)
            if dif == 1:
                speedX = 0.1
                if direction == "forward":
                    speedX = 0.25
                else:
                    speedX = 0.1
            elif dif == 2:
                if direction == "forward":
                    speedX = 0.75
                else:
                    speedX = 0.5
            elif dif >= 3:
                if direction == "forward":
                    speedX = 1
                else:
                    speedX = 0.9
            print(dif)
            print(speedX)
            motorX.move(direction, speedX)
        motorX.lastPos = data['x']

def stop_motor_if_idle():
    global last_mouse_move_time
    while True:
        eventlet.sleep(MOUSE_TIMEOUT)
#        if last_mouse_move_time and (time.monotonic() - last_mouse_move_time > MOUSE_TIMEOUT):
        if last_mouse_move_time and (time.time() - last_mouse_move_time > MOUSE_TIMEOUT):
            motorX.stop()
            last_mouse_move_time = None


if __name__ == "__main__":
    #eventlet.spawn(generate_video)  # Run video stream in a separate thread
    motorX = ContinuousServoController(18)
    eventlet.spawn(stop_motor_if_idle)
    print("starting run")
    socketio.run(app, host="0.0.0.0", port=5000)
