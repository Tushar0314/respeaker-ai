#!/bin/bash

# Script to test SSH tunnel connectivity
# Run this on the Raspberry Pi

echo "🔍 Testing SSH Tunnel Setup..."
echo ""

# Test 1: Check if SSH tunnel process is running
echo "1️⃣ Checking for active SSH tunnel process..."
if pgrep -f "ssh -R 8080:localhost:8080" > /dev/null; then
    echo "✅ SSH tunnel process is running"
else
    echo "❌ SSH tunnel process NOT found"
    echo "   Run: ssh -R 8080:localhost:8080 root@echo.cooperativepaddling.com -N -v"
fi
echo ""

# Test 2: Check if camera stream is running locally
echo "2️⃣ Checking if camera stream is available locally..."
if curl -s -I http://localhost:8080/stream | grep -q "200 OK"; then
    echo "✅ Camera stream is running on localhost:8080"
elif curl -s -I http://localhost:8080/ | grep -q "200 OK"; then
    echo "⚠️  Server running but /stream endpoint not found"
    echo "   Make sure you selected option 1 (Start Streaming Server)"
else
    echo "❌ No server running on localhost:8080"
    echo "   Run: python camera_stream.py and select option 1"
fi
echo ""

# Test 3: Check network connectivity to server
echo "3️⃣ Testing connection to remote server..."
if ping -c 1 echo.cooperativepaddling.com > /dev/null 2>&1; then
    echo "✅ Can reach echo.cooperativepaddling.com"
else
    echo "❌ Cannot reach echo.cooperativepaddling.com"
    echo "   Check your internet connection"
fi
echo ""

echo "📋 Summary:"
echo "If all tests pass, try these on the server:"
echo "1. SSH to server: ssh bhaven@echo.cooperativepaddling.com"
echo "2. Test tunnel: curl -I http://localhost:8080/stream"
echo "3. Restart nginx: sudo systemctl restart nginx"
