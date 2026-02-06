#!/bin/bash
# Camera Streaming Setup Script for Raspberry Pi 5
# Quick setup for Camera Module 3 streaming

echo "======================================================================"
echo "📷 RASPBERRY PI CAMERA STREAMING - SETUP SCRIPT"
echo "======================================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   This script is designed for Raspberry Pi 5"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Updating system..."
echo "-------------------------------------------------------------------"
sudo apt update

echo ""
echo "Step 2: Installing camera libraries..."
echo "-------------------------------------------------------------------"
sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps

echo ""
echo "Step 3: Installing Python packages..."
echo "-------------------------------------------------------------------"
pip3 install requests flask --break-system-packages 2>/dev/null || pip3 install requests flask

echo ""
echo "Step 4: Testing camera..."
echo "-------------------------------------------------------------------"
if command -v libcamera-hello &> /dev/null; then
    echo "✓ libcamera is installed"
    echo "  Testing camera (5 seconds)..."
    timeout 5 libcamera-hello 2>/dev/null && echo "✓ Camera is working!" || echo "⚠️  Camera test failed"
else
    echo "⚠️  libcamera-hello not found"
fi

echo ""
echo "Step 5: Checking camera status..."
echo "-------------------------------------------------------------------"
if vcgencmd get_camera | grep -q "detected=1"; then
    echo "✓ Camera detected!"
else
    echo "⚠️  Camera not detected"
    echo ""
    echo "To enable camera:"
    echo "  1. Run: sudo raspi-config"
    echo "  2. Go to: Interface Options → Camera"
    echo "  3. Enable camera"
    echo "  4. Reboot: sudo reboot"
fi

echo ""
echo "Step 6: Network information..."
echo "-------------------------------------------------------------------"
LOCAL_IP=$(hostname -I | awk '{print $1}')
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo "Local IP:  $LOCAL_IP"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "Your stream will be available at:"
echo "  http://$LOCAL_IP:8080/"

echo ""
echo "Step 7: Firewall configuration..."
echo "-------------------------------------------------------------------"
if command -v ufw &> /dev/null; then
    sudo ufw allow 8080 2>/dev/null && echo "✓ Port 8080 opened" || echo "⚠️  Firewall not configured"
else
    echo "ℹ️  UFW firewall not installed (usually not needed)"
fi

echo ""
echo "======================================================================"
echo "✅ SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. Test the camera:"
echo "   python3 camera_stream.py"
echo "   (Choose option 2: Test Camera)"
echo ""
echo "2. Start streaming:"
echo "   python3 camera_stream.py"
echo "   (Choose option 1: Start HTTP Stream)"
echo ""
echo "3. View stream in browser:"
echo "   http://$LOCAL_IP:8080/"
echo ""
echo "📱 Mobile devices on same WiFi can access:"
echo "   http://$LOCAL_IP:8080/"
echo ""
echo "🌐 For internet access:"
echo "   - Forward port 8080 on your router"
echo "   - Access via: http://$PUBLIC_IP:8080/"
echo ""
echo "📖 Full documentation: CAMERA_SETUP_GUIDE.md"
echo ""
echo "======================================================================"

# Offer to run test
echo ""
read -p "Would you like to test the camera now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running camera test..."
    python3 camera_stream.py
fi
