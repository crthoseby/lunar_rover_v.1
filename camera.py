"""
Camera Module for Lunar Rover
Supports both Pi Camera and USB webcams
"""

import io
import time
import threading
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Try to import camera libraries
camera_available = False
camera_type = None

try:
    from picamera2 import Picamera2
    camera_type = 'picamera2'
    camera_available = True
    print("Pi Camera 2 module detected")
except ImportError:
    try:
        import picamera
        camera_type = 'picamera'
        camera_available = True
        print("Pi Camera (legacy) module detected")
    except ImportError:
        try:
            import cv2
            camera_type = 'opencv'
            camera_available = True
            print("OpenCV camera module detected")
        except ImportError:
            print("No camera module found - using simulator")
            camera_type = 'simulator'


class CameraController:
    """Handles camera operations for the rover"""
    
    def __init__(self, resolution=(640, 480), framerate=30):
        """
        Initialize camera controller
        
        Args:
            resolution: Tuple of (width, height)
            framerate: Frames per second
        """
        self.resolution = resolution
        self.framerate = framerate
        self.camera = None
        self.camera_type = camera_type
        self.is_streaming = False
        self.lock = threading.Lock()
        self.current_frame = None
        
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize the appropriate camera"""
        try:
            if self.camera_type == 'picamera2':
                self._init_picamera2()
            elif self.camera_type == 'picamera':
                self._init_picamera_legacy()
            elif self.camera_type == 'opencv':
                self._init_opencv()
            else:
                self._init_simulator()
            
            print(f"✓ Camera initialized: {self.camera_type}")
        except Exception as e:
            print(f"✗ Camera initialization failed: {e}")
            print("Falling back to simulator mode")
            self.camera_type = 'simulator'
            self._init_simulator()
    
    def _init_picamera2(self):
        """Initialize Pi Camera 2"""
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(
            main={"size": self.resolution, "format": "RGB888"}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)  # Warmup
    
    def _init_picamera_legacy(self):
        """Initialize legacy Pi Camera"""
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate
        time.sleep(2)  # Warmup
    
    def _init_opencv(self):
        """Initialize OpenCV camera (USB webcam)"""
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.camera.set(cv2.CAP_PROP_FPS, self.framerate)
        time.sleep(1)  # Warmup
    
    def _init_simulator(self):
        """Initialize simulator (generates test pattern)"""
        self.camera = 'simulator'
        self.frame_count = 0
    
    def capture_frame(self):
        """Capture a single frame and return as JPEG bytes"""
        with self.lock:
            try:
                if self.camera_type == 'picamera2':
                    return self._capture_picamera2()
                elif self.camera_type == 'picamera':
                    return self._capture_picamera_legacy()
                elif self.camera_type == 'opencv':
                    return self._capture_opencv()
                else:
                    return self._capture_simulator()
            except Exception as e:
                print(f"Frame capture error: {e}")
                return self._generate_error_frame()
    
    def _capture_picamera2(self):
        """Capture from Pi Camera 2"""
        array = self.camera.capture_array()
        image = Image.fromarray(array)
        return self._image_to_jpeg(image)
    
    def _capture_picamera_legacy(self):
        """Capture from legacy Pi Camera"""
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return stream.read()
    
    def _capture_opencv(self):
        """Capture from OpenCV camera"""
        ret, frame = self.camera.read()
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            return self._image_to_jpeg(image)
        return self._generate_error_frame()
    
    def _capture_simulator(self):
        """Generate simulated camera feed"""
        self.frame_count += 1
        
        # Create test pattern
        img = Image.new('RGB', self.resolution, color=(20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Draw grid
        for i in range(0, self.resolution[0], 50):
            draw.line([(i, 0), (i, self.resolution[1])], fill=(40, 40, 60), width=1)
        for i in range(0, self.resolution[1], 50):
            draw.line([(0, i), (self.resolution[0], i)], fill=(40, 40, 60), width=1)
        
        # Draw crosshair
        cx, cy = self.resolution[0] // 2, self.resolution[1] // 2
        draw.line([(cx - 30, cy), (cx + 30, cy)], fill=(0, 255, 0), width=2)
        draw.line([(cx, cy - 30), (cx, cy + 30)], fill=(0, 255, 0), width=2)
        draw.ellipse([(cx - 5, cy - 5), (cx + 5, cy + 5)], outline=(0, 255, 0), width=2)
        
        # Add text overlay
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "🌙 LUNAR ROVER CAMERA", fill=(255, 255, 255), font=font)
        draw.text((10, 40), f"SIMULATOR MODE", fill=(255, 200, 0), font=font)
        draw.text((10, 70), f"Frame: {self.frame_count}", fill=(200, 200, 200), font=font)
        draw.text((10, self.resolution[1] - 30), 
                  f"{self.resolution[0]}x{self.resolution[1]} @ {self.framerate}fps",
                  fill=(150, 150, 150), font=font)
        
        # Add some "terrain" features
        import random
        random.seed(self.frame_count // 10)  # Change slowly
        for _ in range(5):
            x = random.randint(0, self.resolution[0])
            y = random.randint(self.resolution[1] // 2, self.resolution[1])
            r = random.randint(20, 60)
            color = (random.randint(60, 100), random.randint(50, 80), random.randint(40, 70))
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=color, outline=color)
        
        return self._image_to_jpeg(img)
    
    def _image_to_jpeg(self, image, quality=85):
        """Convert PIL Image to JPEG bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        return buffer.read()
    
    def _generate_error_frame(self):
        """Generate an error frame"""
        img = Image.new('RGB', self.resolution, color=(40, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((self.resolution[0] // 2 - 100, self.resolution[1] // 2),
                  "CAMERA ERROR", fill=(255, 0, 0), font=font)
        
        return self._image_to_jpeg(img)
    
    def start_streaming(self):
        """Start streaming mode"""
        self.is_streaming = True
        print("Camera streaming started")
    
    def stop_streaming(self):
        """Stop streaming mode"""
        self.is_streaming = False
        print("Camera streaming stopped")
    
    def cleanup(self):
        """Release camera resources"""
        if self.camera_type == 'picamera2':
            if self.camera:
                self.camera.stop()
                self.camera.close()
        elif self.camera_type == 'picamera':
            if self.camera:
                self.camera.close()
        elif self.camera_type == 'opencv':
            if self.camera:
                self.camera.release()
        
        print("Camera resources released")
    
    def get_info(self):
        """Get camera information"""
        return {
            'type': self.camera_type,
            'resolution': self.resolution,
            'framerate': self.framerate,
            'is_streaming': self.is_streaming,
            'available': camera_available
        }
