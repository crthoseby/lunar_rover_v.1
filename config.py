# Lunar Rover Configuration for Freenove 4WD Smart Car Kit v2.4

# ===== MOTOR CONTROL CONFIGURATION =====
# GPIO Pin Configuration (BCM numbering)
# Freenove 4WD Smart Car uses PCA9685 PWM driver via I2C
# Standard motor control pins for direct GPIO control (fallback mode)
MOTOR_LEFT_FORWARD = 17
MOTOR_LEFT_BACKWARD = 27
MOTOR_RIGHT_FORWARD = 22
MOTOR_RIGHT_BACKWARD = 23

# PWM Configuration
PWM_FREQUENCY = 1000  # Hz
DEFAULT_SPEED = 75  # 0-100%

# ===== SERVO CONFIGURATION =====
# SG90 9g Micro Servo - Camera Pan/Tilt
SERVO_CAMERA_PAN_PIN = 16  # GPIO pin for pan servo
SERVO_CAMERA_TILT_PIN = 18  # GPIO pin for tilt servo
SERVO_MIN_PULSE = 500  # Minimum pulse width (μs)
SERVO_MAX_PULSE = 2500  # Maximum pulse width (μs)
SERVO_CENTER = 90  # Center position (degrees)
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180
SERVO_FREQUENCY = 50  # Hz (standard for SG90)

# ===== ULTRASONIC SENSOR CONFIGURATION =====
# HC-SR04 Ultrasonic Distance Sensor
ULTRASONIC_TRIG_PIN = 27  # Trigger pin
ULTRASONIC_ECHO_PIN = 22  # Echo pin
ULTRASONIC_MAX_DISTANCE = 400  # Maximum distance in cm
ULTRASONIC_TIMEOUT = 0.05  # Timeout in seconds

# ===== BUZZER CONFIGURATION =====
BUZZER_PIN = 12  # Buzzer GPIO pin

# ===== LED CONFIGURATION =====
LED_PINS = [5, 6, 13, 19]  # Four LED GPIO pins (if available)

# ===== BATTERY MONITORING =====
# ADC channels for battery voltage monitoring (if using ADS1115)
BATTERY_ADC_CHANNEL = 0
BATTERY_MIN_VOLTAGE = 6.0  # Minimum safe voltage
BATTERY_MAX_VOLTAGE = 8.4  # Maximum voltage (2S LiPo)

# ===== MARS COMMUNICATION LAG SIMULATION =====
# Average one-way light delay: 3-22 minutes depending on distance
# Using a scaled down version for practical testing
MARS_LAG_MIN = 0.0  # seconds (disabled)
MARS_LAG_MAX = 0.0  # seconds (disabled)
MARS_LAG_AVERAGE = 0.0  # seconds (disabled)

# ===== MOVEMENT SETTINGS =====
DEFAULT_MOVE_DURATION = 1.0  # seconds

# Command Queue Settings
MAX_QUEUE_SIZE = 10

# ===== CAMERA SETTINGS =====
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 15

# ===== LINE FOLLOWING SETTINGS =====
LINE_COLOR_RANGES = {
    'black': ([0, 0, 0], [180, 255, 50]),
    'white': ([0, 0, 200], [180, 30, 255]),
    'red': ([0, 100, 100], [10, 255, 255]),
    'blue': ([100, 100, 100], [130, 255, 255]),
    'yellow': ([20, 100, 100], [30, 255, 255])
}

# ===== AUDIO CONFIGURATION =====
AUDIO_ENABLED = True
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1  # Mono
AUDIO_CHUNK_SIZE = 1024

# ===== LOGGING CONFIGURATION =====
LOG_DIRECTORY = 'logs'
LOG_FILENAME_FORMAT = 'rover_log_%Y%m%d_%H%M%S.txt'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_RETENTION_DAYS = 30
