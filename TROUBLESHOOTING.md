# 🆘 Troubleshooting Guide - Raspberry Pi Voice Assistant

## Quick Diagnostics

### Is It Even Running?
```bash
# Check if Python script is running
ps aux | grep hello_ai_pi_custom.py

# Kill if stuck
pkill -f hello_ai_pi_custom.py

# Check Python error
python3 hello_ai_pi_custom.py 2>&1 | head -20
```

---

## Common Problems & Fixes

### 1️⃣ "ModuleNotFoundError: No module named 'vosk'"

**Cause:** Virtual environment not activated or packages not installed

**Fix:**
```bash
# Make sure you're in the right folder
cd ~/respeaker-ai

# Activate virtual environment
source venv/bin/activate

# Verify prompt shows (venv)
# Should look like: (venv) pi@raspberrypi:~/respeaker-ai $

# Reinstall if needed
pip install vosk sounddevice google-generativeai

# Test import
python -c "import vosk; print('✓ vosk OK')"
```

---

### 2️⃣ "ReSpeaker not auto-detected"

**Cause:** ReSpeaker not connected or wrong device index

**Fix:**
```bash
# Check ReSpeaker USB connection
lsusb | grep -i seeed
# Should show: Seeed Studio ReSpeaker or similar

# List all audio devices
arecord -l

# Look for ReSpeaker in the list
# Usually shows as "USB Audio Device" with 4 channels

# When script asks, enter the device index number
# Example: 1 for [1] USB Audio Device
```

---

### 3️⃣ Can't Hear Speaker Output

**Cause:** Wrong audio output selected, volume too low, JBL not connected

**Fix:**
```bash
# Check current volume
alsamixer
# Use arrow keys: UP to increase, ESC to exit

# List audio outputs
aplay -l

# Test speaker directly
espeak "Testing speaker output"

# Test with different output device
aplay -D hw:0,0 test.wav    # Try device 0
aplay -D hw:1,0 test.wav    # Try device 1
aplay -D hw:2,0 test.wav    # Try device 2

# Set default output
sudo nano /etc/asound.conf
```

Example `/etc/asound.conf` for JBL on device 2:
```
defaults.ctl.card 2
defaults.pcm.card 2
```

---

### 4️⃣ Microphone Not Picking Up Sound

**Cause:** ReSpeaker not connected, wrong device, microphone level too low

**Fix:**
```bash
# Verify ReSpeaker is connected
lsusb | grep -i seeed

# Check if it's in audio devices
arecord -l

# Record test audio (15 seconds)
arecord -D hw:1,0 -f S16_LE -r 16000 -d 15 test.wav

# Play it back
aplay test.wav

# If no sound, try these:

# 1. Check microphone levels
alsamixer
# Find ReSpeaker and check input levels (should show bars)

# 2. Test with different device index
arecord -D hw:2,0 -d 3 test2.wav

# 3. Check ReSpeaker LED
# The LED on ReSpeaker should be solid or blinking
# If dark, check USB power connection
```

---

### 5️⃣ "Gemini Error" or "No suitable model found"

**Cause:** API key invalid, API quota exceeded, no internet

**Fix:**
```bash
# Test API key
python << 'EOF'
import google.generativeai as genai
API_KEY = 'YOUR_API_KEY_HERE'
genai.configure(api_key=API_KEY)

try:
    models = list(genai.list_models())
    print(f"✓ API works! Found {len(models)} models")
    for m in models[:5]:
        print(f"  - {m.name}")
except Exception as e:
    print(f"✗ API Error: {e}")
EOF

# Check internet connection
ping google.com

# Verify API key
# 1. Go to https://aistudio.google.com
# 2. Click "Get API Key"
# 3. Copy your key
# 4. Replace in hello_ai_pi_custom.py
```

---

### 6️⃣ "Vosk model not found"

**Cause:** Model not downloaded or in wrong location

**Fix:**
```bash
# Check if model exists
ls -la models/en/

# Should show: am, conf, graph, ivector, etc.

# If empty or missing:
cd models
rm -rf vosk-model-* en  # Clean up

# Download fresh
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip

# Verify
ls en/
```

---

### 7️⃣ Script Runs Slowly or Freezes

**Cause:** Raspberry Pi low on memory, heavy Gemini model, network latency

**Fix:**
```bash
# Check system resources
free -h
df -h
top

# If memory low:
# 1. Close other applications
# 2. Restart: sudo reboot

# Switch to faster Gemini model in hello_ai_pi_custom.py:
preferred_models = [
    'models/gemini-2.5-flash',    # Fastest
    'models/gemini-2.0-flash',
]

# Check network speed
ping -c 5 google.com
```

---

### 8️⃣ "Externally-managed-environment" Error

**Cause:** Using pip outside virtual environment with system Python

**Fix:**
```bash
# Always activate virtual environment FIRST
source ~/respeaker-ai/venv/bin/activate

# Should see (venv) in prompt
# Now pip install works

# Never use sudo with pip inside venv
# ❌ WRONG: sudo pip install vosk
# ✓ RIGHT: pip install vosk
```

