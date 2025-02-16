import cv2
import numpy as np
import tensorflow as tf
from scipy.spatial.distance import cosine
from tensorflow.keras.models import load_model
from PIL import Image
import os

# Load FaceNet model (Pre-trained model from Keras-FaceNet)
model = load_model("facenet_keras.h5", compile=False)

# Load OpenCV face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Function to preprocess image for FaceNet
def preprocess_face(face):
    face = cv2.resize(face, (160, 160))  # FaceNet input size
    face = face.astype("float32") / 255.0  # Normalize
    face = np.expand_dims(face, axis=0)  # Add batch dimension
    return face

# Function to get embedding
def get_embedding(face):
    return model.predict(preprocess_face(face))[0]

# Load reference images and their embeddings
folder_path = "faces/"
target_faces_embeddings = []
image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg'))]

for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    reference_img = cv2.imread(image_path)
    if reference_img is None:
        print(f"Error: Failed to load {image_file}")
        continue
    reference_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    reference_faces = face_cascade.detectMultiScale(reference_gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    if len(reference_faces) == 0:
        print(f"No face found in {image_file}!")
        continue
    x, y, w, h = reference_faces[0]
    reference_face = reference_img[y:y+h, x:x+w]
    reference_embedding = get_embedding(reference_face)
    
    # Store both the embedding and the filename
    target_faces_embeddings.append((reference_embedding, image_file))

if len(target_faces_embeddings) == 0:
    print("No face found in reference folder!")
    exit()

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Draw rectangle around detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop detected face
        detected_face = frame[y:y + h, x:x + w]

        try:
            detected_embedding = get_embedding(detected_face)

            # Initialize a variable to track the max similarity and the corresponding reference image
            max_similarity = -1  # Similarity ranges from 0 to 1, so -1 ensures any score will be higher
            best_match_filename = None  # Keeps track of the best matching reference image filename

            # Loop through all target face embeddings to find the max similarity
            for reference_embedding, image_filename in target_faces_embeddings:
                similarity = 1 - cosine(reference_embedding, detected_embedding)  # Cosine similarity
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_filename = image_filename  # Update with the filename of the best match

            # Set threshold (0.5-0.7 is usually a good range)
            threshold = 0.5
            recognized = max_similarity > threshold

            # Display result
            label = best_match_filename if recognized else "No Match"
            color = (0, 255, 0) if recognized else (0, 0, 255)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Optionally, you can also print the highest similarity score and the corresponding reference image filename
            print(f"Max Similarity Score: {max_similarity:.2f}")
    
        except Exception as e:
            print("FaceNet error:", e)

    # Display the frame
    cv2.imshow("Face Recognition", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
