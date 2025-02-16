import cv2
import mediapipe as mp
import numpy as np
import time

class ForeheadTracking:
    def __init__(self):
        # Initialize Mediapipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.1,
            min_tracking_confidence=0.1,
        )

        # Video Setup
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # FPS Control
        self.TARGET_FPS = 20
        self.FRAME_TIME = 1.0 / self.TARGET_FPS

        # Kalman Filter Setup (4 state variables: x, y, dx, dy)
        self.kalman = cv2.KalmanFilter(4, 2)

        # State transition matrix for constant velocity model
        self.kalman.transitionMatrix = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)

        self.kalman.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=np.float32)

        # Tune noise values
        self.kalman.processNoiseCov = np.diag([0.03, 0.03, 0.1, 0.1]).astype(np.float32)
        self.kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
        self.kalman.errorCovPost = np.eye(4, dtype=np.float32) * 1

        self.initialized = False
        self.prev_time = time.time()

    def track_forehead(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_results = self.face_mesh.process(rgb_frame)

        if last_results and last_results.multi_face_landmarks:
            for face_landmarks in last_results.multi_face_landmarks:
                ih, iw, _ = frame.shape
                forehead_landmark = face_landmarks.landmark[151]
                forehead_x, forehead_y = int(forehead_landmark.x * iw), int(forehead_landmark.y * ih)

                # Initialize Kalman state on first detection
                if not self.initialized:
                    self.kalman.statePost = np.array([forehead_x, forehead_y, 0, 0], dtype=np.float32)
                    self.initialized = True

                # Feed new measurement into Kalman
                measurement = np.array([[np.float32(forehead_x)], [np.float32(forehead_y)]])
                self.kalman.correct(measurement)

        if self.initialized:
            # Predict position using Kalman filter
            predicted = self.kalman.predict()
            predicted_x = int(predicted[0])
            predicted_y = int(predicted[1])

            # Draw red dot for predicted forehead position
            cv2.circle(frame, (predicted_x, predicted_y), 4, (0, 0, 255), -1)



        # Return the processed frame
        return frame
    
    def deconstruct(self):
        self.cap.release()
        cv2.destroyAllWindows()

