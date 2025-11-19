# 🌙 Lunar Rover Control System

A comprehensive Raspberry Pi-based robotic rover with web control interface, designed to simulate lunar/Mars operations with realistic communication delays, terrain simulation, and autonomous capabilities.

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Hardware Requirements](#hardware-requirements)
- [Software Installation](#software-installation)
- [Quick Start](#quick-start)
- [Web Interface](#web-interface)
- [Simulation Mode](#simulation-mode)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Known Limitations](#known-limitations)

---

## ✨ Features

### 🎮 **Control Systems**
- **Motor Control**: Precise 4-wheel drive with PWM speed control (0-100%)
- **Servo Control**: Pan/tilt camera mount with configurable angles
- **Web Interface**: Real-time control dashboard with live camera feed
- **Command Queue**: Asynchronous command processing with Mars delay simulation

### 🌍 **Environmental Simulation**
- **Ground Conditions**: 6 terrain types (flat rock, dusty plain, rocky field, soft sand, crater rim, regolith)
- **Gravity Modes**: Moon (1.62 m/s²), Mars (3.71 m/s²), Earth (9.81 m/s²)
- **Physics**: Wheel slip, dust accumulation, getting stuck, energy consumption
- **Mars Delay**: Realistic 3-22 minute communication lag (scaled for testing)

### 🤖 **Autonomous Features**
- **Line Following**: IR sensor-based path tracking
- **GNSS Tracking**: Position monitoring with coordinate history
- **Autonomous Navigation**: Automatic waypoint following

### 📊 **Monitoring & Logging**
- **Transmission Log**: Real-time activity log with color-coded entries
- **Statistics**: Distance traveled, commands executed, runtime tracking
- **Log Rotation**: Automatic file management with 10MB rotation
- **Export**: HTML and JSON log export

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│         Web Browser (Control Interface)        │
│  ┌─────────┬──────────┬──────────┬──────────┐  │
│  │Dashboard│  Camera  │   GNSS   │   Logs   │  │
│  └─────────┴──────────┴──────────┴──────────┘  │
└────────────────────┬────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────┐
│          Flask Web Server (web_server.py)       │
│  ┌────────────────────────────────────────────┐ │
│  │         Rover Core (rover.py)              │ │
│  │  ┌──────────┬──────────┬──────────────┐   │ │
│  │  │ Motors   │  Servos  │    Camera    │   │ │
│  │  ├──────────┼──────────┼──────────────┤   │ │
│  │  │   GNSS   │LineFollow│GroundConds   │   │ │
│  │  ├──────────┼──────────┼──────────────┤   │ │
│  │  │MarsDelay │  Logger  │ AudioCtrl    │   │ │
│  │  └──────────┴──────────┴──────────────┘   │ │
│  └────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │ GPIO/Hardware
┌────────────────────▼────────────────────────────┐
│   Raspberry Pi GPIO / Simulation Layer          │
│  ┌──────────┬──────────┬──────────────────────┐ │
│  │L298N     │ Servos   │   Pi Camera/USB      │ │
│  │Motor Drv │(SG90)    │                      │ │
│  └──────────┴──────────┴──────────────────────┘ │
└──────────────────────────────────────────────────┘
```

---

## 🔧 Hardware Requirements

### Required Components
- **Raspberry Pi** (3B+, 4, or 5 recommended)
- **L298N Motor Driver** or equivalent H-bridge
- **4x DC Motors** with wheels
- **Robot chassis** (4WD recommended)
- **2x Servo motors** (SG90 or MG996R for pan/tilt)
- **Pi Camera** or USB webcam
- **Battery pack** (7.4V-12V for motors, 2S-3S LiPo)
- **5V Power supply** for Raspberry Pi (separate recommended)
- **IR sensors** (3-5 for line following, optional)
- **Jumper wires** and breadboard

### GPIO Pin Configuration (BCM Mode)

| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Motor IN1 | GPIO 17 | Left motor forward |
| Motor IN2 | GPIO 27 | Left motor backward |
| Motor IN3 | GPIO 22 | Right motor forward |
| Motor IN4 | GPIO 23 | Right motor backward |
| Servo Pan | GPIO 16 | Camera pan control |
| Servo Tilt | GPIO 18 | Camera tilt control |

*Note: Configure pins in `config.py` if using different GPIOs*

---

## 💻 Software Installation

### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install python3-pip python3-venv git -y

# Enable camera (if using Pi Camera)
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### Installation Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd lunar_rover
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure settings**
```bash
# Edit config.py with your GPIO pins and preferences
nano config.py
```

---

## 🚀 Quick Start

### Run in Simulation Mode (No Hardware)
```bash
python web_server.py
```
Then open browser to: **http://localhost:5000**

The system automatically detects missing hardware and runs in simulation mode with:
- GPIO simulator (no RPi.GPIO needed)
- Virtual camera (OpenCV)
- Simulated GNSS coordinates
- Full web interface

### Run with Real Hardware
```bash
# On Raspberry Pi with connected hardware
python web_server.py
```

---

## 🌐 Web Interface

### Dashboard Features

**📊 System Status**
- Real-time rover state (Ready/Busy/Error)
- Speed control (0-100%)
- Mars delay toggle (ON/OFF)
- Statistics (distance, commands, uptime)

**🎮 Movement Controls**
- Directional buttons (Forward/Backward/Left/Right/Stop)
- Keyboard shortcuts (W/S/A/D/Space)
- Visual feedback on command execution

**📹 Camera View**
- Live video stream
- Pan/Tilt servo controls
- Snapshot capture
- Camera toggle

**🛰️ GNSS Position**
- Current coordinates (Lat/Lon)
- Altitude display
- Position history
- Reset function

**📡 Transmission Log**
- Real-time activity feed
- Color-coded log types:
  - 🔵 Info (system events)
  - 🟢 Success (completed actions)
  - 🟠 Commands (sent instructions)
  - 🔴 Errors (failures)
  - 🟡 Warnings (alerts)
- Auto-scroll toggle
- Clear log button

**🌍 Ground Conditions**
- Terrain selection (6 types)
- Gravity mode (Moon/Mars/Earth)
- Wheel slip indicator
- Dust accumulation meter
- Terrain warnings

---

## 🎮 Simulation Mode

### What Gets Simulated?

When hardware is unavailable, the system automatically activates simulation mode:

**🔌 GPIO Simulator** (`gpio_simulator.py`)
- Mimics RPi.GPIO API
- Logs all pin operations
- No actual hardware required
- Perfect for development and testing

**📹 Virtual Camera**
- Generates test pattern with timestamp
- Simulates live video feed
- OpenCV-based rendering
- Frame counter overlay

**🛰️ Simulated GNSS**
- Random walk algorithm
- Realistic coordinate changes
- Moon/Mars surface coordinates
- Distance calculations

**Benefits:**
- ✅ Develop without Raspberry Pi
- ✅ Test on Windows/Mac/Linux
- ✅ Debug without risking hardware
- ✅ Classroom/presentation demos
- ✅ CI/CD pipeline compatible

---

## ⚙️ Configuration

### Main Settings (`config.py`)

```python
# Motor GPIO pins (BCM mode)
MOTOR_LEFT_FORWARD = 17
MOTOR_LEFT_BACKWARD = 27
MOTOR_RIGHT_FORWARD = 22
MOTOR_RIGHT_BACKWARD = 23

# Servo GPIO pins
SERVO_CAMERA_PAN_PIN = 16
SERVO_CAMERA_TILT_PIN = 18

# Movement parameters
DEFAULT_SPEED = 75  # 0-100%
DEFAULT_MOVE_DURATION = 1.0  # seconds

# Mars delay simulation
MARS_DELAY_MIN = 2.0  # seconds (scaled from 3 min)
MARS_DELAY_MAX = 5.0  # seconds (scaled from 22 min)
MARS_DELAY_MODE = 'random'  # 'min', 'max', 'avg', 'random'

# Camera settings
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 30

# Web server
WEB_SERVER_PORT = 5000
WEB_SERVER_HOST = '0.0.0.0'  # Allow external connections

# Logging
LOG_DIRECTORY = 'logs'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_RETENTION_DAYS = 30
```

---

## 📡 API Reference

### Base URL
```
http://localhost:5000
```

### Endpoints

#### Movement Commands
```http
POST /api/command/<action>
```
Actions: `forward`, `backward`, `left`, `right`, `stop`

**Request Body (optional):**
```json
{
  "duration": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "command": "forward"
}
```

#### System Status
```http
GET /api/status
```

**Response:**
```json
{
  "status": "ready",
  "speed": 75,
  "delay_enabled": true,
  "delay_mode": "random",
  "stats": {
    "distance": 12.5,
    "commands": 45,
    "runtime": "00:15:32"
  }
}
```

#### GNSS Position
```http
GET /api/gnss/position
```

**Response:**
```json
{
  "latitude": -20.5847,
  "longitude": -25.3249,
  "altitude": 125.4,
  "timestamp": "2025-11-18T21:20:45"
}
```

#### Ground Conditions
```http
GET /api/ground/status
POST /api/ground/terrain/<type>
POST /api/ground/environment/<env>
POST /api/ground/clean_dust
POST /api/ground/unstuck
```

#### Transmission Logs
```http
GET /api/logs/recent?count=20
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-11-18 21:20:45.123",
      "type": "command",
      "message": "Command: FORWARD | Delay: 2.34s"
    }
  ]
}
```

---

## 📂 Project Structure

```
lunar_rover/
├── web_server.py          # Flask web server & main entry point
├── rover.py               # Core rover controller
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── Hardware Controllers/
│   ├── motor_control.py   # L298N motor driver control
│   ├── servo_control.py   # SG90 servo control (pan/tilt)
│   ├── camera.py          # Camera interface (Pi/USB/simulator)
│   └── gpio_simulator.py  # GPIO simulation for testing
│
├── Navigation & Sensors/
│   ├── gnss_tracker.py    # GNSS/GPS position tracking
│   └── line_follower.py   # IR-based line following
│
├── Simulation/
│   ├── mars_delay.py      # Communication delay simulator
│   └── ground_conditions.py # Terrain physics simulation
│
├── Logging & Audio/
│   ├── log_manager.py     # Log file management
│   └── audio_controller.py # Audio playback/recording
│
└── Web Interface/
    ├── templates/
    │   └── index.html     # Main dashboard
    └── static/
        ├── style.css      # Dashboard styling
        └── script.js      # Client-side logic
```

---

## 🐛 Known Limitations

1. **Mars Delay Simulation**
   - Uses `time.sleep()` which blocks the thread
   - Recommendation: Migrate to async/await for better responsiveness

2. **GNSS Tracker**
   - Simulator uses random walk, not realistic trajectory
   - No real NMEA sentence parsing yet
   - No Kalman filtering for position smoothing

3. **Web Security**
   - No authentication (anyone on network can control)
   - No CSRF protection
   - Commands use POST but no rate limiting

4. **Camera Stream**
   - MJPEG streaming (high bandwidth)
   - No WebRTC support
   - Limited to one concurrent viewer

5. **Line Following**
   - Requires calibration for each surface
   - Binary threshold (no PID control yet)

6. **Ground Conditions**
   - Simplified physics model
   - No multi-terrain transitions
   - Dust/slip are probabilistic, not physics-based

---

## 🔬 Future Enhancements

- [ ] Add authentication and CSRF protection
- [ ] Implement WebSocket for real-time telemetry
- [ ] Add unit tests (pytest)
- [ ] Migrate to async/await for delays
- [ ] Add NMEA parsing for real GPS
- [ ] Implement Kalman filtering for GNSS
- [ ] Add PID control for line following
- [ ] Battery voltage monitoring
- [ ] Obstacle detection (ultrasonic sensors)
- [ ] ROS2 integration option
- [ ] Multi-rover support

---

## 📝 License

This project is part of the Freenove 4WD Smart Car educational platform.

---

## 🤝 Contributing

Contributions welcome! Areas needing improvement:
- Security enhancements
- Test coverage
- Documentation
- Hardware compatibility
- Performance optimization

---

## 📧 Support

For issues, questions, or contributions, please refer to the course materials or contact your instructor.

---

**Happy Roving! 🌙🚗**
- Raspberry Pi (any model with GPIO)
- L298N Motor Driver (or similar H-bridge)
- 2x DC Motors
- Robot chassis with wheels
- Battery pack (6-12V for motors)
- 5V power supply for Raspberry Pi
- Jumper wires

### Wiring Diagram

```
Raspberry Pi GPIO (BCM)          L298N Motor Driver
================================  ==================
GPIO 17 -----------------------> IN1 (Left Motor Forward)
GPIO 27 -----------------------> IN2 (Left Motor Backward)
GPIO 22 -----------------------> IN3 (Right Motor Forward)
GPIO 23 -----------------------> IN4 (Right Motor Backward)

GND --------------------------->  GND

L298N Motor Driver               Motors
==================               ======
OUT1, OUT2 --------------------> Left Motor
OUT3, OUT4 --------------------> Right Motor

12V Power Supply
================
+ ----------------------------->  L298N 12V Input
- ----------------------------->  GND (shared with Pi)
```

**Note**: Adjust GPIO pins in `config.py` if using different pins.

## Software Requirements

```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install python3 python3-pip
sudo pip3 install RPi.GPIO
```

## Installation

1. Clone or download this project to your Raspberry Pi:
```bash
cd ~
mkdir lunar_rover
cd lunar_rover
```

2. Copy all Python files to the directory:
   - `config.py`
   - `motor_control.py`
   - `mars_delay.py`
   - `rover.py`

3. Make the main script executable:
```bash
chmod +x rover.py
```

## Configuration

Edit `config.py` to match your hardware setup:

```python
# GPIO Pin Configuration (BCM numbering)
MOTOR_LEFT_FORWARD = 17
MOTOR_LEFT_BACKWARD = 27
MOTOR_RIGHT_FORWARD = 22
MOTOR_RIGHT_BACKWARD = 23

# PWM Configuration
DEFAULT_SPEED = 75  # 0-100%

# Mars Communication Lag (in seconds)
MARS_LAG_MIN = 2.0
MARS_LAG_MAX = 5.0
MARS_LAG_AVERAGE = 3.5
```

## Usage

### Basic Usage

```bash
python3 rover.py
```

### Command Line Options

```bash
# Run without delay simulation
python3 rover.py --no-delay

# Run with specific delay mode
python3 rover.py --mode=random
python3 rover.py --mode=min
python3 rover.py --mode=max
```

### Interactive Commands

Once running, use these commands:

**Movement:**
- `w` or `forward` - Move forward
- `s` or `backward` - Move backward
- `a` or `left` - Turn left
- `d` or `right` - Turn right
- `x` or `stop` - Stop all motors

**Configuration:**
- `speed <0-100>` - Set motor speed (e.g., `speed 50`)
- `delay <on/off>` - Toggle Mars delay simulation
- `mode <min/max/average/random>` - Set delay mode

**Information:**
- `stats` - Show delay statistics
- `help` - Show help menu
- `quit` - Exit program

### Example Session

```
Rover> w
[EARTH] Command sent: FORWARD
[TRANSMISSION] Delay: 3.50s
[WAITING] Signal traveling to Mars...
[████████████████████] 100%
[MARS] Command received: FORWARD
Moving forward at 75% speed

Rover> speed 50
Speed set to 50%

Rover> mode random
Delay mode set to: random

Rover> a
[EARTH] Command sent: TURN LEFT
[TRANSMISSION] Delay: 4.23s
...
```

## Project Structure

```
lunar_rover/
├── config.py           # Configuration settings
├── motor_control.py    # Motor control via GPIO
├── mars_delay.py       # Communication delay simulator
├── rover.py           # Main control script
└── README.md          # This file
```

## How It Works

1. **Motor Control**: Uses GPIO pins with PWM to control DC motors through an L298N driver
2. **Mars Delay**: Simulates the time it takes for radio signals to travel between Earth and Mars
3. **Command Queue**: Commands are delayed before execution to simulate real mission conditions
4. **Visual Feedback**: Progress bars show signal transmission in real-time

## Troubleshooting

### Motors not responding
- Check wiring connections
- Verify GPIO pin numbers in `config.py`
- Ensure motor driver is powered
- Check that you're running with sudo if needed: `sudo python3 rover.py`

### Permission errors
```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

### Motors spinning in wrong direction
- Swap the motor wires on the L298N outputs
- Or adjust the pin assignments in `config.py`

## Safety Notes

⚠️ **Important Safety Reminders:**
- Always have a way to quickly cut power to motors
- Test in a clear area first
- Don't exceed motor voltage ratings
- Never connect motor power directly to Raspberry Pi pins

## Future Enhancements

- [ ] Add camera module for FPV
- [ ] Implement autonomous obstacle avoidance
- [ ] Add telemetry logging
- [ ] Web-based control interface
- [ ] Queue multiple commands
- [ ] Add ultrasonic distance sensors

## License

This project is for educational purposes.

## Credits

Created for the Digital Integration and System Testing module at Cranfield University.

---

**Happy Roving! 🚀**
