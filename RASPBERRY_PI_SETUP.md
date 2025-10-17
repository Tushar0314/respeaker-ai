# Raspberry Pi 3 Setup Guide for Voice Assistant

## Hardware Requirements
- Raspberry Pi 3 (32-bit OS)
- ReSpeaker 2-Mic or 4-Mic USB Array
- Speaker/Headphones connected to Pi

## Software Installation

### 1. System Dependencies (IMPORTANT - Install these FIRST!)
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install audio and build tools (REQUIRED for sounddevice)
sudo apt-get install -y \
    espeak \
    portaudio19-dev \
    python3-pip \
    python3-dev \
    python3-pyaudio \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    alsa-utils \
    build-essential

# Verify portaudio is installed
pkg-config --modversion portaudio-2.0
```

### 2. Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Upgrade pip first
pip3 install --upgrade pip setuptools wheel

# Install Python packages one by one to see any errors
pip3 install vosk
pip3 install sounddevice
pip3 install google-generativeai
pip3 install pyttsx3

# Or install all at once
pip3 install -r requirements_rpi.txt

# Verify sounddevice installation
python3 -c "import sounddevice as sd; print('sounddevice version:', sd.__version__); print(sd.query_devices())"
```

### 3. Download Vosk Model
```bash
# Download small English model (lighter for Raspberry Pi 3)
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip
```

## ReSpeaker Configuration

### Check Audio Devices
```bash
# List audio devices
arecord -l

# Test recording
arecord -D hw:1,0 -f S16_LE -r 16000 -d 3 test.wav
aplay test.wav
```

### Configure ReSpeaker (if needed)
```bash
# For ReSpeaker 2-Mic or 4-Mic Array
# Install drivers if not already installed
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
sudo ./install.sh
sudo reboot
```

## Running the Voice Assistant

### 1. Basic Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python3 hello_ai_rpi.py
```

### 2. Auto-start on Boot (Optional)
Create systemd service:
```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

Add content:
```ini
[Unit]
Description=Voice Assistant with Gemini AI
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RESpeacker
ExecStart=/home/pi/RESpeacker/venv/bin/python3 /home/pi/RESpeacker/hello_ai_rpi.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service
sudo systemctl status voice-assistant.service
```

## Troubleshooting

### "No module named sounddevice" Error
This is the most common error. Fix it by:

```bash
# 1. Install system dependencies FIRST
sudo apt-get install -y portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0

# 2. If in virtual environment, activate it
source venv/bin/activate

# 3. Reinstall sounddevice
pip3 uninstall sounddevice -y
pip3 install sounddevice --no-cache-dir

# 4. Test it
python3 -c "import sounddevice; print('Success!')"
```

If still failing:
```bash
# Try installing system-wide (outside venv)
deactivate  # Exit virtual environment
sudo pip3 install sounddevice
python3 -c "import sounddevice; print('Success!')"
```

### "No module named _portaudio" Error
```bash
# Install portaudio development files
sudo apt-get install -y portaudio19-dev python3-pyaudio

# Reinstall sounddevice
pip3 install --force-reinstall sounddevice
```

### No Audio Output
```bash
# Check volume
alsamixer

# Test speaker
speaker-test -t wav -c 2

# Check espeak
espeak "Hello from Raspberry Pi"
```

### Microphone Not Working
```bash
# List devices
arecord -l

# Test specific device
arecord -D hw:1,0 -f S16_LE -r 16000 -d 3 test.wav

# Adjust microphone gain
alsamixer
# Press F4 for capture, adjust levels
```

### ReSpeaker Not Detected
```bash
# Check USB connection
lsusb

# Reinstall drivers
cd ~/seeed-voicecard
git pull
sudo ./install.sh
sudo reboot
```

### Performance Issues (Raspberry Pi 3)
- Use smaller Vosk model (vosk-model-small-en-us-0.15)
- Reduce sample rate to 16000 Hz
- Use gemini-2.0-flash model (fastest)
- Consider overclocking Pi 3 (add to /boot/config.txt):
  ```
  over_voltage=2
  arm_freq=1300
  ```

## Key Differences from Windows Version

1. **TTS Engine**: Uses `espeak` instead of Windows SAPI
   - Lighter and faster on Raspberry Pi
   - No additional libraries needed

2. **Audio Settings**: 
   - Sample rate: 16000 Hz (optimal for ReSpeaker)
   - Channels: 1 (mono)
   - Auto-detects ReSpeaker device

3. **Performance**: 
   - Uses lighter Vosk model
   - Prefers gemini-flash models
   - Optimized for 32-bit ARM

4. **No GUI Required**: Runs headless via SSH

## Notes
- First run may be slower as Python compiles packages
- Keep Raspberry Pi connected to stable power supply
- Use heat sink on Pi 3 for better performance
- Consider using USB sound card if onboard audio has issues
