from simple_facerec import SimpleFacerec
import cv2
import numpy as np

# Initialize face recognition
sfr = SimpleFacerec()
sfr.load_encoding_images("faces/")  # Folder containing images of known people

frame_width, frame_height = 640, 480
center_x, center_y = frame_width // 2, frame_height // 2  # Center of the screen
fire_radius = 30  # Fire detection radius

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, frame_width)  # Set width
cap.set(4, frame_height)  # Set height

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw crosshair
    cv2.circle(frame, (center_x, center_y), radius=fire_radius, color=(255, 0, 0), thickness=1)

    # Detect faces
    face_locations, face_names = sfr.detect_known_faces(frame)

    # Find the closest face to the center
    closest_face = None
    min_distance = float('inf')

    for (top, right, bottom, left) in face_locations:
        face_center_x = (left + right) // 2
        face_center_y = (top + bottom) // 2
        distance = np.sqrt((center_x - face_center_x) ** 2 + (center_y - face_center_y) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_face = (left, top, right, bottom)

    # Fire status check
    status_text = ""

    if closest_face:
        face_left, face_top, face_right, face_bottom = closest_face
        face_center_x = (face_left + face_right) // 2
        face_center_y = (face_top + face_bottom) // 2

        # Condition 1: Closest face is within fire radius
        in_fire_radius = min_distance < fire_radius

        # Condition 2: Fire radius circle is entirely inside the face rectangle
        fire_circle_inside_face = (center_x - fire_radius >= face_left and
                                   center_x + fire_radius <= face_right and
                                   center_y - fire_radius >= face_top and
                                   center_y + fire_radius <= face_bottom)

        if in_fire_radius or fire_circle_inside_face:
            status_text = "FIRE"
        else:
            status_text = "MOVE"
            if face_center_x < center_x:
                status_text +=  " LEFT"
            if face_center_x > center_x:
                status_text += " RIGHT"
            if face_center_y < center_y:
                status_text += " UP"
            if face_center_y > center_y:
                status_text += " DOWN"

    # Draw rectangles around all faces
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        face_color = (0, 255, 0)  # Green by default
        if closest_face and (left, top, right, bottom) == closest_face:
            face_color = (0, 165, 255)  # Orange for closest face

        cv2.rectangle(frame, (left, top), (right, bottom), face_color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, face_color, 2)

    # Draw fire status
    cv2.putText(frame, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

