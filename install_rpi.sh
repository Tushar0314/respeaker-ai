#!/bin/bash
# Complete Installation Script for Raspberry Pi Voice Assistant
# This fixes ALL common issues including Python 3.13 compatibility
# Run with: bash install_rpi.sh

echo "=========================================="
echo "Raspberry Pi Voice Assistant Installer"
echo "=========================================="
echo ""

# Exit current venv if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivating current virtual environment..."
    deactivate 2>/dev/null || true
fi

echo "Step 1: Updating system..."
sudo apt-get update

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y \
    espeak \
    portaudio19-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    libffi-dev \
    python3-pip \
    python3-dev \
    python3-pyaudio \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    ffmpeg \
    alsa-utils \
    build-essential \
    git \
    unzip \
    wget

echo ""
echo "Step 3: Checking Python version..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
    echo "✓ Using Python 3.11 (recommended for compatibility)"
else
    PYTHON_CMD=python3
    echo "⚠ Using system Python $(python3 --version)"
fi

echo ""
echo "Step 4: Removing old virtual environment..."
rm -rf venv
echo "✓ Old venv removed"

echo ""
echo "Step 5: Creating fresh virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv
echo "✓ Virtual environment created"

echo ""
echo "Step 6: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 7: Upgrading pip..."
pip3 install --upgrade pip setuptools wheel

echo ""
echo "Step 8: Installing Python packages..."
echo "  - Installing cffi..."
pip3 install cffi

echo "  - Installing sounddevice..."
pip3 install sounddevice

echo "  - Installing vosk..."
pip3 install vosk

echo "  - Installing google-generativeai..."
pip3 install google-generativeai

echo "  - Installing pyttsx3..."
pip3 install pyttsx3

echo ""
echo "Step 9: Verifying installations..."
python3 << 'EOF'
import sys
errors = []

try:
    import vosk
    print("✓ vosk imported successfully")
except Exception as e:
    print(f"✗ vosk import failed: {e}")
    errors.append("vosk")

try:
    import sounddevice as sd
    print(f"✓ sounddevice imported successfully (version {sd.__version__})")
except Exception as e:
    print(f"✗ sounddevice import failed: {e}")
    errors.append("sounddevice")

try:
    import google.generativeai as genai
    print("✓ google-generativeai imported successfully")
except Exception as e:
    print(f"✗ google-generativeai import failed: {e}")
    errors.append("google-generativeai")

try:
    import pyttsx3
    print("✓ pyttsx3 imported successfully")
except Exception as e:
    print(f"✗ pyttsx3 import failed: {e}")
    errors.append("pyttsx3")

if errors:
    print(f"\n⚠ Some packages failed to import: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All packages imported successfully!")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Package verification failed!"
    echo "Check errors above for details."
    exit 1
fi

echo ""
echo "Step 10: Checking for Vosk model..."
if [ ! -d "models/en" ]; then
    echo "Vosk model not found. Downloading..."
    mkdir -p models
    cd models
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    mv vosk-model-small-en-us-0.15 en
    rm vosk-model-small-en-us-0.15.zip
    cd ..
    echo "✓ Vosk model downloaded"
else
    echo "✓ Vosk model already exists"
fi

echo ""
echo "Step 11: Testing audio devices..."
python3 << 'EOF'
import sounddevice as sd
print("\nAvailable audio devices:")
devices = sd.query_devices()
for idx, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"  Input {idx}: {device['name']}")
EOF

echo ""
echo "Step 12: Testing espeak..."
espeak "Installation complete" 2>/dev/null || echo "⚠ espeak test skipped"

echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "To run the voice assistant:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the script:"
echo "     python3 hello_ai_rpi.py"
echo ""
echo "The script is now ready to use!"
echo ""
