# 🚀 Raspberry Pi Deployment Guide

## Prerequisites
- Raspberry Pi 3/4 with Raspbian OS installed
- SD card with at least 8GB storage
- WiFi connection or Ethernet cable
- Freenove 4WD Smart Car hardware assembled

## Step 1: Copy Files to Raspberry Pi

### Option A: Using USB Drive
1. Copy the entire `lunar_rover` folder to a USB drive
2. Insert USB into Raspberry Pi
3. Copy to home directory:
   ```bash
   cp -r /media/pi/USB_NAME/lunar_rover ~/lunar_rover
   cd ~/lunar_rover
   ```

### Option B: Using SCP (from your computer)
```bash
scp -r lunar_rover pi@RASPBERRY_PI_IP:~/
```

### Option C: Using Git
```bash
# On Raspberry Pi
git clone YOUR_REPO_URL
cd lunar_rover
```

## Step 2: Run Setup Script

```bash
cd ~/lunar_rover
chmod +x setup_pi.sh
./setup_pi.sh
```

This will:
- Update system packages
- Install Python and required libraries
- Enable I2C, SPI, and Camera interfaces
- Install GPS daemon (gpsd)
- Create necessary directories
- Set file permissions

**Reboot after setup:**
```bash
sudo reboot
```

## Step 3: Start the Rover Server

After reboot:
```bash
cd ~/lunar_rover
./start_rover.sh
```

The script will display the IP address to access from other devices.

## Step 4: Connect from Your Device/Phone

### Find Raspberry Pi IP Address
```bash
hostname -I
```

### Connect
1. **Same WiFi**: Make sure your phone/laptop is on the same WiFi network as the Pi
2. **Open browser**: Go to `http://RASPBERRY_PI_IP:5000`
3. **Control**: Use the web interface to control the rover

### Example URLs
- From Pi itself: `http://localhost:5000`
- From phone: `http://192.168.1.100:5000` (use actual Pi IP)

## Auto-Start on Boot (Optional)

To make the rover start automatically when Pi boots:

1. Edit crontab:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```
   @reboot sleep 30 && cd /home/pi/lunar_rover && ./start_rover.sh
   ```

3. Save and exit (Ctrl+X, Y, Enter)

## Troubleshooting

### Server won't start
```bash
# Check Python is installed
python3 --version

# Check dependencies
pip3 list

# Reinstall requirements
pip3 install -r requirements.txt
```

### Can't access from phone
1. Verify Pi and phone are on same WiFi network
2. Check firewall settings:
   ```bash
   sudo ufw allow 5000
   ```
3. Verify server is running:
   ```bash
   ps aux | grep web_server.py
   ```

### GPIO Permissions
If you get GPIO permission errors:
```bash
sudo usermod -a -G gpio pi
sudo reboot
```

### Camera not working
```bash
# Enable camera
sudo raspi-config
# Navigate to Interface Options > Camera > Enable

# Test camera
raspistill -o test.jpg
```

### I2C not detected
```bash
# Check I2C is enabled
sudo i2cdetect -y 1

# Enable I2C
sudo raspi-config
# Navigate to Interface Options > I2C > Enable
```

## Stopping the Server

```bash
cd ~/lunar_rover
./stop_rover.sh
```

Or manually:
```bash
pkill -f web_server.py
```

## Monitoring Logs

```bash
# View real-time logs
tail -f logs/rover_log_*.txt

# List all log files
ls -lh logs/
```

## Network Configuration

### Static IP (Recommended)
To assign a static IP to your Pi for easier access:

1. Edit dhcpcd.conf:
   ```bash
   sudo nano /etc/dhcpcd.conf
   ```

2. Add at the end:
   ```
   interface wlan0
   static ip_address=192.168.1.100/24
   static routers=192.168.1.1
   static domain_name_servers=192.168.1.1 8.8.8.8
   ```

3. Restart networking:
   ```bash
   sudo systemctl restart dhcpcd
   ```

### Hotspot Mode (Advanced)
To make the Pi create its own WiFi network:

```bash
sudo apt-get install hostapd dnsmasq
# Follow Raspberry Pi hotspot tutorial
```

## Security Notes

⚠️ **Production Deployment:**
- The Flask development server is NOT suitable for production
- For production, use a proper WSGI server like Gunicorn:
  ```bash
  pip3 install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
  ```

- Add authentication if exposing to the internet
- Use HTTPS with SSL certificates
- Configure firewall rules

## Performance Tips

1. **Overclock Pi** (at your own risk):
   ```bash
   sudo raspi-config
   # Performance Options > Overclock
   ```

2. **Reduce camera resolution** in `config.py` for better performance

3. **Disable unnecessary services**:
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable cups
   ```

## Hardware Checklist

Before testing, verify:
- [ ] All motors connected to motor driver
- [ ] Battery charged and connected
- [ ] Camera module connected to CSI port
- [ ] Servo motors connected to GPIO pins
- [ ] I2C connections secure (if using PCA9685)
- [ ] Power switch accessible

## Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Verify hardware connections
3. Test individual components (motors, camera, servos)
4. Check GPIO pin configuration in `config.py`

Happy roving! 🌙🚗
