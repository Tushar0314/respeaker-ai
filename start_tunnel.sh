#!/bin/bash

# Improved SSH Tunnel Startup Script
# This creates a more reliable SSH tunnel with auto-reconnect

echo "🚀 Starting SSH Tunnel to echo.cooperativepaddling.com..."
echo ""

# Kill any existing SSH tunnel
echo "Cleaning up old connections..."
pkill -f "ssh -R 8080:localhost:8080"
sleep 2

# Check if camera stream is running
if ! curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "⚠️  WARNING: Camera stream doesn't seem to be running on localhost:8080"
    echo "   Start it first with: python camera_stream.py (option 1)"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📡 Establishing tunnel with the following options:"
echo "   -R 8080:localhost:8080  (forward remote port 8080 to local 8080)"
echo "   -N                      (no remote command)"
echo "   -v                      (verbose for debugging)"
echo "   -o ServerAliveInterval=60  (keep connection alive)"
echo "   -o ServerAliveCountMax=3   (reconnect if no response)"
echo ""
echo "Look for this message: 'debug1: remote forward success for: listen 8080'"
echo ""

# Start SSH tunnel with keepalive options
ssh -R 8080:localhost:8080 \
    -N \
    -v \
    -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    bhaven@echo.cooperativepaddling.com
