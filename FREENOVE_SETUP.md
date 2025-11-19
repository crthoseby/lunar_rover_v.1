# Freenove 4WD Smart Car v2.4 - Complete Setup Guide

## 🚗 Hardware Components Supported

### ✅ What You Have Configured:

1. **Motor Control**
   - 4WD motor system with PWM speed control
   - GPIO-based motor driver (compatible with L298N or Freenove board)
   - Speed range: 0-100%
   - Directional control: Forward, Backward, Left, Right, Stop

2. **SG90 9g Micro Servos**
   - Camera pan servo (GPIO 16)
   - Camera tilt servo (GPIO 18)
   - 0-180° range with center at 90°
   - Scanning and positioning capabilities

3. **Raspberry Pi Camera**
   - Support for: picamera2 (latest), picamera (legacy), USB webcams
   - Live streaming via MJPEG
   - Resolution: 640x480 @ 15fps
   - Snapshot capture with timestamp naming
   - Saved to `snapshots/` folder

4. **GNSS/GPS Tracker**
   - Supports GPSD, serial GPS, and simulator modes
   - Real-time coordinates, altitude, speed, heading
   - Distance tracking and statistics
   - Satellite count display

5. **Audio System**
   - Audio recording capability
   - WAV format support
   - Configurable sample rate (44.1kHz default)
   - Mono/stereo support

6. **Sensors Ready** (configurable in config.py):
   - Ultrasonic sensor (HC-SR04) pins defined
   - Buzzer (GPIO 12)
   - LED pins (GPIO 5, 6, 13, 19)
   - Battery monitoring (ADC ready)

---

## 📁 Project Structure

```
lunar_rover/
├── config.py              # Central configuration for all hardware
├── motor_control.py       # Motor driver controller
├── servo_control.py       # SG90 servo controller (NEW)
├── camera.py              # Multi-source camera support
├── audio_controller.py    # Audio recording/playback (NEW)
├── gnss_tracker.py        # GPS positioning (NEW)
├── line_follower.py       # Autonomous line following
├── mars_delay.py          # Communication delay simulation
├── log_manager.py         # Transmission log saving (NEW)
├── gpio_simulator.py      # Windows testing simulator
├── web_server.py          # Flask web server with all APIs
├── rover.py               # Command-line interface
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
│
├── templates/
│   ├── index.html         # Main control dashboard
│   └── test_camera.html   # Camera test page
│
├── static/
│   ├── style.css          # Dashboard styling
│   └── script.js          # Client-side controls
│
├── snapshots/             # Camera snapshots (auto-created)
└── logs/                  # Transmission logs (auto-created)
```

---

## 🔌 Pin Configuration (BCM Mode)

### Motors (L298N/Freenove Motor Driver)
- GPIO 17: Left Motor Forward
- GPIO 27: Left Motor Backward
- GPIO 22: Right Motor Forward
- GPIO 23: Right Motor Backward

### Servos (SG90 9g)
- GPIO 16: Camera Pan Servo
- GPIO 18: Camera Tilt Servo

### Sensors (Optional - Ready to Use)
- GPIO 27: Ultrasonic Trigger
- GPIO 22: Ultrasonic Echo
- GPIO 12: Buzzer
- GPIO 5, 6, 13, 19: LEDs

### Camera
- Raspberry Pi Camera Module (CSI connector)
- OR USB Webcam

### GPS
- /dev/ttyAMA0 (UART) or USB GPS
- OR GPSD daemon

---

## 📦 Installation on Raspberry Pi

