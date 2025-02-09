import curses
import RPi.GPIO as GPIO
import time
import sys

# Define GPIO pins connected to the stepper motor
IN1_1 = 14
IN2_1 = 15
IN3_1 = 18
IN4_1 = 23

IN1_2 = 24
IN2_2 = 25
IN3_2 = 8
IN4_2 = 7

# Define the GPIO pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up the GPIO pins as outputs
GPIO.setup(IN1_1, GPIO.OUT)
GPIO.setup(IN2_1, GPIO.OUT)
GPIO.setup(IN3_1, GPIO.OUT)
GPIO.setup(IN4_1, GPIO.OUT)

GPIO.setup(IN1_2, GPIO.OUT)
GPIO.setup(IN2_2, GPIO.OUT)
GPIO.setup(IN3_2, GPIO.OUT)
GPIO.setup(IN4_2, GPIO.OUT)

# Define step sequence for full-step drive
STEP_SEQUENCE = [
    [1, 0, 0, 1],  # Step 1
    [1, 0, 0, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [0, 1, 0, 0],  # Step 4
    [0, 1, 1, 0],  # Step 5
    [0, 0, 1, 0],  # Step 6
    [0, 0, 1, 1],  # Step 7
    [0, 0, 0, 1]   # Step 8
]

# Function to rotate the motor
def rotate_motor(direction, steps, IN1, IN2, IN3, IN4):
    if direction not in ["clockwise", "counterclockwise"]:
        print("Invalid direction. Choose 'clockwise' or 'counterclockwise'.")
        return

    if direction == "counterclockwise":
        STEP_SEQUENCE.reverse()  # Reverse the order of steps for counterclockwise rotation

    for step in range(steps):
        for phase in STEP_SEQUENCE:
            GPIO.output(IN1, phase[0])
            GPIO.output(IN2, phase[1])
            GPIO.output(IN3, phase[2])
            GPIO.output(IN4, phase[3])
            time.sleep(0.0008)  # Delay for motor step (adjust speed by changing the delay)

    if direction == "counterclockwise":
        STEP_SEQUENCE.reverse()


def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Disable cursor and enable keypad
    curses.curs_set(0)

    while True:
        # Get user input without waiting for Enter
        key = stdscr.getch()

        if key == curses.KEY_LEFT:
            # Left arrow key pressed, run this loop
            rotate_motor("counterclockwise", 5, IN1_1, IN2_1, IN3_1, IN4_1)
            stdscr.clear()
            stdscr.addstr(0, 0, "Left Arrow Key Loop Running...")
            stdscr.refresh()

        elif key == curses.KEY_RIGHT:
            # Right arrow key pressed, run this loop
            rotate_motor("clockwise", 5, IN1_1, IN2_1, IN3_1, IN4_1)
            stdscr.clear()
            stdscr.addstr(0, 0, "Right Arrow Key Loop Running...")
            stdscr.refresh()
        elif key == curses.KEY_UP:
            rotate_motor("counterclockwise", 5, IN1_2, IN2_2, IN3_2, IN4_2)
            stdscr.clear()
            stdscr.addstr(0, 0, "Up Arrow Key Loop Running...")
            stdscr.refresh()
        elif key == curses.KEY_DOWN:
            rotate_motor("clockwise", 5, IN1_2, IN2_2, IN3_2, IN4_2)
            stdscr.clear()
            stdscr.addstr(0, 0, "Down Arrow Key Loop Running...")
            stdscr.refresh()
        elif key == 27:  # Escape key to exit the program
            break

# Initialize curses
curses.wrapper(main)
