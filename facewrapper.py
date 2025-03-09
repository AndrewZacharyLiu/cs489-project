
from deepfacetest import FaceRecognition
import cv2
tracker = FaceRecognition()

while True:
    frame, status = tracker.recognize_faces()
    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


tracker.release()