### 1. System Preparation
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and tools
sudo apt-get install -y python3 python3-pip git
```

### 2. Install Python Dependencies
```bash
cd ~/lunar_rover
pip3 install -r requirements.txt
```

### 3. Enable Raspberry Pi Camera (if using Pi Camera)
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### 4. Enable UART for GPS (if using serial GPS)
```bash
sudo raspi-config
# Navigate to: Interface Options → Serial Port
# Disable login shell, Enable serial hardware
```

### 5. Install Optional Components

**For GPSD (GPS daemon):**
```bash
sudo apt-get install -y gpsd gpsd-clients python3-gps
sudo systemctl enable gpsd
sudo systemctl start gpsd
```

**For Pi Camera (latest Raspberry Pi OS):**
```bash
pip3 install picamera2
```

**For Audio:**
```bash
sudo apt-get install -y portaudio19-dev
pip3 install pyaudio
```

---

## 🚀 Running the Rover

### Start Web Server
```bash
cd ~/lunar_rover
python3 web_server.py
```

Access dashboard:
- Local: http://localhost:5000
- Network: http://YOUR_PI_IP:5000
- From PC on same WiFi: http://raspberry_pi_ip:5000

### Command-Line Control (Optional)
```bash
python3 rover.py
```

---

## 🌐 Web Dashboard Features

### Left Column
1. **📹 Rover Camera Feed**
   - Live MJPEG stream
   - Toggle camera on/off
   - Capture snapshots
   
2. **📡 Transmission Log**
   - Real-time command history
   - Color-coded entries (info/command/success/error)
   - Auto-saves to logs/ folder
   
3. **📊 Statistics**
   - Commands sent count
   - Total delay time
   - Average delay
   
4. **🛰️ GNSS Position**
   - GPS coordinates
   - Altitude, speed, heading
   - Satellite count
   - Distance traveled

### Right Column
1. **🎮 Movement Controls**
   - Directional buttons (W/A/S/D keyboard support)
   - Stop button (X key)
   
2. **⚙️ Speed Control**
   - Slider: 0-100%
   
3. **🤖 Autonomous Mode**
   - Line following
   - Color selection (black/white/red/blue/yellow)
   - Speed adjustment
   
4. **🔴 Mars Communication Delay**
   - Enable/disable simulation
   - Modes: Min/Average/Max/Random
   - 2-5 second delays

---

## 🆕 New Features Added

### 1. Servo Control API
- `POST /api/servo/position` - Set pan/tilt angles
- `POST /api/servo/center` - Center both servos
- `GET /api/servo/status` - Get current positions

### 2. Audio Recording API
- `POST /api/audio/record/start` - Start recording
- `POST /api/audio/record/stop` - Stop recording
- `GET /api/audio/status` - Get recording status

### 3. Log Management API
- `POST /api/logs/export` - Export current log
- `GET /api/logs/list` - List all log files
- `GET /api/logs/stats` - Get logging statistics
- `GET /api/logs/recent?count=50` - Get recent entries

### 4. Transmission Log Storage
- Auto-saves all console messages to files
- Format: `logs/rover_log_YYYYMMDD_HHMMSS.txt`
- Max file size: 10MB (auto-rotation)
- Retention: 30 days
- Export functionality

---

## 🎯 Testing Individual Components

### Test Servos
```bash
python3 servo_control.py
```

### Test Audio
```bash
python3 audio_controller.py
```

### Test GPS
```bash
python3 gnss_tracker.py
```

### Test Camera
```bash
# Open browser to: http://YOUR_PI_IP:5000/test
```

---

## 🔧 Configuration Changes

Edit `config.py` to adjust:
- GPIO pin mappings
- Servo angles and limits
- Camera resolution/framerate
- GPS mode (auto/gpsd/serial/simulator)
- Audio settings
- Log retention period
- Mars delay parameters

---

## 📝 Log Files

### Location
- `logs/` directory (auto-created)

### Format
```
================================================================================
LUNAR ROVER TRANSMISSION LOG
Session Started: 2025-11-18 14:30:00
================================================================================

2025-11-18 14:30:01.123 [INFO] Rover initialized successfully
2025-11-18 14:30:05.456 [CMD] Command: forward | Delay: 3.20s
2025-11-18 14:30:08.678 [OK] Executed: forward
```

### Export
- Manual: Click "Export Log" button in dashboard
- Automatic: Logs saved continuously
- Access: `GET /api/logs/list` to see all files

---

## 🌟 What's Complete

✅ Motor control with PWM
✅ Camera streaming and snapshots
✅ Autonomous line following
✅ Mars delay simulation
✅ GNSS position tracking
✅ Servo pan/tilt control (NEW)
✅ Audio recording (NEW)
✅ Transmission log saving (NEW)
✅ Web dashboard interface
✅ Keyboard controls
✅ Statistics tracking
✅ GPIO simulator for Windows testing

---

## 📱 Mobile Access

The dashboard is responsive and works on:
- Desktop browsers
- Tablets
- Smartphones

Just connect to: `http://YOUR_PI_IP:5000`

---

## 🔒 Security Note

The web server runs without authentication. For production use:
1. Run behind a reverse proxy (nginx)
2. Add HTTPS (SSL/TLS)
3. Implement authentication
4. Restrict to local network

---

## 🐛 Troubleshooting

### Camera not showing
1. Hard refresh browser (Ctrl+Shift+R)
2. Check `/video_feed` endpoint directly
3. Verify camera permissions

### GPS not working
1. Check UART enabled in raspi-config
2. Verify GPS module connection
3. Test with `gpsd` or serial monitor

### Servo jitter
1. Ensure stable 5V power supply
2. Add capacitor to servo power
3. PWM signals stop after movement (anti-jitter)

### Audio errors
1. Install portaudio: `sudo apt-get install portaudio19-dev`
2. Check microphone permissions
3. Test with `arecord -l`

---

## 📞 Support

For Freenove kit issues:
- Email: support@freenove.com
- GitHub: https://github.com/Freenove/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi

---

## 🎓 Cranfield University Project

**Module:** Digital Integration and System Testing (A25)

**Features Implemented:**
- Real-time remote control
- Communication delay simulation (Mars rover scenario)
- Autonomous navigation
- Position tracking
- Multi-sensor integration
- Data logging and export
