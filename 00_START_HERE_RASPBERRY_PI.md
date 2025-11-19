# 🎤 VOICE ASSISTANT FOR RASPBERRY PI - START HERE! 🎤

## ✨ What You Have

A complete voice assistant system for your Raspberry Pi that:
- 🎤 Listens through **ReSpeaker 4-Mic Array**
- 🧠 Thinks using **Google Gemini AI**
- 🔊 Speaks through your **JBL Speaker**

---

## 🚀 3-Minute Quick Start

### Step 1: SSH into Your Raspberry Pi
```bash
ssh pi@raspberrypi.local
# Or: ssh pi@<your_raspberry_pi_ip>
```

### Step 2: Copy-Paste This Entire Block
```bash
cd ~
git clone https://github.com/Tushar0314/respeaker-ai.git
cd respeaker-ai

# Install dependencies (takes ~10 minutes)
sudo apt-get update
sudo apt-get install -y espeak portaudio19-dev libasound2-dev libportaudio2 python3-pip python3-dev python3-venv ffmpeg

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install vosk sounddevice google-generativeai

# Get speech model
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en
rm vosk-model-small-en-us-0.15.zip
cd ..
```

### Step 3: Configure Your API Key
```bash
nano hello_ai_pi_custom.py
```

Find this line (line 9):
```python
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
```

Replace `AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ` with your actual Gemini API key.

Get your key: https://aistudio.google.com → "Get API Key"

Save file: `Ctrl+X` → `Y` → `Enter`

### Step 4: Test Your Setup
```bash
source venv/bin/activate
python test_respeaker_setup.py
```

Expected output:
```
🎤 ReSpeaker 4-Mic Array - Detection & Calibration Test
[STEP 1] Audio Devices Detected:
[1] ReSpeaker ← This should show!
[STEP 2] ReSpeaker Detection:
✓ ReSpeaker found at device index: 1
```

### Step 5: Run Voice Assistant!
```bash
source venv/bin/activate
python3 hello_ai_pi_custom.py
```

**Wait for message:** `[READY] Say something to the ReSpeaker microphone...`

**Then speak!** 🎤

---

## 📝 What to Expect

```
🎤 Voice Assistant - Raspberry Pi + ReSpeaker 4-Mic Array
🔊 Output: JBL Speaker
============================================================

[STEP 1] Detecting ReSpeaker 4-Mic Array...
[STEP 2] Connecting to Gemini AI...
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

Now speak clearly into your ReSpeaker! 🎤

---

## 🎯 Try These Commands

After it says "Say something...":

1. **"Hello"** → AI says "Hello! How can I help?"
2. **"What time is it?"** → Gets current time info
3. **"Tell me a joke"** → AI tells a joke
4. **"What is Python?"** → Explanation of Python
5. **"Calculate 2 plus 2"** → Does math

---

## 📚 Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **QUICK_START.md** | Fast setup guide | Before running |
| **RASPBERRY_PI_SETUP_CUSTOM.md** | Detailed instructions | During setup |
| **SETUP_CHECKLIST.md** | Track your progress | While setting up |
| **TROUBLESHOOTING.md** | Fix problems | If something breaks |
| **FILE_OVERVIEW.md** | Complete file list | For reference |

---

## 🔧 Troubleshooting

### ReSpeaker Not Detected?
```bash
lsusb | grep seeed
# Should show: Seeed Studio ReSpeaker
```

### Can't Hear Speaker?
```bash
espeak "Hello test"
# Should hear this from JBL speaker
```

### Microphone Not Working?
```bash
arecord -d 3 test.wav && aplay test.wav
# Should record and play your voice
```

### Import Errors?
```bash
source venv/bin/activate
pip install vosk sounddevice google-generativeai
```

---

## 🔄 Running Every Day

Every time you want to use it:

```bash
# SSH in
ssh pi@raspberrypi.local

# Navigate to folder
cd ~/respeaker-ai

# Activate Python environment
source venv/bin/activate

# Run it!
python3 hello_ai_pi_custom.py

# To stop: Press Ctrl+C
```

---

## ⚡ Common Issues & Fixes

### Issue: "vosk module not found"
**Fix:** `source venv/bin/activate`

### Issue: "ReSpeaker not detected"
**Fix:** Check USB connection, run `lsusb | grep seeed`

### Issue: "Can't hear AI speaking"
**Fix:** Check speaker connection, run `espeak "test"`

### Issue: "API error"
**Fix:** Check your API key is correct in `hello_ai_pi_custom.py`

---

## 🎨 Cool Things to Try

1. **Ask it questions** about anything
2. **Tell it jokes** - it will laugh
3. **Ask for cooking recipes**
4. **Get homework help**
5. **Ask trivia questions**
6. **Tell it to summarize things**
7. **Use it as a timer** (if extended)
8. **Make it explain concepts**

---

## 📞 If You Need Help

1. **Check TROUBLESHOOTING.md** first
2. **Run test_respeaker_setup.py** to diagnose
3. **Save the error output** and share it
4. **Tell me:**
   - What error you see
   - What you were doing
   - Your Raspberry Pi model

---

## ✅ Checklist Before Running

- [ ] Raspberry Pi SSH connection working
- [ ] ReSpeaker 4-Mic mounted on top
- [ ] ReSpeaker USB connected to Pi
- [ ] JBL speaker connected to audio jack
- [ ] Internet working on Pi (`ping google.com`)
- [ ] All files copied to ~/respeaker-ai
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] API key added to `hello_ai_pi_custom.py`
- [ ] Test passed (`python test_respeaker_setup.py`)

---

## 🎉 You're Ready!

Run this command and start talking to AI:
```bash
cd ~/respeaker-ai && source venv/bin/activate && python3 hello_ai_pi_custom.py
```

---

## 📖 Next Steps (After Working)

1. **Customize responses** in `hello_ai_pi_custom.py`
2. **Auto-start on boot** using systemd service
3. **Add custom commands** and keywords
4. **Integrate with home automation**
5. **Improve speech quality** with different models

---

**Questions?** 

Check these in order:
1. QUICK_START.md
2. RASPBERRY_PI_SETUP_CUSTOM.md
3. TROUBLESHOOTING.md
4. FILE_OVERVIEW.md

**Let me know how it goes!** 🚀

---

## 🎬 Final Check

Before you say you're done:

1. Run the setup commands above
2. Test with `python test_respeaker_setup.py`
3. Start with `python3 hello_ai_pi_custom.py`
4. Say "hello" into the ReSpeaker
5. Hear AI response from JBL speaker

**If all 5 work, you're done!** ✅🎉

---

**Version:** 1.0
**Updated:** November 18, 2025
**Hardware:** Raspberry Pi + ReSpeaker 4-Mic + JBL Speaker
**AI:** Google Gemini
**Status:** Ready to Use! ✅
