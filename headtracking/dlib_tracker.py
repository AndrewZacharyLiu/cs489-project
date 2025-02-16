import cv2
import dlib

# Load face detector (HOG or CNN)
detector = dlib.get_frontal_face_detector()

# Load pre-trained facial landmark predictor (68 points)
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # Forehead approximation (Manually chosen based on 68 landmarks)
        forehead_x = (landmarks.part(21).x + landmarks.part(22).x) // 2
        forehead_y = landmarks.part(21).y - 20  # Roughly above the eyebrows

        # Draw forehead dot
        cv2.circle(frame, (forehead_x, forehead_y), 4, (0, 0, 255), -1)

        # Optional: Draw all 68 landmarks
        for n in range(68):
            x, y = landmarks.part(n).x, landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    cv2.imshow("Landmarks", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
