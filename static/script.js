// Lunar Rover Web Controller
console.log('🚀 Script loaded - Version 20251118-2055');
const API_BASE = '';
let statusInterval;
let autoScroll = true;

// Dummy log function to prevent errors (we now use server-side logs only)
function log(message, type = 'info') {
    // Do nothing - logs are now server-side only
}

// Clear console log
function clearConsole() {
    const consoleEl = document.getElementById('console');
    if (consoleEl) {
        consoleEl.innerHTML = '<div class="log-entry log-info"><span class="timestamp">[--:--:--]</span> Log cleared</div>';
    }
}

// Toggle auto-scroll
function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const btn = document.getElementById('auto-scroll-toggle');
    if (btn) {
        btn.textContent = autoScroll ? '🔒 Auto-Scroll: ON' : '🔓 Auto-Scroll: OFF';
        btn.style.background = autoScroll ? 'rgba(76, 175, 80, 0.2)' : 'rgba(244, 67, 54, 0.2)';
        btn.style.borderColor = autoScroll ? 'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)';
        btn.style.color = autoScroll ? '#81C784' : '#E57373';
    }
}

// Send command to rover
async function sendCommand(action) {
    const statusEl = document.getElementById('status');
    
    console.log(`🚀 sendCommand called: ${action}`);
    
    try {
        statusEl.textContent = 'Busy';
        statusEl.className = 'status-busy';
        
        console.log(`📡 Sending POST to /api/command/${action}`);
        
        const response = await fetch(`${API_BASE}/api/command/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        console.log(`✅ Response:`, data);
        
        if (!data.success) {
            console.error(`❌ Command failed: ${data.error}`);
        }
    } catch (error) {
        console.error(`❌ Connection error: ${error.message}`);
    }
}

// Update status display
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        // Update status
        const statusEl = document.getElementById('status');
        statusEl.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        statusEl.className = `status-${data.status}`;
        
        // Update other displays
        document.getElementById('last-command').textContent = data.last_command;
        document.getElementById('current-speed').textContent = data.speed;
        document.getElementById('commands-sent').textContent = data.commands_sent;
        document.getElementById('total-delay').textContent = data.total_delay + 's';
        document.getElementById('avg-delay').textContent = data.avg_delay + 's';
        
        // Update GNSS data
        updateGNSS();
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

// Set speed
async function setSpeed(speed) {
    try {
        const response = await fetch(`${API_BASE}/api/speed`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speed: parseInt(speed) })
        });
        
        const data = await response.json();
        if (data.success) {
            log(`Speed set to ${speed}%`, 'info');
        }
    } catch (error) {
        log(`✗ Failed to set speed: ${error.message}`, 'error');
    }
}

// Toggle delay
async function toggleDelay(enabled) {
    try {
        const response = await fetch(`${API_BASE}/api/delay`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        });
        
        const data = await response.json();
        if (data.success) {
            log(`Mars delay ${enabled ? 'enabled' : 'disabled'}`, 'info');
        }
    } catch (error) {
        log(`✗ Failed to toggle delay: ${error.message}`, 'error');
    }
}

// Set delay mode
async function setDelayMode(mode) {
    try {
        const response = await fetch(`${API_BASE}/api/delay/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        
        const data = await response.json();
        if (data.success) {
            log(`Delay mode set to: ${mode}`, 'info');
        }
    } catch (error) {
        log(`✗ Failed to set delay mode: ${error.message}`, 'error');
    }
}

// Reset statistics
async function resetStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            log('Statistics reset', 'info');
            updateStatus();
        }
    } catch (error) {
        log(`✗ Failed to reset stats: ${error.message}`, 'error');
    }
}

