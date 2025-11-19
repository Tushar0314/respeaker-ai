# 🚀 QUICK START - Raspberry Pi Voice Assistant

## Your Setup
```
┌─────────────────────────┐
│   Raspberry Pi 3/4      │
├─────────────────────────┤
│  ReSpeaker 4-Mic Array  │ ← Microphone (top of Pi)
│  (mounted on GPIO pins) │
├─────────────────────────┤
│  Audio Jack → JBL       │ ← Speaker output
│  (3.5mm or USB)         │
└─────────────────────────┘
```

---

## First Time Setup (Copy-Paste Commands)

### Terminal 1: Install Dependencies
```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required libraries
sudo apt-get install -y espeak portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 python3-pip python3-dev python3-venv ffmpeg alsa-utils build-essential

# Go to project folder
cd ~ && git clone https://github.com/Tushar0314/respeaker-ai.git
cd respeaker-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install vosk sounddevice google-generativeai

# Download speech model
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip
cd ..
```

---

## Running the Voice Assistant

### Terminal: Start Voice Assistant
```bash
cd ~/respeaker-ai
source venv/bin/activate
python3 hello_ai_pi_custom.py
```

### What You'll See
```
============================================================
🎤 Voice Assistant - Raspberry Pi + ReSpeaker 4-Mic Array
🔊 Output: JBL Speaker
============================================================

[STEP 1] Detecting ReSpeaker 4-Mic Array...
  [0] Built-in Audio
  [1] ReSpeaker 4-Mic Array

✓ Found ReSpeaker at device index: 1

[STEP 2] Connecting to Gemini AI...
  ✓ Using model: models/gemini-2.0-flash

[✓ SETUP COMPLETE]
  Microphone: ReSpeaker (device 1)
  Speaker: JBL (via Pi audio output)

[STARTUP TEST]
[SPEAKING] Voice assistant ready. Listening for commands.
[✓ Speech completed]

[READY] Say something to the ReSpeaker microphone...
       Press Ctrl+C to stop

============================================================
[LISTENING #1...]
============================================================
```

---

## How to Use

1. **Wait for** `[LISTENING]` prompt
2. **Speak clearly** into the ReSpeaker microphone (mounted on top of Pi)
3. **Wait** for your speech to be recognized
4. **Listen** as the AI responds through your JBL speaker
5. **Speak again** for next conversation
6. **Press Ctrl+C** to stop

---

## Example Conversations

```
You:  "What is the capital of France?"
AI:   "The capital of France is Paris..."

You:  "Tell me a joke"
AI:   "Why did the chicken cross the road?..."

You:  "What time is it?"
AI:   "I don't have access to real-time data..."
```

---

## Testing Components

### Test Microphone
```bash
# Record 3 seconds
arecord -D hw:1,0 -d 3 test.wav

# Play back
aplay test.wav
```

### Test Speaker
```bash
# Using espeak
espeak "Hello, this is a test"

# Or using speaker-test
speaker-test -c 2 -r 48000 -t wav
```

### Check Audio Devices
```bash
python test_respeaker_setup.py
```

---

## Quick Fixes

### ReSpeaker Not Detected?
```bash
# List all USB devices
lsusb | grep -i seeed

# List audio devices
arecord -l
aplay -l
```

### Can't Hear Speaker Output?
```bash
# Check volume
alsamixer

# Set default output
sudo nano /etc/asound.conf
```

### Microphone Not Working?
1. Check USB cable connection
2. Verify ReSpeaker LED indicator is on
3. Try different audio input device index

### Python Import Errors?
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify installations
pip list
```

---

## Performance Tips

- 🎯 **Speak clearly** - ReSpeaker works best with clear pronunciation
- 🎤 **Speak at normal volume** - No need to shout
- ⏱️ **Wait for response** - Gemini takes 1-2 seconds to respond
- 🔊 **Adjust speaker volume** - Use `alsamixer` to control JBL volume
- ⚙️ **Use USB speaker** - If 3.5mm jack audio is low, try USB JBL speaker

---

## Stop Running

Press `Ctrl+C` in the terminal where the script is running.

Output:
```
^C

============================================================
[SHUTTING DOWN]
============================================================
[SPEAKING] Voice assistant shutting down. Goodbye!
[✓ Speech completed]
Goodbye!
```

---

## Next Commands

```bash
# Stop voice assistant
Ctrl+C

# Deactivate Python environment
deactivate

# Run again next time
cd ~/respeaker-ai
source venv/bin/activate
python3 hello_ai_pi_custom.py
```

---

## Files You'll Use

```
respeaker-ai/
├── hello_ai_pi_custom.py          ← RUN THIS (main program)
├── test_respeaker_setup.py        ← Test your hardware
├── RASPBERRY_PI_SETUP_CUSTOM.md   ← Detailed guide
├── models/en/                     ← Speech recognition model
└── venv/                          ← Virtual environment
```

---

## Support

- 📖 **Detailed Guide**: `RASPBERRY_PI_SETUP_CUSTOM.md`
- 🧪 **Test Script**: `python test_respeaker_setup.py`
- 🔧 **Check Logs**: Look at console output for errors

---

**Good luck!** 🎉 Let me know if you have any issues! 🚀
