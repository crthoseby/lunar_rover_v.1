"""
Servo Controller for SG90 9g Micro Servos
Controls camera pan/tilt servos
"""

import time
import config

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    import gpio_simulator as GPIO
    GPIO_AVAILABLE = False
    print("⚠ Using GPIO simulator for servo control")


class ServoController:
    """Control SG90 servos for camera pan/tilt"""
    
    def __init__(self):
        """Initialize servo controller"""
        self.pan_pin = config.SERVO_CAMERA_PAN_PIN
        self.tilt_pin = config.SERVO_CAMERA_TILT_PIN
        self.frequency = config.SERVO_FREQUENCY
        
        # Current positions
        self.pan_angle = config.SERVO_CENTER
        self.tilt_angle = config.SERVO_CENTER
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pan_pin, GPIO.OUT)
        GPIO.setup(self.tilt_pin, GPIO.OUT)
        
        # Create PWM instances
        self.pan_pwm = GPIO.PWM(self.pan_pin, self.frequency)
        self.tilt_pwm = GPIO.PWM(self.tilt_pin, self.frequency)
        
        # Start PWM at center position
        self.pan_pwm.start(self._angle_to_duty_cycle(config.SERVO_CENTER))
        self.tilt_pwm.start(self._angle_to_duty_cycle(config.SERVO_CENTER))
        
        print(f"✓ Servo controller initialized (Pan: GPIO{self.pan_pin}, Tilt: GPIO{self.tilt_pin})")
    
    def _angle_to_duty_cycle(self, angle):
        """
        Convert angle (0-180) to duty cycle percentage
        SG90: 0° = 2.5% duty, 90° = 7.5% duty, 180° = 12.5% duty
        """
        # Clamp angle to valid range
        angle = max(config.SERVO_MIN_ANGLE, min(config.SERVO_MAX_ANGLE, angle))
        
        # Map angle to duty cycle (2.5% - 12.5%)
        duty = 2.5 + (angle / 180.0) * 10.0
        return duty
    
    def set_pan(self, angle):
        """
        Set pan servo angle (0-180 degrees)
        90 = center, 0 = full left, 180 = full right
        """
        try:
            angle = max(config.SERVO_MIN_ANGLE, min(config.SERVO_MAX_ANGLE, angle))
            self.pan_angle = angle
            duty = self._angle_to_duty_cycle(angle)
            self.pan_pwm.ChangeDutyCycle(duty)
            time.sleep(0.3)  # Allow servo to move
            self.pan_pwm.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter
            print(f"[SERVO] Pan set to {angle}°")
        except Exception as e:
            print(f"⚠ Error setting pan servo: {e}")
    
    def set_tilt(self, angle):
        """
        Set tilt servo angle (0-180 degrees)
        90 = center, 0 = down, 180 = up
        """
        try:
            angle = max(config.SERVO_MIN_ANGLE, min(config.SERVO_MAX_ANGLE, angle))
            self.tilt_angle = angle
            duty = self._angle_to_duty_cycle(angle)
            self.tilt_pwm.ChangeDutyCycle(duty)
            time.sleep(0.3)  # Allow servo to move
            self.tilt_pwm.ChangeDutyCycle(0)  # Stop sending signal
            print(f"[SERVO] Tilt set to {angle}°")
        except Exception as e:
            print(f"⚠ Error setting tilt servo: {e}")
    
    def set_position(self, pan, tilt):
        """Set both pan and tilt angles simultaneously"""
        self.set_pan(pan)
        self.set_tilt(tilt)
    
    def center(self):
        """Return servos to center position"""
        self.set_position(config.SERVO_CENTER, config.SERVO_CENTER)
        print("[SERVO] Centered")
    
    def scan(self, steps=5, delay=0.5):
        """Perform a scanning motion (pan left-right while centered)"""
        original_pan = self.pan_angle
        angles = []
        
        # Generate scan angles
        for i in range(steps):
            angle = config.SERVO_MIN_ANGLE + (i * (config.SERVO_MAX_ANGLE - config.SERVO_MIN_ANGLE) / (steps - 1))
            angles.append(angle)
        
        # Scan right
        for angle in angles:
            self.set_pan(angle)
            time.sleep(delay)
        
        # Scan left
        for angle in reversed(angles):
            self.set_pan(angle)
            time.sleep(delay)
        
        # Return to original position
        self.set_pan(original_pan)
        print("[SERVO] Scan complete")
    
    def get_position(self):
        """Get current servo positions"""
        return {
            'pan': self.pan_angle,
            'tilt': self.tilt_angle
        }
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            self.pan_pwm.stop()
            self.tilt_pwm.stop()
            GPIO.cleanup([self.pan_pin, self.tilt_pin])
            print("✓ Servo controller cleaned up")
        except:
            pass


# Test servo control
if __name__ == '__main__':
    print("Testing Servo Controller...")
    servo = ServoController()
    
    try:
        print("\nCentering servos...")
        servo.center()
        time.sleep(1)
        
        print("\nTesting pan (left-center-right)...")
        servo.set_pan(0)
        time.sleep(1)
        servo.set_pan(90)
        time.sleep(1)
        servo.set_pan(180)
        time.sleep(1)
        servo.set_pan(90)
        
        print("\nTesting tilt (down-center-up)...")
        servo.set_tilt(45)
        time.sleep(1)
        servo.set_tilt(90)
        time.sleep(1)
        servo.set_tilt(135)
        time.sleep(1)
        servo.set_tilt(90)
        
        print("\nPerforming scan...")
        servo.scan()
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        servo.cleanup()
