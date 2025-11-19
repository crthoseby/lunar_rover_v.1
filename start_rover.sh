#!/bin/bash
# Start Lunar Rover Web Server

echo "🌙 Starting Lunar Rover Web Server..."

# Get IP address
IP=$(hostname -I | awk '{print $1}')

# Start the server
python3 web_server.py &

# Save PID to file for stopping later
echo $! > rover.pid

echo ""
echo "============================================================"
echo "✅ Rover Server Started!"
echo "============================================================"
echo "Access the control panel from:"
echo "  • Local:   http://localhost:5000"
echo "  • Network: http://$IP:5000"
echo ""
echo "From your phone/tablet, connect to the same WiFi and visit:"
echo "  http://$IP:5000"
echo ""
echo "To stop the server: ./stop_rover.sh"
echo "============================================================"
