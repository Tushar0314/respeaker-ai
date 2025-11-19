# 📋 Raspberry Pi Voice Assistant - Setup Checklist

## Hardware Verification
- [ ] Raspberry Pi connected to PC/Network
- [ ] ReSpeaker 4-Mic Array mounted on top of Pi (USB connected)
- [ ] JBL Speaker connected to Pi's audio jack (or USB)
- [ ] Gemini API Key ready

## Software Installation

### System Setup
- [ ] SSH into Raspberry Pi: `ssh pi@raspberrypi.local`
- [ ] System updated: `sudo apt-get update && sudo apt-get upgrade -y`
- [ ] System dependencies installed (espeak, portaudio, etc.)
  - Run: `sudo apt-get install -y espeak portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 python3-pip python3-dev python3-venv ffmpeg alsa-utils build-essential`
  - Verify: `pkg-config --modversion portaudio-2.0`

### Project Setup
- [ ] Project cloned: `git clone https://github.com/Tushar0314/respeaker-ai.git`
- [ ] Navigated to folder: `cd ~/respeaker-ai`
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Pip upgraded: `pip install --upgrade pip setuptools wheel`

### Python Packages
- [ ] vosk installed: `pip install vosk`
- [ ] sounddevice installed: `pip install sounddevice`
- [ ] google-generativeai installed: `pip install google-generativeai`
- [ ] Packages verified: `python -c "import sounddevice; import vosk; print('✓ OK')"`

### Vosk Model
- [ ] Navigated to models folder: `cd models`
- [ ] Model downloaded: `wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip`
- [ ] Model extracted: `unzip vosk-model-small-en-us-0.15.zip`
- [ ] Model renamed: `mv vosk-model-small-en-us-0.15 en`
- [ ] Cleanup: `rm vosk-model-small-en-us-0.15.zip`
- [ ] Verify model exists: `ls models/en/` shows files
- [ ] Returned to project root: `cd ..`

## Configuration

### Audio Setup
- [ ] Audio devices listed: `arecord -l` and `aplay -l`
- [ ] ReSpeaker detected in list
- [ ] JBL speaker (or audio output) detected
- [ ] Test script run: `python test_respeaker_setup.py`

### API Key Configuration
- [ ] Opened `hello_ai_pi_custom.py`: `nano hello_ai_pi_custom.py`
- [ ] Found line: `GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'`
- [ ] Replaced with actual key: `GEMINI_API_KEY = 'your-api-key-here'`
- [ ] Saved file: `Ctrl+X` → `Y` → `Enter`

## Testing

### Component Tests
- [ ] Microphone test:
  - `arecord -D hw:1,0 -d 3 test.wav`
  - `aplay test.wav`
  - Result: Can hear recorded sound ✓

- [ ] Speaker test:
  - `espeak "Hello this is a test"`
  - Result: Hear "Hello..." from JBL speaker ✓

- [ ] Gemini API test:
  - `python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('✓ API OK')"`
  - Result: No errors ✓

### Full System Test
- [ ] Voice assistant started: `python3 hello_ai_pi_custom.py`
- [ ] Sees "Detecting ReSpeaker" message
- [ ] ReSpeaker device number found
- [ ] Gemini model loaded successfully
- [ ] Hears "Voice assistant ready"
- [ ] Sees "[READY] Say something..." message

## Running the System

### First Run
- [ ] Activated environment: `source venv/bin/activate`
- [ ] Started program: `python3 hello_ai_pi_custom.py`
- [ ] Waited for "[LISTENING]" prompt
- [ ] Spoke clearly into microphone
- [ ] Speech recognized and printed
- [ ] AI response generated
- [ ] Response spoken through JBL speaker ✓

### Success Indicators
- [ ] Microphone picks up sound
- [ ] Speech is recognized correctly
- [ ] AI generates intelligent responses
- [ ] Speaker plays responses audibly

## Troubleshooting (if needed)

### Microphone Issues
- [ ] ReSpeaker USB connection verified
- [ ] ReSpeaker LED indicator is ON
- [ ] Microphone orientation correct (USB port facing away)
- [ ] Audio device index correct in `test_respeaker_setup.py`

### Speaker Issues
- [ ] JBL speaker powered on and connected
- [ ] Audio jack properly inserted
- [ ] Volume not muted: `alsamixer`
- [ ] Volume level > 50%
- [ ] espeak test successful

### API Issues
- [ ] API key valid and not expired
- [ ] API key has necessary permissions
- [ ] Internet connection working
- [ ] No API rate limiting

### Software Issues
- [ ] Virtual environment properly activated
- [ ] All packages properly installed
- [ ] Vosk model present and correct
- [ ] No Python version conflicts (use 3.9+)

## Maintenance Tasks

- [ ] Regular testing of components
- [ ] Monitor API usage and costs
- [ ] Keep system updated: `sudo apt-get update && upgrade`
- [ ] Backup Gemini API key securely
- [ ] Review and optimize performance

## Optional Enhancements

- [ ] Setup auto-start on boot
- [ ] Configure custom wake words
- [ ] Add logging to file
- [ ] Setup remote access
- [ ] Create systemd service
- [ ] Performance optimization
- [ ] Custom response training

---

## Notes

**Device Indices** (from your setup):
- Microphone (ReSpeaker): `[1]`
- Speaker (JBL): `[0]`

**Important Paths:**
- Project: `/home/pi/respeaker-ai`
- Virtual env: `/home/pi/respeaker-ai/venv`
- Models: `/home/pi/respeaker-ai/models/en`

**API Key:**
- Status: [  ] Configured
- Last verified: ___________

---

## Progress Tracking

**Date Started:** ___________
**Date Completed:** ___________
**Total Time:** ___________

**Signature:** ________________________
