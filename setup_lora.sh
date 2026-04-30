#!/bin/bash
# LoRa Module Setup Script for Raspberry Pi 5
# This script sets up everything needed for LoRa communication

echo "======================================================================"
echo "   LoRa Module Setup for Raspberry Pi 5"
echo "======================================================================"
echo ""

# Update system
echo "[1/6] Updating system..."
sudo apt-get update -y

# Install espeak for text-to-speech
echo "[2/6] Installing espeak (text-to-speech)..."
sudo apt-get install -y espeak

# Install Python dependencies
echo "[3/6] Installing Python dependencies..."
pip install pyserial

# Enable UART
echo "[4/6] Configuring UART..."
echo "Please enable UART in raspi-config:"
echo "  1. Navigate to: Interface Options → Serial Port"
echo "  2. Login shell over serial: NO"
echo "  3. Serial port hardware: YES"
echo ""
read -p "Press Enter to open raspi-config, or Ctrl+C to skip..."
sudo raspi-config

# Add user to dialout group
echo "[5/6] Adding user to dialout group..."
sudo usermod -a -G dialout $USER

# Test components
echo "[6/6] Testing components..."

# Test espeak
echo "Testing espeak..."
espeak "Text to speech is working" 2>/dev/null && echo "✓ espeak OK" || echo "✗ espeak failed"

# Check serial ports
echo ""
echo "Available serial ports:"
ls /dev/tty* 2>/dev/null | grep -E "(ttyAMA|ttyUSB|ttyACM|serial)" || echo "No serial ports found"

echo ""
echo "======================================================================"
echo "   Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Connect your LoRa module to Pi5 GPIO or USB"
echo "  2. Reboot your Pi (required for UART and group changes)"
echo "  3. Test transmission: python3 lora_transmitter.py location"
echo "  4. Test receiver: python3 lora_receiver_tts.py test"
echo ""
echo "IMPORTANT: You must REBOOT for changes to take effect!"
echo ""
read -p "Reboot now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo reboot
fi
