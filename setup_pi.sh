#!/bin/bash
# Raspberry Pi Setup Script for Lunar Rover
# Run this script on the Raspberry Pi after copying files

echo "============================================================"
echo "🌙 LUNAR ROVER - Raspberry Pi Setup"
echo "============================================================"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python3 and pip if not present
echo "🐍 Installing Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev

# Install system libraries for OpenCV and GPIO
echo "📚 Installing system libraries..."
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev

# Install I2C tools (for PCA9685 PWM driver)
echo "🔧 Installing I2C tools..."
sudo apt-get install -y i2c-tools python3-smbus

# Enable I2C, SPI, and Camera interfaces
echo "⚙️ Enabling hardware interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_camera 0

# Install Python packages from requirements.txt
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Install optional GPS daemon
echo "🛰️ Installing GPS daemon (optional)..."
sudo apt-get install -y gpsd gpsd-clients

# Create logs directory if it doesn't exist
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p snapshots

# Set permissions
echo "🔐 Setting permissions..."
chmod +x start_rover.sh
chmod +x stop_rover.sh

# Check if we're running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(cat /proc/device-tree/model)
    echo "✅ Detected: $PI_MODEL"
else
    echo "⚠️ Warning: Not running on Raspberry Pi!"
fi

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Reboot the Raspberry Pi: sudo reboot"
echo "2. After reboot, start the rover: ./start_rover.sh"
echo "3. Access from your device: http://RASPBERRY_PI_IP:5000"
echo ""
echo "To find your Pi's IP address: hostname -I"
echo "============================================================"
