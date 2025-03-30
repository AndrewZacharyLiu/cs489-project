import eventlet
eventlet.monkey_patch()

import cv2
import base64
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from headtracking.mediapipe_copy import ForeheadTracking
from servo.limitedServoController import LimitedServoController
from servo.servo_control import ContinuousServoController

last_mouse_move_time = None
MOUSE_TIMEOUT = 0.15
angle = 90
video_tracking = True

# Flask setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

tracker = ForeheadTracking()
frame_count = 0
motorX = LimitedServoController(14)
motorY = LimitedServoController(18)

lastX = 0
lastY = 0

# OpenCV video capture (Use 0 for USB camera, or change based on your setup)
#cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')




def generate_video():
    global angle
    global video_tracking
    while True:
        frame, command = tracker.track_forehead()
        if frame is None:
            print("[WARN] No frame captured")
            continue
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('video_stream', {'image': jpg_as_text})
        if (video_tracking and command):
            move_turret(command.split(','))
        eventlet.sleep(0.02)  # 20 FPS cap



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
            motorY.move_slowly(230, 5, 0.2)


@socketio.on('mouse_move')
def handle_mouse_move(data):
    #print(f"Mouse moved: {data}")  # Logs mouse movement
    # socketio.emit('mouse_position', data)  # Broadcast position to all clients if needed

    global last_mouse_move_time
    last_mouse_move_time = time.time()
#    last_mouse_move_time = time.monotonic()

    global motorX
    global motorY

    global lastX
    global lastY

    difX = lastX - data['x']
    difY = lastY - data['y']

    lastX = data['x']
    lastY = data['y']
    print("moving")
    motorX.move_slowly(motorX.current_angle + (difX * 5), 1, 0.05)
    motorY.move_slowly(motorY.current_angle + (difY * 5), 1, 0.05)


    #motorX.current_angle
    """
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
    """

def stop_motor_if_idle():
    global last_mouse_move_time
    """
    while True:
        eventlet.sleep(MOUSE_TIMEOUT)
#        if last_mouse_move_time and (time.monotonic() - last_mouse_move_time > MOUSE_TIMEOUT):
        if last_mouse_move_time and (time.time() - last_mouse_move_time > MOUSE_TIMEOUT):
            motorX.stop()
            last_mouse_move_time = None
    """

def move_turret(command_array):
    global frame_count
    frame_count += 1
    if frame_count % 3 != 0:
        return
    global motorX
    global motorY

    if (command_array is None or len(command_array) <= 0):
        return
    if (command_array[0] == "Fire"):
        print("Fire") # TODO: replace with actual fire logic
        return
    if (command_array[0] == "Left"):
        #print("left")
        thread_left = threading.Thread(target=motorX.set_angle, args=(motorX.current_angle - int(command_array[1]),))
        thread_left.start()
    elif (command_array[0] == "Right"):
        #print("right")
        thread_right = threading.Thread(target=motorX.set_angle, args=(motorX.current_angle + int(command_array[1]),))
        thread_right.start()
    if (command_array[2] == "Up"):
        thread_up = threading.Thread(target=motorY.set_angle, args=(motorY.current_angle + int(command_array[1]),))
        thread_up.start()
    elif (command_array[2] == "Down"):
        thread_down = threading.Thread(target=motorY.set_angle, args=(motorY.current_angle - int(command_array[1]),))
        thread_down.start()


if __name__ == "__main__":
    eventlet.spawn(generate_video)  # Run video stream in a separate thread
    #motorX = ContinuousServoController(18)
    #motorY = LimitedServoController(23)
    eventlet.spawn(stop_motor_if_idle)
    print("starting run")
    socketio.run(app, host="0.0.0.0", port=5000)