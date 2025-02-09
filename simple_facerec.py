import face_recognition
import cv2
import numpy as np
import os

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25  # Resize frame for faster processing

    def load_encoding_images(self, images_path):
        """
        Load face encodings from images in a directory.
        """
        for file in os.listdir(images_path):
            if file.startswith('.'):
                continue
            img_path = os.path.join(images_path, file)
            img = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(img)

            if encodings:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(os.path.splitext(file)[0])
            else:
                print(f"Warning: No face found in {file}")

    def detect_known_faces(self, frame):
        """
        Detect known faces in a given frame.
        """
        # Resize frame to speed up processing
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

            if face_distances is not None and len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        # Scale back face locations to match the original frame size
        face_locations = np.array(face_locations)
        face_locations = (face_locations / self.frame_resizing).astype(int)

        return face_locations, face_names
