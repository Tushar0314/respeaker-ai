# 🎤 Voice Assistant Setup Guide - Raspberry Pi + ReSpeaker 4-Mic Array + JBL Speaker

## Your Hardware Setup
- ✓ Raspberry Pi (connected to PC)
- ✓ ReSpeaker 4-Mic Array (mounted on top of Pi)
- ✓ JBL Speaker (connected to Pi's audio jack or USB)
- ✓ Gemini API Key

---

## Step 1: Initial Setup on Raspberry Pi

### 1.1 Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.2 Install Required System Dependencies
```bash
# Audio libraries (MUST install before Python packages)
sudo apt-get install -y \
    espeak \
    portaudio19-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    alsa-utils \
    build-essential \
    python3-pip \
    python3-dev \
    python3-venv

# Verify portaudio installation
pkg-config --modversion portaudio-2.0
```

### 1.3 Configure Audio Output for JBL Speaker
```bash
# List sound cards
aplay -l

# Set default ALSA output (if needed)
sudo nano /etc/asound.conf
```

If your JBL speaker appears as a separate device, set it as default in `/etc/asound.conf`:
```
defaults.ctl.card 1
defaults.pcm.card 1
```

Then test:
```bash
speaker-test -c 2 -r 48000 -t wav
```

---

## Step 2: Download Project and Setup Virtual Environment

### 2.1 Clone or Navigate to Project
```bash
cd ~/
git clone https://github.com/Tushar0314/respeaker-ai.git
cd respeaker-ai
```

### 2.2 Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Upgrade pip
```bash
pip install --upgrade pip setuptools wheel
```

### 2.4 Install Python Dependencies
```bash
# Install packages one by one to see any errors
pip install vosk
pip install sounddevice
pip install google-generativeai

# Optional: numpy for better audio processing
pip install numpy

# Verify installation
python -c "import sounddevice; import vosk; print('✓ Dependencies OK')"
```

---

## Step 3: Vosk Model Setup

### 3.1 Download Speech Recognition Model
```bash
cd models

# Download small model (optimized for Raspberry Pi 3)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Extract and organize
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip

cd ..
ls models/en/  # Should show: am, conf, graph, ivector, model files
```

---

## Step 4: Test ReSpeaker Setup

### 4.1 Test Audio Devices
```bash
# List all audio devices
python test_respeaker_setup.py
```

This will show:
- All connected microphones and speakers
- Detect ReSpeaker automatically
- Test microphone recording
- Test speaker output

### 4.2 Manual Audio Device Check (if needed)
```bash
# List input devices
arecord -l

# Test recording from ReSpeaker (example: device hw:1,0)
arecord -D hw:1,0 -f S16_LE -r 16000 -d 3 test.wav

# Test playback on JBL speaker
aplay -D hw:0,0 test.wav
```

---

## Step 5: Configure Gemini API Key

Edit `hello_ai_pi_custom.py` and replace the API key:

```bash
nano hello_ai_pi_custom.py
```

Find this line:
```python
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
```

Replace with your actual API key:
```python
GEMINI_API_KEY = 'your-api-key-here'
```

Save with `Ctrl+X`, then `Y`, then `Enter`

---

## Step 6: Run the Voice Assistant

### 6.1 Quick Start
```bash
source venv/bin/activate
python3 hello_ai_pi_custom.py
```

### 6.2 What to Expect
```
============================================================
🎤 Voice Assistant - Raspberry Pi + ReSpeaker 4-Mic Array
🔊 Output: JBL Speaker
============================================================

[STEP 1] Detecting ReSpeaker 4-Mic Array...
[STEP 2] Connecting to Gemini AI...
[SETUP COMPLETE]
  Microphone: ReSpeaker (device X)
  Sample Rate: 16000 Hz
  AI Model: gemini-2.0-flash
  Speaker: JBL (via Pi audio output)
============================================================

[READY] Say something to the ReSpeaker microphone...
       Press Ctrl+C to stop
```

Now speak into the ReSpeaker!

### 6.3 Troubleshooting

**Problem: "ReSpeaker not auto-detected"**
- Check USB connection: `lsusb | grep -i seeed`
- Run `test_respeaker_setup.py` to find the device index
- When prompted, enter the correct device number

**Problem: Can't hear speaker output**
- Test speaker separately: `speaker-test -c 2 -r 48000 -t wav`
- Check volume: `alsamixer`
- Verify JBL is connected to the correct audio output

**Problem: Microphone not picking up sound**
- Check ReSpeaker orientation (USB port should face away)
- Run audio test: `arecord -D hw:1,0 -f S16_LE -r 16000 -d 3 test.wav`
- Play it back: `aplay test.wav`

**Problem: "Import vosk failed"**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall: `pip install vosk --force-reinstall`

---

## Step 7: Advanced Configuration (Optional)

### 7.1 Auto-start on Boot
Create systemd service:
```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

Paste:
```ini
[Unit]
Description=Voice Assistant
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/respeaker-ai
Environment="PATH=/home/pi/respeaker-ai/venv/bin"
ExecStart=/home/pi/respeaker-ai/venv/bin/python3 hello_ai_pi_custom.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant
```

### 7.2 Adjust Microphone Sensitivity
Edit `hello_ai_pi_custom.py`, modify:
```python
# Increase listening duration for longer sentences
recognized_text = listen_once(mic_index, RESPEAKER_RATE, seconds=7.0)

# Adjust audio chunk size for better quality
RESPEAKER_CHUNK = 2048  # Larger = more accurate
```

### 7.3 Faster Response Time
Change the Gemini model to a lighter one:
```python
preferred_models = [
    'models/gemini-2.5-flash',  # Faster
    'models/gemini-2.0-flash',
]
```

---

## Reference Commands

```bash
# Activate environment
source ~/respeaker-ai/venv/bin/activate

# Run voice assistant
cd ~/respeaker-ai
python3 hello_ai_pi_custom.py

# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -D hw:1,0 -d 3 test.wav && aplay test.wav

# Test speaker
espeak "Hello from voice assistant"

# Check logs
journalctl -u voice-assistant -f

# Stop auto-start
sudo systemctl stop voice-assistant
sudo systemctl disable voice-assistant
```

---

## Support & Debugging

If something doesn't work:

1. **Run the test script first:**
   ```bash
   python test_respeaker_setup.py
   ```

2. **Check Python packages:**
   ```bash
   pip list | grep -E "vosk|sounddevice|google"
   ```

3. **Test each component separately:**
   - Microphone: `test_respeaker_setup.py`
   - Speaker: `espeak "Test"`
   - API: `python -c "import google.generativeai; print('OK')"`

4. **View detailed errors:**
   ```bash
   python3 hello_ai_pi_custom.py 2>&1 | tee run.log
   ```

---

## 🎉 Success Indicators

When working correctly, you should see:
- ✓ ReSpeaker detected at device index X
- ✓ Gemini model loaded
- ✓ "Voice assistant ready" message spoken
- ✓ [LISTENING] prompt appears
- ✓ Your speech recognized as text
- ✓ AI response spoken through JBL speaker

**Enjoy your voice assistant!** 🎤🤖🔊
