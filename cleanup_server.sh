#!/bin/bash

# Run this script ON THE SERVER to clear old tunnels
# Usage: ssh bhaven@164.92.89.157 'bash -s' < cleanup_server.sh

echo "🧹 Cleaning up old SSH tunnels on server..."

# Kill any SSH processes listening on ports 8080-8090
for port in {8080..8090}; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process $PID on port $port"
        kill -9 $PID 2>/dev/null
    fi
done

echo "✅ Cleanup complete"

# Show what's listening
echo ""
echo "Current listening ports:"
netstat -tlnp 2>/dev/null | grep -E ":(808[0-9])" || echo "No ports 8080-8089 in use"
