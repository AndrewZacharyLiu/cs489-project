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
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # Determine center point
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.center = (self.frame_width // 2, self.frame_height // 2)

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
        self.frame_count = 0
        self.rgb_frame = None
        self.last_results = None

    def calculate_degree_offset(predicted_y, center_y, frame_height=240, vertical_fov=55.8):
        degrees_per_pixel = vertical_fov / frame_height
        degree_offset = (predicted_y - center_y) * degrees_per_pixel
        return abs(degree_offset)

    def track_forehead(self):
        start_time = time.time()
        command = ""
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_count += 1

        if self.frame_count % 3 == 0:
            self.rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.last_results = self.face_mesh.process(self.rgb_frame)

        if self.last_results and self.last_results.multi_face_landmarks:
            for face_landmarks in self.last_results.multi_face_landmarks:
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

        if self.initialized and self.last_results and self.last_results.multi_face_landmarks:
            # Predict position using Kalman filter
            predicted = self.kalman.predict()
            predicted_x = int(predicted[0])
            predicted_y = int(predicted[1])

            # Draw red dot for predicted forehead position
            cv2.circle(frame, (predicted_x, predicted_y), 4, (0, 0, 255), -1)

            #draw crosshair
            cv2.circle(frame, self.center, 10, (255, 0, 0), 2)
            center_x, center_y = self.center
            distance = np.sqrt((predicted_x - center_x) ** 2 + (predicted_y - center_y) ** 2)

            if distance < 10:
                command += "Fire"
            else:
                if predicted_x < center_x:
                    command += "Left,"
                elif predicted_x > center_x:
                    command += "Right,"
                else:
                    command += "XGood,"
                
                if predicted_y < center_y:
                    command += "Up," + str(self.calculate_degree_offset(predicted_y, center_y))
                elif predicted_y > center_y:
                    command += "Down," + str(self.calculate_degree_offset(predicted_y, center_y))
                else:
                    command += "YGood"
            cv2.putText(frame, command, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        # FPS Display
        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        

        #cv2.imshow("Kalman Filter - Constant Velocity (Forehead Tracking)", frame)

        # FPS Limiter
        #elapsed_time = time.time() - start_time
        #sleep_time = max(0, FRAME_TIME - elapsed_time)
        #time.sleep(sleep_time)



        # Return the processed frame
        return frame, command
    
    def deconstruct(self):
        self.cap.release()
        cv2.destroyAllWindows()

