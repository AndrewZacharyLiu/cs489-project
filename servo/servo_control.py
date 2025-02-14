from gpiozero import Servo
from time import sleep

class ContinuousServoController:
    def __init__(self, pin):
        self.servo = Servo(pin, min_pulse_width=1/1000, max_pulse_width=2/1000)
        self.servo.value = None
        self.lastPos = -1

    def move(self, direction, speed=1.0):
        """Controls the servo motor.

        :param direction: 'forward' or 'backward'
        :param speed: A float between 0 and 1 (default is 1.0)
        """
        if direction == "forward":
            self.servo.value = min(1, max(0, speed*1.5))  # Clamp speed to 0-1
        elif direction == "backward":
            self.servo.value = -min(1, max(0, speed)) # Reverse direction
        else:
            print("Invalid direction. Use 'forward' or 'backward'.")

    def stop(self):
        """Stops the servo motor."""
        self.servo.value = None  # Sets to neutral position (stop)

if __name__ == "__main__":
    motor = ContinuousServoController(18)

    try:
        while True:
            cmd = input("Enter command (f/b/stop/exit): ").strip().lower()
            if cmd == "f":
                speed = float(input("Enter speed (0-1): "))
                motor.move("forward", speed)
            elif cmd == "b":
                speed = float(input("Enter speed (0-1): "))
                motor.move("backward", speed)
            elif cmd == "stop":
                motor.stop()
            elif cmd == "exit":
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        print("\nStopping motor.")
    finally:
        motor.stop()