// Toggle camera
async function toggleCamera() {
    try {
        const response = await fetch(`${API_BASE}/api/camera/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            const toggleBtn = document.getElementById('toggle-camera');
            if (toggleBtn) {
                toggleBtn.textContent = data.active ? '📷 Camera ON' : '📷 Camera OFF';
            }
            log(`Camera ${data.active ? 'enabled' : 'disabled'}`, 'info');
            updateCameraStatus();
        }
    } catch (error) {
        log(`✗ Failed to toggle camera: ${error.message}`, 'error');
    }
}

// Take snapshot
async function takeSnapshot() {
    try {
        log('Taking snapshot...', 'command');
        const response = await fetch(`${API_BASE}/api/camera/snapshot`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rover_snapshot_${Date.now()}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            log('✓ Snapshot saved', 'success');
        } else {
            log('✗ Failed to capture snapshot', 'error');
        }
    } catch (error) {
        log(`✗ Snapshot error: ${error.message}`, 'error');
    }
}

// Update camera status
async function updateCameraStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/camera/info`);
        const data = await response.json();
        
        const statusEl = document.getElementById('camera-status');
        const typeEl = document.getElementById('camera-type');
        const resEl = document.getElementById('camera-resolution');
        
        if (statusEl && data.active) {
            statusEl.className = 'camera-status-active';
        } else if (statusEl) {
            statusEl.className = 'camera-status-inactive';
        }
        
        if (typeEl) {
            typeEl.textContent = data.active ? 'LIVE' : 'OFF';
        }
        
        if (resEl && data.resolution) {
            resEl.textContent = `${data.resolution[0]}x${data.resolution[1]} @ ${data.framerate}fps | ${data.type.toUpperCase()}`;
        }
    } catch (error) {
        console.error('Camera status update failed:', error);
    }
}

// Start autonomous mode
async function startAutonomous() {
    try {
        // Get current settings
        const lineColor = document.getElementById('line-color').value;
        const baseSpeed = parseInt(document.getElementById('auto-speed').value);
        
        // Update config first
        await fetch(`${API_BASE}/api/autonomous/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                line_color: lineColor,
                base_speed: baseSpeed
            })
        });
        
        // Start autonomous mode
        const response = await fetch(`${API_BASE}/api/autonomous/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            log('🤖 Autonomous mode started', 'success');
            document.getElementById('start-autonomous').disabled = true;
            document.getElementById('stop-autonomous').disabled = false;
            updateAutonomousStatus();
        } else {
            log(`✗ Failed to start: ${data.error}`, 'error');
        }
    } catch (error) {
        log(`✗ Autonomous start error: ${error.message}`, 'error');
    }
}

