"""
Motor Control Module for Lunar Rover
Handles GPIO motor control for Raspberry Pi
"""

try:
    import RPi.GPIO as GPIO
    print("Running on Raspberry Pi - Using hardware GPIO")
except (ImportError, RuntimeError):
    import gpio_simulator as GPIO
    print("Running in SIMULATOR mode - No actual GPIO control")

import time
from typing import Optional
import config


class MotorController:
    """Controls the rover's motors via GPIO pins"""
    
    def __init__(self):
        """Initialize GPIO pins and PWM for motor control"""
        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup motor pins as outputs
        self.pins = [
            config.MOTOR_LEFT_FORWARD,
            config.MOTOR_LEFT_BACKWARD,
            config.MOTOR_RIGHT_FORWARD,
            config.MOTOR_RIGHT_BACKWARD
        ]
        
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Setup PWM for speed control
        self.pwm_left_forward = GPIO.PWM(config.MOTOR_LEFT_FORWARD, config.PWM_FREQUENCY)
        self.pwm_left_backward = GPIO.PWM(config.MOTOR_LEFT_BACKWARD, config.PWM_FREQUENCY)
        self.pwm_right_forward = GPIO.PWM(config.MOTOR_RIGHT_FORWARD, config.PWM_FREQUENCY)
        self.pwm_right_backward = GPIO.PWM(config.MOTOR_RIGHT_BACKWARD, config.PWM_FREQUENCY)
        
        # Start all PWM at 0
        self.pwm_left_forward.start(0)
        self.pwm_left_backward.start(0)
        self.pwm_right_forward.start(0)
        self.pwm_right_backward.start(0)
        
        self.current_speed = config.DEFAULT_SPEED
        print(f"Motor controller initialized. Speed: {self.current_speed}%")
    
    def stop(self):
        """Stop all motors"""
        try:
            self.pwm_left_forward.ChangeDutyCycle(0)
            self.pwm_left_backward.ChangeDutyCycle(0)
            self.pwm_right_forward.ChangeDutyCycle(0)
            self.pwm_right_backward.ChangeDutyCycle(0)
            print("Motors stopped")
        except Exception as e:
            print(f"⚠ Error stopping motors: {e}")
    
    def forward(self, duration: Optional[float] = None, speed: Optional[int] = None):
        """Move forward"""
        try:
            speed = speed or self.current_speed
            self.stop()
            self.pwm_left_forward.ChangeDutyCycle(speed)
            self.pwm_right_forward.ChangeDutyCycle(speed)
            print(f"Moving forward at {speed}% speed")
            
            if duration:
                time.sleep(duration)
                self.stop()
        except Exception as e:
            print(f"⚠ Error in forward movement: {e}")
            self.stop()
    
    def backward(self, duration: Optional[float] = None, speed: Optional[int] = None):
        """Move backward"""
        try:
            speed = speed or self.current_speed
            self.stop()
            self.pwm_left_backward.ChangeDutyCycle(speed)
            self.pwm_right_backward.ChangeDutyCycle(speed)
            print(f"Moving backward at {speed}% speed")
        except Exception as e:
            print(f"⚠ Error in backward movement: {e}")
            self.stop()
        
        if duration:
            time.sleep(duration)
            self.stop()
    
    def left(self, duration: Optional[float] = None, speed: Optional[int] = None):
        """Turn left (left motor backward, right motor forward)"""
        speed = speed or self.current_speed
        self.stop()
        self.pwm_left_backward.ChangeDutyCycle(speed)
        self.pwm_right_forward.ChangeDutyCycle(speed)
        print(f"Turning left at {speed}% speed")
        
        if duration:
            time.sleep(duration)
            self.stop()
    
    def right(self, duration: Optional[float] = None, speed: Optional[int] = None):
        """Turn right (left motor forward, right motor backward)"""
        speed = speed or self.current_speed
        self.stop()
        self.pwm_left_forward.ChangeDutyCycle(speed)
        self.pwm_right_backward.ChangeDutyCycle(speed)
        print(f"Turning right at {speed}% speed")
        
        if duration:
            time.sleep(duration)
            self.stop()
    
    def set_speed(self, speed: int):
        """Set the default speed (0-100)"""
        self.current_speed = max(0, min(100, speed))
        print(f"Speed set to {self.current_speed}%")
    
    def cleanup(self):
        """Clean up GPIO pins"""
        self.stop()
        self.pwm_left_forward.stop()
        self.pwm_left_backward.stop()
        self.pwm_right_forward.stop()
        self.pwm_right_backward.stop()
        GPIO.cleanup()
        print("GPIO cleanup complete")
