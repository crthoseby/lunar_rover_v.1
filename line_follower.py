"""
Autonomous Line Following Module
Detects and follows a line/tape on the floor using camera vision
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Tuple


class LineFollower:
    """Line detection and following controller"""
    
    def __init__(self, camera_controller, motor_controller, config_params=None):
        """
        Initialize line follower
        
        Args:
            camera_controller: CameraController instance
            motor_controller: MotorController instance
            config_params: Dictionary of configuration parameters
        """
        self.camera = camera_controller
        self.motors = motor_controller
        
        # Default configuration
        self.config = {
            'line_color': 'black',  # 'black', 'white', 'red', 'blue', 'yellow'
            'detection_area': 0.6,  # Bottom 60% of frame
            'turn_threshold': 30,   # Pixels offset to trigger turn
            'base_speed': 40,       # Base driving speed (0-100)
            'turn_speed': 30,       # Speed when turning
            'stop_area_threshold': 0.05,  # Stop if line area is too small
            'debug_mode': True      # Show detection overlay
        }
        
        if config_params:
            self.config.update(config_params)
        
        # State
        self.is_active = False
        self.thread = None
        self.line_center = None
        self.frame_center = None
        self.last_direction = 'forward'
        self.frames_without_line = 0
        self.max_frames_without_line = 10
        
        print("✓ Line follower initialized")
    
    def _get_color_range(self, color_name):
        """Get HSV color range for line detection"""
        color_ranges = {
            'black': (np.array([0, 0, 0]), np.array([180, 255, 50])),
            'white': (np.array([0, 0, 200]), np.array([180, 30, 255])),
            'red': (np.array([0, 120, 70]), np.array([10, 255, 255])),
            'blue': (np.array([100, 100, 100]), np.array([130, 255, 255])),
            'yellow': (np.array([20, 100, 100]), np.array([30, 255, 255])),
        }
        return color_ranges.get(color_name, color_ranges['black'])
    
    def detect_line(self, frame):
        """
        Detect line in the frame
        
        Returns:
            Tuple of (line_center_x, frame_width, detected_area)
        """
        if frame is None:
            return None, None, 0
        
        # Convert to numpy array if needed
        if not isinstance(frame, np.ndarray):
            frame = np.array(frame)
        
        height, width = frame.shape[:2]
        self.frame_center = width // 2
        
        # Focus on bottom portion of frame
        roi_height = int(height * self.config['detection_area'])
        roi = frame[height - roi_height:height, :]
        
        # Convert to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        # Create mask for line color
        lower, upper = self._get_color_range(self.config['line_color'])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, width, 0
        
        # Find largest contour (the line)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Calculate moments to find center
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Store for debugging
            self.line_center = cx
            
            return cx, width, area
        
        return None, width, 0
    
    def calculate_steering(self, line_center, frame_width):
        """
        Calculate steering direction based on line position
        
        Returns:
            'forward', 'left', 'right', or 'stop'
        """
        if line_center is None:
            self.frames_without_line += 1
            if self.frames_without_line > self.max_frames_without_line:
                return 'stop'
            # Continue in last direction
            return self.last_direction
        
        self.frames_without_line = 0
        offset = line_center - (frame_width // 2)
        
        # Determine direction
        if abs(offset) < self.config['turn_threshold']:
            direction = 'forward'
        elif offset > 0:
            direction = 'right'
        else:
            direction = 'left'
        
        self.last_direction = direction
        return direction
    
    def execute_movement(self, direction):
        """Execute motor commands based on direction"""
        if direction == 'forward':
            self.motors.set_speed(self.config['base_speed'])
            self.motors.forward(duration=0.1)
        elif direction == 'left':
            self.motors.set_speed(self.config['turn_speed'])
            self.motors.left(duration=0.1)
        elif direction == 'right':
            self.motors.set_speed(self.config['turn_speed'])
            self.motors.right(duration=0.1)
        elif direction == 'stop':
            self.motors.stop()
    
    def _autonomous_loop(self):
        """Main autonomous driving loop"""
        print("🤖 Autonomous mode started")
        
        while self.is_active:
            try:
                # Capture frame
                frame_bytes = self.camera.capture_frame()
                
                # Convert JPEG to numpy array
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect line
                    line_center, frame_width, area = self.detect_line(frame)
                    
                    # Calculate steering
                    direction = self.calculate_steering(line_center, frame_width)
                    
                    # Execute movement
                    self.execute_movement(direction)
                    
                    # Debug output
                    if self.config['debug_mode']:
                        offset = line_center - (frame_width // 2) if line_center else 0
                        print(f"[AUTO] Direction: {direction:8s} | Line Center: {line_center:4} | Offset: {offset:4} | Area: {int(area):6}")
                
                time.sleep(0.05)  # 20 Hz update rate
                
            except Exception as e:
                print(f"[AUTO] Error in autonomous loop: {e}")
                time.sleep(0.1)
        
        # Stop motors when exiting
        self.motors.stop()
        print("🛑 Autonomous mode stopped")
    
    def start(self):
        """Start autonomous line following"""
        if self.is_active:
            print("⚠ Autonomous mode already active")
            return False
        
        self.is_active = True
        self.frames_without_line = 0
        self.thread = threading.Thread(target=self._autonomous_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop autonomous line following"""
        if not self.is_active:
            return False
        
        self.is_active = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.motors.stop()
        return True
    
    def update_config(self, new_config):
        """Update configuration parameters"""
        self.config.update(new_config)
        print(f"✓ Line follower config updated: {new_config}")
    
    def get_status(self):
        """Get current status"""
        return {
            'active': self.is_active,
            'line_detected': self.line_center is not None,
            'line_center': self.line_center,
            'frame_center': self.frame_center,
            'last_direction': self.last_direction,
            'config': self.config
        }
