import streamlit as st
import cv2
import numpy as np

text = ""
# Initialize session state
if "direction" not in st.session_state:
    st.session_state["direction"] = "None"

# Camera movement function
def move_camera(direction):
    st.session_state["direction"] = direction
    print(f"Camera moving {direction}")  # Debugging output

# Stop movement function
def stop_camera():
    st.session_state["direction"] = "None"
    print("Camera stopped")  # Debugging output

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

# UI Layout for Video
stframe = st.empty()

# Create a form for controlling the camera
with st.form(key="camera_controls"):
    # Camera Control Buttons inside the form
    col1, col2, col3 = st.columns(3)
    with col2:
        move_up = st.form_submit_button("⬆️ Up")
    with col1:
        move_left = st.form_submit_button("⬅️ Left")
    with col3:
        move_right = st.form_submit_button("➡️ Right")

    col1, col2, col3 = st.columns(3)
    with col2:
        move_down = st.form_submit_button("⬇️ Down")

    # Handle button presses
    if move_up:
        move_camera("Up")
    elif move_left:
        move_camera("Left")
    elif move_right:
        move_camera("Right")
    elif move_down:
        move_camera("Down")

# Video Streaming Loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture video")
        break

    # Convert BGR (OpenCV) to RGB (Streamlit)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Add text overlay
    cv2.putText(
        frame,
        f"Live Feed - Direction: {st.session_state['direction']}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2,
        cv2.LINE_AA,
    )

    # Display Video
    stframe.image(frame, channels="RGB", use_column_width=True)

cap.release()

