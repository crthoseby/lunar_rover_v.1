#!/usr/bin/env python3
"""
Lunar Rover Web Control Server
Control your rover from any web browser
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import threading
import time
import os
from datetime import datetime
from motor_control import MotorController
from mars_delay import MarsDelaySimulator
from camera import CameraController
from line_follower import LineFollower
from gnss_tracker import GNSSTracker
from servo_control import ServoController
from audio_controller import AudioController
from log_manager import LogManager
from ground_conditions import GroundConditions
import config

app = Flask(__name__)
CORS(app)

# Global rover state
rover_state = {
    'motors': None,
    'delay_sim': None,
    'camera': None,
    'line_follower': None,
    'gnss': None,
    'servo': None,
    'audio': None,
    'logger': None,
    'ground': None,
    'delay_enabled': True,
    'delay_mode': 'average',
    'speed': config.DEFAULT_SPEED,
    'status': 'idle',
    'last_command': 'None',
    'commands_sent': 0,
    'total_delay': 0.0,
    'camera_active': True,
    'autonomous_mode': False
}


def initialize_rover():
    """Initialize rover components"""
    try:
        rover_state['logger'] = LogManager()
        rover_state['motors'] = MotorController()
        rover_state['delay_sim'] = MarsDelaySimulator(rover_state['delay_mode'])
        rover_state['camera'] = CameraController(resolution=(640, 480), framerate=15)
        rover_state['camera'].start_streaming()
        rover_state['line_follower'] = LineFollower(
            rover_state['camera'],
            rover_state['motors']
        )
        rover_state['gnss'] = GNSSTracker(mode='auto')  # Auto-detect real hardware
        rover_state['gnss'].start()
        rover_state['servo'] = ServoController()
        rover_state['audio'] = AudioController()
        rover_state['ground'] = GroundConditions(environment='moon')
        rover_state['status'] = 'ready'
        rover_state['logger'].log('Rover initialized - Hardware mode', 'success')
        print("✓ Rover initialized - Hardware mode")
        return True
    except Exception as e:
        print(f"✗ Rover initialization failed: {e}")
        rover_state['status'] = 'error'
        if rover_state['logger']:
            rover_state['logger'].log(f'Initialization failed: {e}', 'error')
        return False


def execute_with_delay(command_func, command_name, *args, **kwargs):
    """Execute command with Mars delay simulation"""
    rover_state['status'] = 'busy'
    rover_state['last_command'] = command_name
    
    if rover_state['delay_enabled'] and rover_state['delay_sim']:
        delay = rover_state['delay_sim'].get_delay()
        rover_state['total_delay'] += delay
        rover_state['commands_sent'] += 1
        
        if rover_state['logger']:
            rover_state['logger'].log(f"Command: {command_name} | Delay: {delay:.2f}s", 'command')
        
        print(f"\n[EARTH] Command: {command_name} | Delay: {delay:.2f}s")
        time.sleep(delay)
        print(f"[MARS] Executing: {command_name}")
    
    command_func(*args, **kwargs)
    
    # Update GNSS position based on movement (simulator mode)
    if rover_state['gnss'] and command_name in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT']:
        simulate_movement(command_name, config.DEFAULT_MOVE_DURATION)
    
    if rover_state['logger']:
        rover_state['logger'].log(f"Executed: {command_name}", 'success')
    
    rover_state['status'] = 'ready'


def simulate_movement(direction, duration):
    """Simulate GNSS position change based on rover movement with ground conditions"""
    if not rover_state['gnss']:
        return
    
    import random
    
    # Base speed and planned distance
    speed_ms = 0.5  # meters per second
    planned_distance = speed_ms * duration  # meters
    
    # Apply ground conditions if available
    if rover_state['ground']:
        # Simulate terrain effects
        terrain_result = rover_state['ground'].simulate_movement(planned_distance, speed_percent=75)
        actual_distance = terrain_result['actual_distance']
        
        # Log terrain effects
        if terrain_result['stuck']:
            rover_state['logger'].log(f"⚠️ Rover stuck in {terrain_result['terrain']}!", 'warning')
            return  # Don't update position if stuck
        
        if terrain_result['wheel_slip'] > 50:
            rover_state['logger'].log(f"⚠️ High wheel slip: {terrain_result['wheel_slip']}% on {terrain_result['terrain']}", 'warning')
    else:
        actual_distance = planned_distance
    
    # Convert distance to degrees (1 degree ≈ 111km at equator)
    distance_deg = actual_distance / 111000
    
    if direction == 'FORWARD':
        rover_state['gnss'].latitude += distance_deg + random.uniform(-distance_deg*0.1, distance_deg*0.1)
        rover_state['gnss'].heading = 0
        rover_state['gnss'].speed = speed_ms * 3.6  # convert to km/h
    elif direction == 'BACKWARD':
        rover_state['gnss'].latitude -= distance_deg + random.uniform(-distance_deg*0.1, distance_deg*0.1)
        rover_state['gnss'].heading = 180
        rover_state['gnss'].speed = speed_ms * 3.6
    elif direction == 'LEFT':
        rover_state['gnss'].longitude -= distance_deg + random.uniform(-distance_deg*0.1, distance_deg*0.1)
        rover_state['gnss'].heading = 270
        rover_state['gnss'].speed = speed_ms * 3.6
    elif direction == 'RIGHT':
        rover_state['gnss'].longitude += distance_deg + random.uniform(-distance_deg*0.1, distance_deg*0.1)
        rover_state['gnss'].heading = 90
        rover_state['gnss'].speed = speed_ms * 3.6
    
    rover_state['gnss']._update_position_history()


@app.route('/')
def index():
    """Serve the main control page"""
    return render_template('index.html')


@app.route('/test')
def test_camera():
    """Serve camera test page"""
    return render_template('test_camera.html')


@app.route('/simple')
def simple_control():
    """Serve simple control page"""
    with open('SIMPLE_CONTROL.html', 'r') as f:
        return f.read()


@app.route('/api/status')
def get_status():
    """Get current rover status"""
    return jsonify({
        'status': rover_state['status'],
        'last_command': rover_state['last_command'],
        'speed': rover_state['speed'],
        'delay_enabled': rover_state['delay_enabled'],
        'delay_mode': rover_state['delay_mode'],
        'commands_sent': rover_state['commands_sent'],
        'total_delay': round(rover_state['total_delay'], 2),
        'avg_delay': round(rover_state['total_delay'] / rover_state['commands_sent'], 2) if rover_state['commands_sent'] > 0 else 0
    })


@app.route('/api/command/<action>', methods=['POST', 'GET'])
def send_command(action):
    """Send movement command to rover"""
    print(f"🎯 COMMAND RECEIVED: {action.upper()}")
    
    if rover_state['status'] == 'error':
        return jsonify({'success': False, 'error': 'Rover not initialized'}), 500
    
    if rover_state['status'] == 'busy':
        return jsonify({'success': False, 'error': 'Rover is busy'}), 409
    
    # Get duration from JSON body or use default
    try:
        duration = request.json.get('duration', config.DEFAULT_MOVE_DURATION) if request.json else config.DEFAULT_MOVE_DURATION
    except:
        duration = config.DEFAULT_MOVE_DURATION
    
    commands = {
        'forward': lambda: rover_state['motors'].forward(duration),
        'backward': lambda: rover_state['motors'].backward(duration),
        'left': lambda: rover_state['motors'].left(duration),
        'right': lambda: rover_state['motors'].right(duration),
        'stop': lambda: rover_state['motors'].stop()
    }
    
    if action not in commands:
        return jsonify({'success': False, 'error': 'Invalid command'}), 400
    
    # Execute command in background thread
    thread = threading.Thread(
        target=execute_with_delay,
        args=(commands[action], action.upper())
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'command': action})


@app.route('/api/speed', methods=['POST'])
def set_speed():
    """Set rover speed"""
    data = request.json
    speed = data.get('speed', 75)
    speed = max(0, min(100, int(speed)))
    
    rover_state['speed'] = speed
    if rover_state['motors']:
        rover_state['motors'].set_speed(speed)
    
    return jsonify({'success': True, 'speed': speed})


@app.route('/api/delay', methods=['POST'])
def toggle_delay():
    """Toggle Mars delay simulation"""
    data = request.json
    rover_state['delay_enabled'] = data.get('enabled', not rover_state['delay_enabled'])
    
    return jsonify({'success': True, 'delay_enabled': rover_state['delay_enabled']})


@app.route('/api/delay/mode', methods=['POST'])
def set_delay_mode():
    """Set delay mode"""
    data = request.json
    mode = data.get('mode', 'average')
    
    valid_modes = ['min', 'max', 'average', 'random']
    if mode not in valid_modes:
        return jsonify({'success': False, 'error': 'Invalid mode'}), 400
    
    rover_state['delay_mode'] = mode
    if rover_state['delay_sim']:
        rover_state['delay_sim'].set_mode(mode)
    
    return jsonify({'success': True, 'mode': mode})


@app.route('/api/stats/reset', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    rover_state['commands_sent'] = 0
    rover_state['total_delay'] = 0.0
    rover_state['last_command'] = 'None'
    
    return jsonify({'success': True})


def generate_video_stream():
    """Generate video frames for streaming"""
    while True:
        if rover_state['camera'] and rover_state['camera_active']:
            frame = rover_state['camera'].capture_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/camera/info')
def camera_info():
    """Get camera information"""
    if rover_state['camera']:
        info = rover_state['camera'].get_info()
        info['active'] = rover_state['camera_active']
        return jsonify(info)
    return jsonify({'available': False})


@app.route('/api/camera/toggle', methods=['POST'])
def toggle_camera():
    """Toggle camera on/off"""
    rover_state['camera_active'] = not rover_state['camera_active']
    return jsonify({'success': True, 'active': rover_state['camera_active']})


@app.route('/api/camera/snapshot', methods=['POST'])
def camera_snapshot():
    """Capture and save a snapshot"""
    if rover_state['camera']:
        try:
            # Create snapshots directory if it doesn't exist
            snapshots_dir = os.path.join(os.path.dirname(__file__), 'snapshots')
            os.makedirs(snapshots_dir, exist_ok=True)
            
            # Generate filename with timestamp (no colons for Windows compatibility)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'rover_snapshot_{timestamp}.jpg'
            filepath = os.path.join(snapshots_dir, filename)
            
            # Capture and save frame
            frame = rover_state['camera'].capture_frame()
            with open(filepath, 'wb') as f:
                f.write(frame)
            
            print(f"📸 Snapshot saved: {filename}")
            
            # Return the frame for download
            return Response(frame, mimetype='image/jpeg', 
                          headers={'Content-Disposition': f'attachment; filename={filename}'})
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Camera not available'}), 500


@app.route('/api/autonomous/start', methods=['POST'])
def start_autonomous():
    """Start autonomous line following mode"""
    if not rover_state['line_follower']:
        return jsonify({'success': False, 'error': 'Line follower not available'}), 500
    
    if rover_state['autonomous_mode']:
        return jsonify({'success': False, 'error': 'Already in autonomous mode'}), 409
    
    success = rover_state['line_follower'].start()
    if success:
        rover_state['autonomous_mode'] = True
        return jsonify({'success': True, 'message': 'Autonomous mode started'})
    return jsonify({'success': False, 'error': 'Failed to start autonomous mode'}), 500


@app.route('/api/autonomous/stop', methods=['POST'])
def stop_autonomous():
    """Stop autonomous line following mode"""
    if not rover_state['line_follower']:
        return jsonify({'success': False, 'error': 'Line follower not available'}), 500
    
    success = rover_state['line_follower'].stop()
    rover_state['autonomous_mode'] = False
    return jsonify({'success': True, 'message': 'Autonomous mode stopped'})


@app.route('/api/autonomous/status')
def autonomous_status():
    """Get autonomous mode status"""
    if rover_state['line_follower']:
        return jsonify(rover_state['line_follower'].get_status())
    return jsonify({'active': False, 'available': False})


@app.route('/api/autonomous/config', methods=['POST'])
def update_autonomous_config():
    """Update autonomous mode configuration"""
    if not rover_state['line_follower']:
        return jsonify({'success': False, 'error': 'Line follower not available'}), 500
    
    data = request.json
    rover_state['line_follower'].update_config(data)
    return jsonify({'success': True, 'config': rover_state['line_follower'].config})


@app.route('/api/gnss/position')
def gnss_position():
    """Get current GNSS position"""
    if rover_state['gnss']:
        return jsonify(rover_state['gnss'].get_position())
    return jsonify({'valid': False, 'error': 'GNSS not available'})


@app.route('/api/gnss/reset', methods=['POST'])
def gnss_reset():
    """Reset GNSS statistics"""
    if rover_state['gnss']:
        rover_state['gnss'].reset_statistics()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'GNSS not available'}), 500


@app.route('/api/servo/position', methods=['POST'])
def set_servo_position():
    """Set servo positions"""
    if not rover_state['servo']:
        return jsonify({'success': False, 'error': 'Servo not available'}), 500
    
    data = request.json
    pan = data.get('pan')
    tilt = data.get('tilt')
    
    try:
        if pan is not None and tilt is not None:
            rover_state['servo'].set_position(pan, tilt)
        elif pan is not None:
            rover_state['servo'].set_pan(pan)
        elif tilt is not None:
            rover_state['servo'].set_tilt(tilt)
        
        return jsonify({'success': True, 'position': rover_state['servo'].get_position()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/servo/center', methods=['POST'])
def center_servo():
    """Center servos"""
    if rover_state['servo']:
        rover_state['servo'].center()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Servo not available'}), 500


@app.route('/api/servo/status')
def servo_status():
    """Get servo status"""
    if rover_state['servo']:
        return jsonify(rover_state['servo'].get_position())
    return jsonify({'pan': 90, 'tilt': 90, 'available': False})


@app.route('/api/audio/record/start', methods=['POST'])
def start_audio_recording():
    """Start audio recording"""
    if not rover_state['audio']:
        return jsonify({'success': False, 'error': 'Audio not available'}), 500
    
    success = rover_state['audio'].start_recording()
    return jsonify({'success': success})


@app.route('/api/audio/record/stop', methods=['POST'])
def stop_audio_recording():
    """Stop audio recording"""
    if not rover_state['audio']:
        return jsonify({'success': False, 'error': 'Audio not available'}), 500
    
    success = rover_state['audio'].stop_recording()
    return jsonify({'success': success})


@app.route('/api/audio/status')
def audio_status():
    """Get audio status"""
    if rover_state['audio']:
        return jsonify(rover_state['audio'].get_status())
    return jsonify({'enabled': False, 'recording': False, 'playing': False})


@app.route('/api/logs/export', methods=['POST'])
def export_log():
    """Export current log"""
    if not rover_state['logger']:
        return jsonify({'success': False, 'error': 'Logger not available'}), 500
    
    filepath = rover_state['logger'].export_log()
    if filepath:
        return jsonify({'success': True, 'filepath': filepath})
    return jsonify({'success': False, 'error': 'Export failed'}), 500


@app.route('/api/logs/list')
def list_logs():
    """Get list of log files"""
    if rover_state['logger']:
        return jsonify({'files': rover_state['logger'].get_log_files()})
    return jsonify({'files': []})


@app.route('/api/logs/stats')
def log_stats():
    """Get logging statistics"""
    if rover_state['logger']:
        return jsonify(rover_state['logger'].get_stats())
    return jsonify({'total_files': 0, 'total_size_mb': 0})


@app.route('/api/logs/recent')
def recent_logs():
    """Get recent log entries"""
    if rover_state['logger']:
        count = request.args.get('count', 50, type=int)
        logs = rover_state['logger'].get_recent_logs(count)
        return jsonify({'logs': logs})
    return jsonify({'logs': []})


# Ground conditions API endpoints
@app.route('/api/ground/status')
def ground_status():
    """Get ground conditions status"""
    if rover_state['ground']:
        status = rover_state['ground'].get_status()
        warnings = rover_state['ground'].get_warnings()
        return jsonify({**status, 'warnings': warnings})
    return jsonify({'error': 'Ground conditions not available'})


@app.route('/api/ground/environment/<env>')
def set_environment(env):
    """Set environment (moon/mars/earth)"""
    if rover_state['ground'] and env in ['moon', 'mars', 'earth']:
        rover_state['ground'].set_environment(env)
        rover_state['logger'].log(f"Environment changed to {env.upper()}", 'system')
        return jsonify({'success': True, 'environment': env})
    return jsonify({'success': False, 'error': 'Invalid environment'})


@app.route('/api/ground/terrain/<terrain>')
def set_terrain(terrain):
    """Set terrain type"""
    if rover_state['ground']:
        terrain_types = list(rover_state['ground'].TERRAIN_TYPES.keys())
        if terrain in terrain_types or terrain == 'random':
            rover_state['ground'].change_terrain(None if terrain == 'random' else terrain)
            return jsonify({'success': True, 'terrain': rover_state['ground'].current_terrain})
        return jsonify({'success': False, 'error': 'Invalid terrain type', 'available': terrain_types})
    return jsonify({'success': False, 'error': 'Ground conditions not available'})


@app.route('/api/ground/unstuck', methods=['POST'])
def unstuck():
    """Attempt to free stuck rover"""
    if rover_state['ground']:
        result = rover_state['ground'].attempt_unstuck()
        rover_state['logger'].log(result['message'], 'system')
        return jsonify(result)
    return jsonify({'success': False, 'error': 'Ground conditions not available'})


@app.route('/api/ground/clean_dust', methods=['POST'])
def clean_dust():
    """Clean dust from rover"""
    if rover_state['ground']:
        rover_state['ground'].clean_dust()
        rover_state['logger'].log("Dust cleaning performed", 'system')
        return jsonify({'success': True, 'dust_level': rover_state['ground'].dust_accumulation * 100})
    return jsonify({'success': False, 'error': 'Ground conditions not available'})


@app.route('/api/ground/reset_stats', methods=['POST'])
def reset_ground_stats():
    """Reset ground conditions statistics"""
    if rover_state['ground']:
        rover_state['ground'].reset_stats()
        rover_state['logger'].log("Ground statistics reset", 'system')
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Ground conditions not available'})


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🌙 LUNAR ROVER WEB CONTROL SERVER 🚗")
    print("="*60)
    
    if initialize_rover():
        print("\n📡 Starting web server...")
        print("="*60)
        print("🌐 Control Interface:")
        print("   → http://localhost:5000")
        print("   → http://YOUR_PI_IP:5000 (from other devices)")
        print("\n💡 Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down server...")
        finally:
            if rover_state['motors']:
                rover_state['motors'].cleanup()
            if rover_state['camera']:
                rover_state['camera'].cleanup()
            if rover_state['gnss']:
                rover_state['gnss'].stop()
            if rover_state['servo']:
                rover_state['servo'].cleanup()
            if rover_state['audio']:
                rover_state['audio'].cleanup()
            print("✓ Server stopped")
    else:
        print("✗ Failed to start server - rover initialization failed")


if __name__ == "__main__":
    main()
