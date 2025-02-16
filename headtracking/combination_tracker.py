import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.1)

# Video Setup
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# FPS Control
TARGET_FPS = 20
FRAME_TIME = 1.0 / TARGET_FPS

# Kalman Filter Setup (4 state variables: x, y, dx, dy)
kalman = cv2.KalmanFilter(4, 2)
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

kalman.processNoiseCov = np.diag([0.03, 0.03, 0.1, 0.1]).astype(np.float32)
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
kalman.errorCovPost = np.eye(4, dtype=np.float32) * 1

initialized = False
prev_time = time.time()

# Skip frame control
SKIP_FRAMES = 3
frame_counter = 0

while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    forehead_x, forehead_y = None, None

    if frame_counter % SKIP_FRAMES == 0:
        detection_results = mp_face_detection.process(rgb_frame)

        if detection_results.detections:
            detection = detection_results.detections[0]  # Take the first detected face
            bbox = detection.location_data.relative_bounding_box
            x, y, w, h = int(bbox.xmin * 320), int(bbox.ymin * 240), int(bbox.width * 320), int(bbox.height * 240)
            forehead_x = x + w // 2
            forehead_y = y + int(h * 0.2)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if forehead_x is not None and forehead_y is not None:
        if not initialized:
            kalman.statePost = np.array([forehead_x, forehead_y, 0, 0], dtype=np.float32)
            initialized = True

        measurement = np.array([[np.float32(forehead_x)], [np.float32(forehead_y)]])
        kalman.correct(measurement)

    if initialized:
        predicted = kalman.predict()
        predicted_x = int(predicted[0, 0])
        predicted_y = int(predicted[1, 0])

        cv2.circle(frame, (predicted_x, predicted_y), 4, (0, 0, 255), -1)

    current_time = time.time()
    fps = 1.0 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Kalman Filter - Face Detection Forehead Tracking", frame)

    elapsed_time = time.time() - start_time
    sleep_time = max(0, FRAME_TIME - elapsed_time)
    time.sleep(sleep_time)

    frame_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
