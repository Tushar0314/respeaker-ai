#!/bin/bash
# EMERGENCY FIX for Python 3.13 Vosk compatibility issue
# This script forces Python 3.11 or uses a workaround

echo "=========================================="
echo "Emergency Vosk Fix for Raspberry Pi"
echo "=========================================="
echo ""

# Exit any venv
deactivate 2>/dev/null || true

cd ~/respeaker-ai

echo "Checking Python versions..."
python3 --version
python3.11 --version 2>/dev/null || echo "Python 3.11 not found"

# Check if Python 3.11 is available
if command -v python3.11 &> /dev/null; then
    echo ""
    echo "✓ Python 3.11 found! Creating venv with Python 3.11..."
    rm -rf venv
    python3.11 -m venv venv
    source venv/bin/activate
    
    pip3 install --upgrade pip
    pip3 install cffi sounddevice vosk google-generativeai pyttsx3
    
    echo ""
    echo "Testing with Python 3.11..."
    python3 --version
    python3 -c "import vosk; print('✓ Vosk works with Python 3.11!')"
    
else
    echo ""
    echo "⚠ Python 3.11 not available. Trying workaround..."
    
    # Try to install Python 3.11
    echo "Installing Python 3.11..."
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    
    if command -v python3.11 &> /dev/null; then
        echo "✓ Python 3.11 installed!"
        rm -rf venv
        python3.11 -m venv venv
        source venv/bin/activate
        pip3 install --upgrade pip
        pip3 install cffi sounddevice vosk google-generativeai pyttsx3
    else
        echo ""
        echo "✗ Cannot install Python 3.11. Using system-wide installation instead..."
        rm -rf venv
        
        # Install packages system-wide with --break-system-packages
        sudo pip3 install --break-system-packages cffi
        sudo pip3 install --break-system-packages sounddevice
        sudo pip3 install --break-system-packages vosk
        sudo pip3 install --break-system-packages google-generativeai
        sudo pip3 install --break-system-packages pyttsx3
        
        echo ""
        echo "✓ Packages installed system-wide"
        echo "Run: python3 hello_ai_rpi.py (without venv)"
        exit 0
    fi
fi

echo ""
echo "=========================================="
echo "✓ Fix Complete!"
echo "=========================================="
echo ""
echo "Now run:"
echo "  source venv/bin/activate"
echo "  python3 hello_ai_rpi.py"
echo ""