// Stop autonomous mode
async function stopAutonomous() {
    try {
        const response = await fetch(`${API_BASE}/api/autonomous/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            log('🛑 Autonomous mode stopped', 'info');
            document.getElementById('start-autonomous').disabled = false;
            document.getElementById('stop-autonomous').disabled = true;
            updateAutonomousStatus();
        }
    } catch (error) {
        log(`✗ Autonomous stop error: ${error.message}`, 'error');
    }
}

// Update GNSS position
async function updateGNSS() {
    try {
        const response = await fetch(`${API_BASE}/api/gnss/position`);
        const data = await response.json();
        
        if (data.valid) {
            // Format coordinates
            const latDir = data.latitude >= 0 ? 'N' : 'S';
            const lonDir = data.longitude >= 0 ? 'E' : 'W';
            const coords = `${Math.abs(data.latitude).toFixed(6)}°${latDir}, ${Math.abs(data.longitude).toFixed(6)}°${lonDir}`;
            
            document.getElementById('gnss-coords').textContent = coords;
            document.getElementById('gnss-altitude').textContent = `${data.altitude.toFixed(1)} m`;
            document.getElementById('gnss-speed').textContent = `${data.speed.toFixed(1)} km/h`;
            document.getElementById('gnss-sats').textContent = data.satellites;
            document.getElementById('gnss-distance').textContent = `${data.total_distance.toFixed(1)} m`;
        } else {
            document.getElementById('gnss-coords').textContent = 'Acquiring fix...';
        }
    } catch (error) {
        console.error('GNSS update failed:', error);
    }
}

// Update system component status
async function updateSystemStatus() {
    try {
        // Camera status
        try {
            const cameraResponse = await fetch(`${API_BASE}/api/camera/info`);
            if (cameraResponse.ok) {
                const cameraData = await cameraResponse.json();
                updateComponentStatus('camera', cameraData.active, cameraData.camera_type || 'Offline');
            } else {
                updateComponentStatus('camera', false, 'Error');
            }
        } catch (e) {
            updateComponentStatus('camera', false, 'Error');
        }
        
        // Audio status
        try {
            const audioResponse = await fetch(`${API_BASE}/api/audio/status`);
            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                const audioStatus = audioData.recording ? 'Recording' : (audioData.enabled ? 'Ready' : 'Disabled');
                updateComponentStatus('audio', audioData.enabled, audioStatus);
            } else {
                updateComponentStatus('audio', false, 'Error');
            }
        } catch (e) {
            updateComponentStatus('audio', false, 'Error');
        }
        
        // GNSS status
        try {
            const gnssResponse = await fetch(`${API_BASE}/api/gnss/position`);
            if (gnssResponse.ok) {
                const gnssData = await gnssResponse.json();
                updateComponentStatus('gnss', gnssData.valid, gnssData.valid ? `${gnssData.satellites} Sats` : 'No Fix');
            } else {
                updateComponentStatus('gnss', false, 'Error');
            }
        } catch (e) {
            updateComponentStatus('gnss', false, 'Error');
        }
        
        // Servo status
        try {
            const servoResponse = await fetch(`${API_BASE}/api/servo/status`);
            if (servoResponse.ok) {
                const servoData = await servoResponse.json();
                const servoAvailable = servoData.available !== false;
                updateComponentStatus('servo', servoAvailable, `P:${servoData.pan}° T:${servoData.tilt}°`);
            } else {
                updateComponentStatus('servo', false, 'Error');
            }
        } catch (e) {
            updateComponentStatus('servo', false, 'Error');
        }
        
        // Motor status (based on main status)
        try {
            const statusResponse = await fetch(`${API_BASE}/api/status`);
            if (statusResponse.ok) {
                const statusData = await statusResponse.json();
                const motorActive = statusData.status !== 'error';
                updateComponentStatus('motor', motorActive, statusData.status.charAt(0).toUpperCase() + statusData.status.slice(1));
            } else {
                updateComponentStatus('motor', false, 'Error');
            }
        } catch (e) {
            updateComponentStatus('motor', false, 'Error');
        }
        
    } catch (error) {
        console.error('System status update failed:', error);
    }
}

function updateComponentStatus(component, isActive, text) {
    const indicator = document.getElementById(`sys-${component}-status`);
    const textEl = document.getElementById(`sys-${component}-text`);
    
    if (indicator) {
        indicator.className = 'status-indicator ' + (isActive ? 'active' : 'inactive');
    }
    if (textEl) {
        textEl.textContent = text;
        textEl.style.color = isActive ? '#4CAF50' : '#666';
    }
}

// Reset GNSS statistics
async function resetGNSS() {
    try {
        const response = await fetch(`${API_BASE}/api/gnss/reset`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            log('GNSS statistics reset', 'info');
            updateGNSS();
        }
    } catch (error) {
        log(`Reset failed: ${error.message}`, 'error');
    }
}

// Update transmission log from server
async function updateTransmissionLog() {
    console.log('🔔 updateTransmissionLog called'); // Debug - check if function runs
    try {
        console.log('📡 Fetching logs from API...'); // Debug
        const response = await fetch(`${API_BASE}/api/logs/recent?count=20`);
        console.log('✅ API response status:', response.status); // Debug
        
        if (!response.ok) {
            console.error('❌ Logs API failed:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log('📦 Received logs:', data); // Debug
        const consoleEl = document.getElementById('console');
        
        if (!consoleEl) {
            console.error('❌ Console element not found');
            return;
        }
        
        console.log('🧹 Console element found, clearing...'); // Debug
        // Always clear the console
        consoleEl.innerHTML = '';
        
        if (data.logs && data.logs.length > 0) {
            console.log(`✏️ Rendering ${data.logs.length} log entries`); // Debug
            data.logs.forEach(logEntry => {
                const entry = document.createElement('div');
                entry.className = `log-entry log-${logEntry.type || 'info'}`;
                // Extract just the time from timestamp
                const timePart = logEntry.timestamp ? logEntry.timestamp.substring(11, 19) : '';
                entry.innerHTML = `<span class="timestamp">[${timePart}]</span> ${logEntry.message}`;
                consoleEl.appendChild(entry);
            });
            
            // Auto-scroll to bottom if enabled
            if (autoScroll) {
                consoleEl.scrollTop = consoleEl.scrollHeight;
            }
        } else {
            console.log('No logs received, showing placeholder'); // Debug
            // Show placeholder if no logs
            const entry = document.createElement('div');
            entry.className = 'log-entry log-info';
            entry.innerHTML = '<span class="timestamp">[--:--:--]</span> No logs yet. Press a button to start.';
            consoleEl.appendChild(entry);
        }
    } catch (error) {
        console.error('updateTransmissionLog error:', error); // Debug
        // Show error in console
        const consoleEl = document.getElementById('console');
        if (consoleEl) {
            consoleEl.innerHTML = '<div class="log-entry log-error"><span class="timestamp">[ERROR]</span> Failed to load logs</div>';
        }
    }
}

// Update ground conditions
async function updateGroundConditions() {
    try {
        const response = await fetch(`${API_BASE}/api/ground/status`);
        const data = await response.json();
        
        if (data.environment) {
            // Update environment and gravity
            document.getElementById('ground-environment').textContent = data.environment.toUpperCase();
            document.getElementById('ground-gravity').textContent = `${data.gravity} m/s² (${data.gravity_percent}%)`;
            
            // Update terrain
            document.getElementById('ground-terrain').textContent = data.terrain;
            
            // Update wheel slip
            document.getElementById('ground-slip').textContent = `${data.wheel_slip}%`;
            document.getElementById('slip-progress').style.width = `${data.wheel_slip}%`;
            
            // Update dust level
            document.getElementById('ground-dust').textContent = `${data.dust_accumulation}%`;
            document.getElementById('dust-progress').style.width = `${data.dust_accumulation}%`;
            
            // Update status
            const statusText = document.getElementById('ground-status-text');
            if (data.stuck) {
                statusText.textContent = 'STUCK';
                statusText.className = 'ground-status-text error';
            } else if (data.wheel_slip > 50 || data.dust_accumulation > 70) {
                statusText.textContent = 'Warning';
                statusText.className = 'ground-status-text warning';
            } else {
                statusText.textContent = 'Normal';
                statusText.className = 'ground-status-text';
            }
            
            // Display warnings
            const warningsDiv = document.getElementById('ground-warnings');
            if (data.warnings && data.warnings.length > 0) {
                warningsDiv.style.display = 'flex';
                warningsDiv.innerHTML = data.warnings.map(w => 
                    `<div class="ground-warning ${w.level}">${w.message}</div>`
                ).join('');
            } else {
                warningsDiv.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Ground conditions update failed:', error);
    }
}

// Clean dust from rover
async function cleanDust() {
    try {
        log('🧹 Cleaning dust from rover...', 'command');
        const response = await fetch(`${API_BASE}/api/ground/clean_dust`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            log(`✓ Dust cleaned. New level: ${data.dust_level.toFixed(1)}%`, 'success');
            updateGroundConditions();
        }
    } catch (error) {
        log(`✗ Dust cleaning failed: ${error.message}`, 'error');
    }
}

// Attempt to unstuck rover
async function unstuckRover() {
    try {
        log('🆘 Attempting to free rover...', 'command');
        const response = await fetch(`${API_BASE}/api/ground/unstuck`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            log('✓ Rover freed from stuck condition!', 'success');
        } else {
            log('✗ Unstuck attempt failed. Try again.', 'warning');
        }
        updateGroundConditions();
    } catch (error) {
        log(`✗ Unstuck operation failed: ${error.message}`, 'error');
    }
}

// Change to random terrain
async function changeTerrain() {
    try {
        log('🔄 Changing terrain...', 'info');
        const response = await fetch(`${API_BASE}/api/ground/terrain/random`);
        
        const data = await response.json();
        if (data.success) {
            log(`⛰️ Terrain changed to: ${data.terrain}`, 'info');
            updateGroundConditions();
        }
    } catch (error) {
        log(`✗ Terrain change failed: ${error.message}`, 'error');
    }
}

// Update autonomous status display
async function updateAutonomousStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/autonomous/status`);
        const data = await response.json();
        
        const statusEl = document.getElementById('auto-status');
        if (statusEl) {
            if (data.active) {
                statusEl.textContent = `Active - ${data.last_direction}`;
                statusEl.className = 'auto-status-active';
            } else {
                statusEl.textContent = 'Inactive';
                statusEl.className = 'auto-status-inactive';
            }
        }
    } catch (error) {
        console.error('Autonomous status update failed:', error);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Direction buttons
    document.querySelectorAll('.btn-direction').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            sendCommand(action);
        });
    });
    
    // Speed slider
    const speedSlider = document.getElementById('speed-slider');
    speedSlider.addEventListener('change', (e) => {
        setSpeed(e.target.value);
    });
    speedSlider.addEventListener('input', (e) => {
        document.getElementById('current-speed').textContent = e.target.value;
    });
    
    // Delay toggle
    document.getElementById('delay-toggle').addEventListener('change', (e) => {
        toggleDelay(e.target.checked);
    });
    
    // Delay mode
    document.getElementById('delay-mode').addEventListener('change', (e) => {
        setDelayMode(e.target.value);
    });
    
    // Reset stats button
    document.getElementById('reset-stats').addEventListener('click', resetStats);
    
    // Camera controls
    const toggleCameraBtn = document.getElementById('toggle-camera');
    if (toggleCameraBtn) {
        toggleCameraBtn.addEventListener('click', toggleCamera);
    }
    
    const snapshotBtn = document.getElementById('snapshot');
    if (snapshotBtn) {
        snapshotBtn.addEventListener('click', takeSnapshot);
    }
    
    // Autonomous mode controls
    const startAutoBtn = document.getElementById('start-autonomous');
    if (startAutoBtn) {
        startAutoBtn.addEventListener('click', startAutonomous);
    }
    
    const stopAutoBtn = document.getElementById('stop-autonomous');
    if (stopAutoBtn) {
        stopAutoBtn.addEventListener('click', stopAutonomous);
    }
    
    // Auto speed slider
    const autoSpeedSlider = document.getElementById('auto-speed');
    if (autoSpeedSlider) {
        autoSpeedSlider.addEventListener('input', (e) => {
            document.getElementById('auto-speed-value').textContent = e.target.value + '%';
        });
    }
    
    // GNSS reset button
    const resetGNSSBtn = document.getElementById('reset-gnss');
    if (resetGNSSBtn) {
        resetGNSSBtn.addEventListener('click', resetGNSS);
    }
    
    // Ground conditions buttons
    const cleanDustBtn = document.getElementById('clean-dust');
    if (cleanDustBtn) {
        cleanDustBtn.addEventListener('click', cleanDust);
    }
    
    const unstuckBtn = document.getElementById('unstuck');
    if (unstuckBtn) {
        unstuckBtn.addEventListener('click', unstuckRover);
    }
    
    const changeTerrainBtn = document.getElementById('change-terrain');
    if (changeTerrainBtn) {
        changeTerrainBtn.addEventListener('click', changeTerrain);
    }
    
    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        const key = e.key.toLowerCase();
        const commands = {
            'w': 'forward',
            'a': 'left',
            's': 'backward',
            'd': 'right',
            'x': 'stop'
        };
        
        if (commands[key]) {
            e.preventDefault();
            sendCommand(commands[key]);
            
            // Visual feedback
            const btn = document.querySelector(`[data-action="${commands[key]}"]`);
            if (btn) {
                btn.classList.add('active');
                setTimeout(() => btn.classList.remove('active'), 200);
            }
        }
    });
    
    // Start status updates
    console.log('🎬 Starting intervals...');
    updateStatus();
    updateCameraStatus();
    updateAutonomousStatus();
    updateSystemStatus();
    updateGroundConditions();
    console.log('🔄 Calling updateTransmissionLog for first time...');
    updateTransmissionLog();
    console.log('⏰ Setting up interval...');
    statusInterval = setInterval(() => {
        updateStatus();
        updateCameraStatus();
        updateAutonomousStatus();
        updateSystemStatus();
        updateGroundConditions();
        updateTransmissionLog();
    }, 500);
    console.log('✅ Intervals started');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
});
