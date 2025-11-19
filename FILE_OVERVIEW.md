# 📚 Complete File Overview - Voice Assistant for Raspberry Pi

## Your Complete Setup Package

This repository now contains everything you need to run a voice assistant on your Raspberry Pi with ReSpeaker 4-Mic Array and JBL speaker.

---

## 📁 Files Included

### Main Program
```
hello_ai_pi_custom.py ⭐
└─ The MAIN program you'll run
└─ Optimized for ReSpeaker 4-Mic Array
└─ Auto-detects microphone and speaker
└─ Uses Gemini AI for responses
└─ Run with: python3 hello_ai_pi_custom.py
```

### Original Programs (Reference)
```
hello_ai.py
└─ Original version (for regular computers)
└─ Uses pyttsx3 for text-to-speech
└─ Uses sounddevice for audio I/O

hello_ai_rpi.py
└─ Generic Raspberry Pi version
└─ Uses espeak for TTS
└─ Falls back to pyttsx3

hello_ai_rpi_alternative.py
└─ Alternative implementation
└─ Different approach to audio handling
```

### Testing & Diagnostics
```
test_respeaker_setup.py ⭐
└─ Tests your ReSpeaker and speaker setup
└─ Detects audio devices automatically
└─ Tests microphone recording
└─ Tests speaker output
└─ Run BEFORE running main program
└─ Command: python test_respeaker_setup.py

test_tts.py
└─ Tests text-to-speech functionality
└─ Verifies pyttsx3 is working

test_tts_improved.py
└─ Enhanced TTS testing
└─ Tries different voices
└─ Checks audio output device
```

### Documentation
```
QUICK_START.md ⭐⭐⭐
└─ START HERE!
└─ Fastest way to get running
└─ Copy-paste commands
└─ Quick troubleshooting
└─ Example conversations

RASPBERRY_PI_SETUP_CUSTOM.md ⭐⭐
└─ Complete detailed setup guide
└─ Step-by-step instructions
└─ Hardware configuration
└─ ReSpeaker setup
└─ Audio output configuration
└─ Troubleshooting section

SETUP_CHECKLIST.md ⭐⭐
└─ Track your progress
└─ Verify each step completed
└─ Hardware verification
└─ Software installation checklist
└─ Testing checklist

TROUBLESHOOTING.md ⭐⭐
└─ Fix common problems
└─ Advanced debugging
└─ Component testing
└─ Health check scripts
└─ Diagnostic procedures

RASPBERRY_PI_SETUP.md
└─ Generic Raspberry Pi setup guide
└─ Original documentation
└─ Reference material

ALTERNATIVE_SOLUTION.txt
SIMPLE_FIX.txt
FIX_SOUNDDEVICE_ERROR.md
INSTALL_COMMANDS.txt
└─ Various fixes and guides
└─ Useful troubleshooting resources
```

### Model & Data
```
models/
├─ en/
│  ├─ am/          (acoustic model)
│  ├─ conf/        (configuration)
│  ├─ graph/       (speech graph)
│  └─ ivector/     (i-vector extractor)
└─ vosk-model-small-en-us-0.15.zip
   └─ Downloaded model file (can delete after extraction)
```

### Virtual Environment
```
venv/
└─ Python virtual environment
└─ Contains all installed packages
└─ Created by: python3 -m venv venv
└─ Activated by: source venv/bin/activate
```

### Scripts
```
install_rpi.sh ⭐
└─ Automated installer for Raspberry Pi
└─ Installs all dependencies
└─ Can run instead of manual steps
└─ Command: bash install_rpi.sh

emergency_fix.sh
└─ Emergency fix script
└─ Resolves common issues
```

### Git Files
```
.git/
└─ Git repository metadata

.gitignore
└─ Files to ignore in version control
```

---

## 🚀 Quick Start Path

### Day 1: First Time Setup
1. **Read:** `QUICK_START.md` (5 minutes)
2. **Copy-Paste:** Commands from section "First Time Setup"
3. **Wait:** ~30 minutes for installations
4. **Run:** `python3 hello_ai_pi_custom.py`

### Day 2+: Regular Use
1. **SSH:** `ssh pi@raspberrypi.local`
2. **Navigate:** `cd ~/respeaker-ai`
3. **Activate:** `source venv/bin/activate`
4. **Run:** `python3 hello_ai_pi_custom.py`

---

## 📖 Documentation Reading Order

**If you're new:**
1. `QUICK_START.md` ← Start here!
2. `RASPBERRY_PI_SETUP_CUSTOM.md` ← Detailed guide
3. `SETUP_CHECKLIST.md` ← Track progress
4. Run `test_respeaker_setup.py` ← Verify hardware

**If something breaks:**
1. `TROUBLESHOOTING.md` ← Find your problem
2. Run health check script
3. Create diagnostic report

**For reference:**
- `RASPBERRY_PI_SETUP.md` ← Original guide
- Various `.txt` files ← Fixes and solutions

---

## 🎯 Your Hardware Setup

