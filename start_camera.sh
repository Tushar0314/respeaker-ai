#!/bin/bash

# Script to start a specific camera stream
# Usage: ./start_camera.sh <camera_number>

if [ -z "$1" ]; then
    echo "Usage: ./start_camera.sh <camera_number>"
    echo "Example: ./start_camera.sh 1"
    exit 1
fi

CAMERA_NUM=$1
PORT=$((8080 + CAMERA_NUM))

echo "🎥 Starting Camera $CAMERA_NUM"
echo "📡 Port: $PORT"
echo "🌐 URL: http://echo.cooperativepaddling.com/live$CAMERA_NUM"
echo ""

python camera_stream_multi.py --camera $CAMERA_NUM --port $PORT
