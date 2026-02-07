#!/bin/bash

# Script to start SSH tunnel for a specific camera
# Usage: ./start_tunnel_multi.sh <camera_number>

if [ -z "$1" ]; then
    echo "Usage: ./start_tunnel_multi.sh <camera_number>"
    echo "Example: ./start_tunnel_multi.sh 1"
    exit 1
fi

CAMERA_NUM=$1
LOCAL_PORT=$((8080 + CAMERA_NUM))
REMOTE_PORT=$((8080 + CAMERA_NUM))

echo "🚀 Starting SSH Tunnel for Camera $CAMERA_NUM"
echo "   Local Port: $LOCAL_PORT"
echo "   Remote Port: $REMOTE_PORT"
echo ""

# Clean up old connections
pkill -f "ssh -R $REMOTE_PORT:localhost:$LOCAL_PORT"
sleep 2

# Start SSH tunnel
echo "📡 Connecting to server..."
echo "Look for: 'debug1: remote forward success for: listen $REMOTE_PORT'"
echo ""

ssh -R $REMOTE_PORT:localhost:$LOCAL_PORT \
    -N \
    -v \
    -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    bhaven@164.92.89.157