```
ReSpeaker 4-Mic Array
       ↓ (USB to)
  Raspberry Pi
       ↓ (Audio Out to)
   JBL Speaker
```

### Device Indices (Typical)
- Microphone (ReSpeaker): Device 1
- Speaker (JBL): Device 0
- (May vary - test_respeaker_setup.py will show yours)

---

## 💻 Commands You'll Use Most

```bash
# Setup (one-time)
cd ~/respeaker-ai
python3 -m venv venv
source venv/bin/activate
pip install vosk sounddevice google-generativeai
cd models && wget ... && unzip ... && cd ..

# Testing (before running)
python test_respeaker_setup.py

# Running (every time)
source venv/bin/activate
python3 hello_ai_pi_custom.py

# Stopping
Ctrl+C

# Deactivating environment
deactivate
```

---

## 🔑 Key Settings in hello_ai_pi_custom.py

**Line 9:** Gemini API Key
```python
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
# Replace with your actual key
```

**Line 10:** Model directory
```python
MODEL_DIR = "models/en"
# Should be models/en after extraction
```

**Lines 13-14:** Audio settings (usually fine as-is)
```python
RESPEAKER_RATE = 16000  # Sample rate
RESPEAKER_CHANNELS = 1   # Mono
```

---

## 📊 Installation Checklist (Copy-Paste)

```bash
# 1. System dependencies (one-time)
sudo apt-get update
sudo apt-get install -y espeak portaudio19-dev libasound2-dev libportaudio2 python3-pip python3-dev python3-venv ffmpeg

# 2. Project setup (one-time)
cd ~/
git clone https://github.com/Tushar0314/respeaker-ai.git
cd respeaker-ai
python3 -m venv venv

# 3. Python packages (one-time)
source venv/bin/activate
pip install --upgrade pip
pip install vosk sounddevice google-generativeai

# 4. Vosk model (one-time)
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip
cd ..

# 5. Configuration (one-time)
nano hello_ai_pi_custom.py
# Replace API key, save, exit

# 6. Test
python test_respeaker_setup.py

# 7. Run!
python3 hello_ai_pi_custom.py
```

---

## 🎤 How It Works

```
1. You speak into ReSpeaker
            ↓
2. Audio captured at 16kHz
            ↓
3. Vosk recognizes speech
            ↓
4. Text sent to Gemini API
            ↓
5. Gemini generates response
            ↓
6. Response spoken through JBL speaker
            ↓
7. Ready for next conversation
```

---

## ⚠️ Important Notes

1. **Always activate venv first:** `source venv/bin/activate`
2. **Never use sudo with pip:** Use `pip install`, not `sudo pip install`
3. **API key needed:** Get from https://aistudio.google.com
4. **ReSpeaker USB mounted:** Check with `lsusb | grep seeed`
5. **Speaker connected:** 3.5mm jack or USB
6. **Test before running:** `python test_respeaker_setup.py`

---

## 📞 Support Files

When asking for help, provide:
1. Output from `test_respeaker_setup.py`
2. Output from running the script
3. Your `/home/pi/respeaker-ai/` directory listing
4. `cat TROUBLESHOOTING.md` relevant section

---

## 🔄 File Organization

```
respeaker-ai/
├── hello_ai_pi_custom.py ⭐⭐⭐ (RUN THIS)
├── test_respeaker_setup.py ⭐⭐ (TEST THIS FIRST)
├── QUICK_START.md ⭐⭐⭐ (READ THIS FIRST)
├── RASPBERRY_PI_SETUP_CUSTOM.md ⭐⭐ (DETAILED GUIDE)
├── SETUP_CHECKLIST.md ⭐⭐ (TRACK PROGRESS)
├── TROUBLESHOOTING.md ⭐⭐ (FIX PROBLEMS)
│
├── hello_ai.py (reference)
├── hello_ai_rpi.py (alternative)
├── test_tts.py (extra testing)
│
├── models/
│   └── en/ (speech recognition model)
├── venv/ (python environment)
│
├── install_rpi.sh (automated setup)
├── RASPBERRY_PI_SETUP.md (original guide)
└── Other docs (*.txt, *.md files)
```

---

## ✅ Success Criteria

Your setup is complete when you see:
- ✓ ReSpeaker detected
- ✓ Gemini model loaded
- ✓ "Voice assistant ready" spoken
- ✓ "[LISTENING]" prompt shown
- ✓ Speech recognized as text
- ✓ AI response spoken back

---

## 🚨 Emergency Commands

```bash
# Kill stuck script
pkill -f hello_ai_pi_custom.py

# Check what's running
ps aux | grep python

# View recent errors
cat run.log | tail -20

# Restart everything
sudo reboot

# Check internet
ping google.com

# Check audio
espeak "Test"

# Check ReSpeaker
lsusb | grep seeed
```

---

**Ready to start?** 🎉

1. SSH into your Raspberry Pi
2. Read `QUICK_START.md`
3. Follow the copy-paste commands
4. Enjoy your voice assistant!

**Questions?** Check `TROUBLESHOOTING.md` first! 🔧