---

### 9️⃣ "portaudio not found" during Installation

**Cause:** portaudio19-dev not installed before sounddevice

**Fix:**
```bash
# Install system dependency FIRST
sudo apt-get install -y portaudio19-dev

# Verify
pkg-config --modversion portaudio-2.0

# Then install sounddevice
pip install sounddevice

# If still failing, reinstall everything
pip uninstall sounddevice -y
pip install sounddevice --force-reinstall --no-cache-dir
```

---

### 🔟 Python Script Crashes Randomly

**Cause:** Out of memory, timeout, network drop

**Fix:**
```bash
# Run with error output saved
python3 hello_ai_pi_custom.py 2>&1 | tee run.log

# Check the log file for errors
cat run.log

# Increase timeout for Gemini in code:
response = model.generate_content(prompt, stream=False, timeout=30)

# Add restart loop in bash:
while true; do
    python3 hello_ai_pi_custom.py
    echo "Restarting in 5 seconds..."
    sleep 5
done
```

---

## Advanced Debugging

### Enable Verbose Output
```bash
# Edit hello_ai_pi_custom.py
# Add at top:
import logging
logging.basicConfig(level=logging.DEBUG)

# Run again
python3 hello_ai_pi_custom.py
```

### Test Each Component Individually

**Test 1: Microphone Only**
```bash
python << 'EOF'
import sounddevice as sd
import numpy as np

print("Recording 5 seconds...")
audio = sd.rec(int(5 * 16000), samplerate=16000, channels=1, device=1)
sd.wait()
print(f"Average level: {np.abs(audio).mean()}")
print(f"Peak level: {np.abs(audio).max()}")
EOF
```

**Test 2: Vosk Only**
```bash
python << 'EOF'
from vosk import Model, KaldiRecognizer
model = Model("models/en")
print("✓ Vosk model loaded successfully")
EOF
```

**Test 3: Gemini Only**
```bash
python << 'EOF'
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('models/gemini-2.0-flash')
response = model.generate_content("Say hello")
print(response.text)
EOF
```

**Test 4: Speaker Only**
```bash
espeak "Testing speaker"
# OR
speaker-test -c 2 -r 48000 -t wav
```

---

## System Health Check

```bash
#!/bin/bash
echo "=== Raspberry Pi Health Check ==="

echo "1. Disk Space:"
df -h | grep -E "Size|dev/root"

echo -e "\n2. Memory:"
free -h | grep Mem

echo -e "\n3. CPU Temperature:"
vcgencmd measure_temp

echo -e "\n4. Network:"
ping -c 1 google.com && echo "✓ Internet OK" || echo "✗ No internet"

echo -e "\n5. ReSpeaker:"
lsusb | grep -i seeed && echo "✓ ReSpeaker detected" || echo "✗ ReSpeaker not found"

echo -e "\n6. Audio Devices:"
arecord -l | grep -i usb

echo -e "\n7. Python:"
python3 --version

echo -e "\n8. Required Packages:"
python3 -c "import sounddevice; import vosk; import google.generativeai; print('✓ All packages OK')" 2>&1

echo -e "\n=== End of Check ==="
```

Save as `health_check.sh`:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

## Restart Everything

If all else fails:
```bash
# Kill the script
pkill -f hello_ai_pi_custom.py

# Deactivate environment
deactivate

# Reboot Raspberry Pi
sudo reboot

# After reboot, log back in and start fresh:
ssh pi@raspberrypi.local
cd ~/respeaker-ai
source venv/bin/activate
python3 hello_ai_pi_custom.py
```

---

## When to Get Help

Share these details:
```bash
# Generate diagnostic report
echo "=== Diagnostic Report ===" > diag.txt
echo "Hostname: $(hostname)" >> diag.txt
echo "Python: $(python3 --version)" >> diag.txt
echo "ReSpeaker:" >> diag.txt
lsusb >> diag.txt
echo "Audio Devices:" >> diag.txt
arecord -l >> diag.txt
echo "Installed Packages:" >> diag.txt
pip list >> diag.txt
echo "Error Output:" >> diag.txt
python3 hello_ai_pi_custom.py 2>&1 | head -50 >> diag.txt

# View report
cat diag.txt
```

Include the output of `diag.txt` when asking for help!

---

## Quick Reference Links

- **Vosk Models:** https://alphacephei.com/vosk/models
- **ReSpeaker Docs:** https://wiki.seeedstudio.com/ReSpeaker_4-Mic_Array_for_Raspberry_Pi/
- **Gemini API:** https://aistudio.google.com
- **Raspberry Pi:** https://www.raspberrypi.org

---

**Still stuck?** Try these:
1. ✓ Run `python test_respeaker_setup.py` first
2. ✓ Check `/QUICK_START.md` for basic setup
3. ✓ Review `/RASPBERRY_PI_SETUP_CUSTOM.md` step-by-step
4. ✓ Run health check script above
5. ✓ Create diagnostic report and analyze error messages

Good luck! 🍀
