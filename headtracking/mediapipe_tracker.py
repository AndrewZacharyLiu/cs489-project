import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.1,
    min_tracking_confidence=0.1,
)

# Video Setup
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# FPS Control
TARGET_FPS = 20
FRAME_TIME = 1.0 / TARGET_FPS

frame_count = 0
last_results = None

# Kalman Filter Setup (4 state variables: x, y, dx, dy)
kalman = cv2.KalmanFilter(4, 2)

# State transition matrix for constant velocity model
kalman.transitionMatrix = np.array([
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
], dtype=np.float32)

kalman.measurementMatrix = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
], dtype=np.float32)

# Tune noise values
kalman.processNoiseCov = np.diag([0.03, 0.03, 0.1, 0.1]).astype(np.float32)
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
kalman.errorCovPost = np.eye(4, dtype=np.float32) * 1

initialized = False
prev_time = time.time()

while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % 3 == 0:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_results = face_mesh.process(rgb_frame)

    if last_results and last_results.multi_face_landmarks:
        for face_landmarks in last_results.multi_face_landmarks:
            ih, iw, _ = frame.shape
            forehead_landmark = face_landmarks.landmark[151]
            forehead_x, forehead_y = int(forehead_landmark.x * iw), int(forehead_landmark.y * ih)

            # Initialize Kalman state on first detection
            if not initialized:
                kalman.statePost = np.array([forehead_x, forehead_y, 0, 0], dtype=np.float32)
                initialized = True

            # Feed new measurement into Kalman
            measurement = np.array([[np.float32(forehead_x)], [np.float32(forehead_y)]])
            kalman.correct(measurement)

    if initialized:
        # Predict position using Kalman filter
        predicted = kalman.predict()
        predicted_x = int(predicted[0])
        predicted_y = int(predicted[1])

        # Draw red dot for predicted forehead position
        cv2.circle(frame, (predicted_x, predicted_y), 4, (0, 0, 255), -1)

    # FPS Display
    current_time = time.time()
    fps = 1.0 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Kalman Filter - Constant Velocity (Forehead Tracking)", frame)

    # FPS Limiter
    elapsed_time = time.time() - start_time
    sleep_time = max(0, FRAME_TIME - elapsed_time)
    time.sleep(sleep_time)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

