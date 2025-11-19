#!/bin/bash
# Stop Lunar Rover Web Server

echo "🛑 Stopping Lunar Rover Web Server..."

if [ -f rover.pid ]; then
    PID=$(cat rover.pid)
    kill $PID 2>/dev/null
    rm rover.pid
    echo "✅ Server stopped (PID: $PID)"
else
    # Fallback: find and kill python process running web_server.py
    pkill -f "python3 web_server.py"
    echo "✅ Server stopped"
fi
