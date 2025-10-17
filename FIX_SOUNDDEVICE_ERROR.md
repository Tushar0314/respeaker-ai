# Quick Fix for "No module named sounddevice" Error on Raspberry Pi

## The Problem
When you run `python3 hello_ai_rpi.py` and get:
```
ModuleNotFoundError: No module named 'sounddevice'
```

## The Solution (Run these commands on your Raspberry Pi)

### Step 1: Install System Dependencies FIRST
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 python3-dev build-essential
```

### Step 2: Install sounddevice
```bash
# If using virtual environment
source venv/bin/activate

# Install sounddevice
pip3 install sounddevice

# If that fails, try:
pip3 install sounddevice --no-cache-dir
```

### Step 3: Test It
```bash
python3 -c "import sounddevice as sd; print('Success!'); print(sd.query_devices())"
```

## Alternative: System-Wide Installation
If virtual environment installation fails:
```bash
# Exit virtual environment
deactivate

# Install system-wide
sudo pip3 install sounddevice

# Test
python3 -c "import sounddevice; print('Works!')"
```

## Complete Fresh Install (if nothing else works)

```bash
# 1. Remove old installations
pip3 uninstall sounddevice -y
sudo pip3 uninstall sounddevice -y

# 2. Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    python3-dev \
    python3-pip \
    build-essential

# 3. Verify portaudio
pkg-config --modversion portaudio-2.0

# 4. Install sounddevice
pip3 install --upgrade pip
pip3 install sounddevice --no-cache-dir

# 5. Test
python3 -c "import sounddevice; print('Installed successfully!')"
```

## Using the Automated Installer

The easiest way is to use the automated installer:
```bash
# Make the script executable
chmod +x install_rpi.sh

# Run it
bash install_rpi.sh
```

This will install everything automatically and verify all dependencies.

## Still Not Working?

Try installing all packages at once:
```bash
sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo pip3 install sounddevice
python3 hello_ai_rpi.py
```

## Checking What's Installed
```bash
# Check if portaudio is installed
pkg-config --list-all | grep portaudio

# Check Python packages
pip3 list | grep sounddevice

# Check system Python packages
apt list --installed | grep python3
```
