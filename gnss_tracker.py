"""
GNSS/GPS Tracker Module for Lunar Rover
Supports multiple GPS modules: GPSD, serial GPS (UART), and USB GPS
"""

import time
import threading
from datetime import datetime

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠ pyserial not available - serial GPS disabled")

try:
    from gps import gps, WATCH_ENABLE
    GPSD_AVAILABLE = True
except ImportError:
    GPSD_AVAILABLE = False
    print("⚠ gpsd not available - using fallback mode")


class GNSSTracker:
    """GNSS/GPS position tracker with multiple backend support"""
    
    def __init__(self, mode='auto', port='/dev/ttyAMA0', baudrate=9600):
        """
        Initialize GNSS tracker
        
        Args:
            mode: 'gpsd', 'serial', 'auto', or 'simulator'
            port: Serial port for UART GPS (default /dev/ttyAMA0 for Pi)
            baudrate: Serial baudrate (usually 9600 or 115200)
        """
        self.mode = mode
        self.port = port
        self.baudrate = baudrate
        
        # GPS data
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0  # km/h
        self.heading = 0.0  # degrees
        self.satellites = 0
        self.fix_quality = 0  # 0=no fix, 1=GPS, 2=DGPS
        self.timestamp = None
        self.valid = False
        
        # Statistics
        self.total_distance = 0.0  # meters
        self.max_speed = 0.0
        self.positions = []  # List of (lat, lon, timestamp)
        
        # Threading
        self._running = False
        self._thread = None
        
        # Initialize based on mode
        self._initialize_gps()
    
    def _initialize_gps(self):
        """Initialize GPS module based on available backends"""
        if self.mode == 'simulator':
            print("✓ GNSS initialized in simulator mode")
            self.latitude = 52.0719  # Cranfield University
            self.longitude = -0.6176
            self.altitude = 92.0
            self.valid = True
            return
        
        if self.mode == 'auto':
            # Try GPSD first, then serial
            if GPSD_AVAILABLE:
                self.mode = 'gpsd'
            elif SERIAL_AVAILABLE:
                self.mode = 'serial'
            else:
                self.mode = 'simulator'
                print("⚠ No GPS backend available, using simulator")
        
        if self.mode == 'gpsd':
            try:
                self.gpsd = gps(mode=WATCH_ENABLE)
                print("✓ GNSS initialized: GPSD")
            except Exception as e:
                print(f"⚠ GPSD connection failed: {e}")
                self.mode = 'simulator'
        
        elif self.mode == 'serial':
            if not SERIAL_AVAILABLE:
                print("⚠ pyserial not available")
                self.mode = 'simulator'
            else:
                try:
                    self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
                    print(f"✓ GNSS initialized: Serial ({self.port})")
                except Exception as e:
                    print(f"⚠ Serial GPS failed: {e}")
                    self.mode = 'simulator'
    
    def start(self):
        """Start GPS tracking thread"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        print("📡 GNSS tracking started")
    
    def stop(self):
        """Stop GPS tracking thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("📡 GNSS tracking stopped")
    
    def _update_loop(self):
        """Background thread to update GPS data"""
        while self._running:
            try:
                if self.mode == 'gpsd':
                    self._update_gpsd()
                elif self.mode == 'serial':
                    self._update_serial()
                elif self.mode == 'simulator':
                    self._update_simulator()
                
                time.sleep(1)  # Update every second
            except Exception as e:
                print(f"⚠ GPS update error: {e}")
                time.sleep(1)
    
    def _update_gpsd(self):
        """Update from GPSD"""
        try:
            report = self.gpsd.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'lat'):
                    self.latitude = report.lat
                    self.longitude = report.lon
                    self.altitude = getattr(report, 'alt', 0.0)
                    self.speed = getattr(report, 'speed', 0.0) * 3.6  # m/s to km/h
                    self.heading = getattr(report, 'track', 0.0)
                    self.timestamp = datetime.now()
                    self.valid = True
                    self._update_position_history()
        except StopIteration:
            pass
    
    def _update_serial(self):
        """Update from serial NMEA GPS"""
        try:
            line = self.serial.readline().decode('ascii', errors='ignore').strip()
            if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                self._parse_gga(line)
            elif line.startswith('$GPRMC') or line.startswith('$GNRMC'):
                self._parse_rmc(line)
        except Exception as e:
            print(f"⚠ Serial GPS read error: {e}")
    
    def _parse_gga(self, sentence):
        """Parse NMEA GGA sentence"""
        parts = sentence.split(',')
        if len(parts) < 15:
            return
        
        try:
            # Parse latitude
            lat = float(parts[2][:2]) + float(parts[2][2:]) / 60
            if parts[3] == 'S':
                lat = -lat
            
            # Parse longitude
            lon = float(parts[4][:3]) + float(parts[4][3:]) / 60
            if parts[5] == 'W':
                lon = -lon
            
            self.latitude = lat
            self.longitude = lon
            self.fix_quality = int(parts[6])
            self.satellites = int(parts[7]) if parts[7] else 0
            self.altitude = float(parts[9]) if parts[9] else 0.0
            self.valid = self.fix_quality > 0
            self.timestamp = datetime.now()
            
            if self.valid:
                self._update_position_history()
        except (ValueError, IndexError) as e:
            pass
    
    def _parse_rmc(self, sentence):
        """Parse NMEA RMC sentence"""
        parts = sentence.split(',')
        if len(parts) < 12:
            return
        
        try:
            if parts[2] == 'A':  # Valid data
                # Speed over ground
                self.speed = float(parts[7]) * 1.852 if parts[7] else 0.0  # knots to km/h
                # Track angle
                self.heading = float(parts[8]) if parts[8] else 0.0
        except (ValueError, IndexError):
            pass
    
    def _update_simulator(self):
        """Simulate GPS drift (for testing)"""
        import random
        # Larger random movement to simulate rover driving
        self.latitude += random.uniform(-0.0001, 0.0001)  # ~11 meters per 0.0001 degrees
        self.longitude += random.uniform(-0.0001, 0.0001)
        self.speed = random.uniform(0, 15)  # 0-15 km/h
        self.heading = random.uniform(0, 360)
        self.satellites = random.randint(8, 12)
        self.fix_quality = 1
        self.timestamp = datetime.now()
    
    def _update_position_history(self):
        """Update position history and calculate distance"""
        if len(self.positions) > 0:
            last_lat, last_lon, _ = self.positions[-1]
            distance = self._haversine_distance(
                last_lat, last_lon,
                self.latitude, self.longitude
            )
            self.total_distance += distance
        
        self.positions.append((self.latitude, self.longitude, datetime.now()))
        
        # Keep only last 1000 positions
        if len(self.positions) > 1000:
            self.positions = self.positions[-1000:]
        
        # Update max speed
        if self.speed > self.max_speed:
            self.max_speed = self.speed
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in meters"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Radius of earth in meters
        
        return c * r
    
    def get_position(self):
        """Get current position as dict"""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'satellites': self.satellites,
            'fix_quality': self.fix_quality,
            'valid': self.valid,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'total_distance': round(self.total_distance, 2),
            'max_speed': round(self.max_speed, 2)
        }
    
    def get_coordinates_string(self):
        """Get formatted coordinates string"""
        if not self.valid:
            return "No GPS Fix"
        
        lat_dir = 'N' if self.latitude >= 0 else 'S'
        lon_dir = 'E' if self.longitude >= 0 else 'W'
        
        return f"{abs(self.latitude):.6f}°{lat_dir}, {abs(self.longitude):.6f}°{lon_dir}"
    
    def reset_statistics(self):
        """Reset tracking statistics"""
        self.total_distance = 0.0
        self.max_speed = 0.0
        self.positions = []
        print("📊 GNSS statistics reset")


# Simulator for testing
if __name__ == '__main__':
    print("Starting GNSS Tracker Test...")
    tracker = GNSSTracker(mode='simulator')
    tracker.start()
    
    try:
        while True:
            pos = tracker.get_position()
            print(f"\n📍 Position: {tracker.get_coordinates_string()}")
            print(f"   Altitude: {pos['altitude']:.1f}m")
            print(f"   Speed: {pos['speed']:.1f} km/h")
            print(f"   Satellites: {pos['satellites']}")
            print(f"   Distance: {pos['total_distance']:.1f}m")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        tracker.stop()
