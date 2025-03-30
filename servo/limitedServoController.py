import RPi.GPIO as GPIO
import time
import threading

class LimitedServoController:
    def __init__(self, pin, initial_angle=90):
        """
        Initializes a servo motor on the given GPIO pin.
        :param pin: GPIO pin connected to the servo.
        :param initial_angle: The starting position of the servo.
        """
        self.pin = pin
        self.current_angle = initial_angle
        self.lock = threading.Lock()

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        # Set up PWM with 50Hz frequency
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)

        # Move to the initial angle
        self.set_angle(self.current_angle)

    def set_angle(self, angle):
        """
        Moves the servo to a specified angle.
        :param angle: Target angle between 0 and 180 degrees.
        """
        if not 0 <= angle <= 180:
            print("negative", angle)
            return
        acquired = self.lock.acquire(blocking=False)

        print("setting_angle")
        if acquired:
            try:
                print("acquired and running")
                """
                time.sleep(1)
                """
                duty_cycle = (angle / 180) * (12.5 - 2.5) + 2.5
                self.pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(0.5)  # Adjust time based on servo speed
                self.pwm.ChangeDutyCycle(0)  # Stop sending signal to reduce jitter

                self.current_angle = angle  # Store current position
            finally:
                print("released")
                self.lock.release()
        else:
            print("skipped")
        print()

    def move_slowly(self, target_angle, step=1, delay=0.05):
        """
        Gradually moves the servo from the current angle to the target angle.
        :param target_angle: The desired angle to move to.
        :param step: The increment for each movement step.
        :param delay: Delay between each step for smooth movement.
        """
        if self.current_angle < target_angle:
            for angle in range(self.current_angle, target_angle + 1, step):
                self.set_angle(angle)
                time.sleep(delay)
        else:
            for angle in range(self.current_angle, target_angle - 1, -step):
                self.set_angle(angle)
                time.sleep(delay)

        self.current_angle = target_angle  # Update stored angle

    def cleanup(self):
        """Stops the PWM and cleans up GPIO."""
        self.pwm.stop()
        GPIO.cleanup()

    def __del__(self):
        """Ensures cleanup when the object is deleted."""
        self.cleanup()
