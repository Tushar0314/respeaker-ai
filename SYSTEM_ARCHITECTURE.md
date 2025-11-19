# 🏗️ System Architecture & Flow Diagrams

## Complete System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOICE ASSISTANT SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │ INTERNET/CLOUD   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │                           │
              ┌─────▼────┐          ┌──────────▼──────┐
              │  Google  │          │  Vosk Models    │
              │  Gemini  │          │  (Local/Offline)│
              │   API    │          └─────────────────┘
              └─────┬────┘
                    │
        ┌───────────▼──────────────┐
        │  RASPBERRY PI 3/4        │
        │ ┌──────────────────────┐ │
        │ │ hello_ai_pi_custom   │ │
        │ │ (Main Program)       │ │
        │ └──────────────────────┘ │
        │                          │
        │ ┌────────────────────┐   │
        │ │ Python Environment │   │
        │ │ • vosk             │   │
        │ │ • sounddevice      │   │
        │ │ • google-generativeai   │
        │ └────────────────────┘   │
        └───────┬──────────┬────────┘
                │          │
        ┌───────▼─┐  ┌─────▼────────┐
        │ReSpeaker│  │  JBL Speaker │
        │4-Mic    │  │  (Output)    │
        │Array    │  └──────────────┘
        │(Input)  │
        └─────────┘
```

---

## Data Flow Diagram

```
START
  │
  ├─ Load Models (Vosk, Gemini)
  │
  ├─ Initialize Audio Devices
  │  └─ ReSpeaker: Input
  │  └─ JBL Speaker: Output
  │
  └─ MAIN LOOP
     │
     ├─ [LISTENING]
     │   └─ Capture audio from ReSpeaker
     │       ├─ Record 5 seconds
     │       ├─ Process with Vosk
     │       └─ Convert to text
     │
     ├─ [TEXT RECEIVED] "Hello"
     │   └─ Send to Gemini API
     │
     ├─ [AI THINKING]
     │   └─ Gemini generates response
     │
     ├─ [RESPONSE] "Hello! How can I help?"
     │   └─ Send to text-to-speech (espeak)
     │
     ├─ [SPEAKING]
     │   └─ Output audio to JBL Speaker
     │       ├─ User hears response
     │       └─ Ready for next input
     │
     └─ REPEAT LOOP
        (until Ctrl+C)
```

---

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                     VOICE ASSISTANT COMPONENTS                  │
└─────────────────────────────────────────────────────────────────┘

INPUT LAYER:
┌──────────────────────┐
│  ReSpeaker 4-Mic     │ ← USB connected to Raspberry Pi
│  Array               │   Audio capture @ 16kHz, 16-bit
│  • 4 microphones     │   Auto-detect device index
│  • Beamforming       │
└────────┬─────────────┘
         │ (audio stream)
         │
PROCESSING LAYER:
┌──────────────────────────────────────────────────────────────┐
│                   MAIN PROGRAM                               │
│  hello_ai_pi_custom.py                                      │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Vosk            │  │  Gemini AI       │                │
│  │  (Speech-to-Text)│  │  (Understanding) │                │
│  │                  │  │                  │                │
│  │  • Offline       │  │  • Cloud-based   │                │
│  │  • Fast (<3s)    │  │  • Smart (<2s)   │                │
│  └──────────────────┘  └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
         │                          │
         │ (text)                   │ (response text)
         │                          │
OUTPUT LAYER:
┌──────────────────────┐
│  espeak (TTS)        │ ← Linux text-to-speech
│  • Lightweight       │   ~150 words/minute
│  • Fast              │   Multiple voices available
└────────┬─────────────┘
         │ (audio stream)
         │
┌──────────────────────┐
│  JBL Speaker         │ ← 3.5mm jack from Raspberry Pi
│  • Audio output      │   User hears AI responses
│  • Adjustable volume │   Via alsamixer
└──────────────────────┘
```

---

## File Organization

```
HOME DIRECTORY
└─ respeaker-ai/
   │
   ├─ DOCUMENTATION (START HERE)
   │  ├─ 00_START_HERE_RASPBERRY_PI.md ⭐⭐⭐
   │  ├─ COMPLETE_SUMMARY.md ⭐⭐⭐
   │  ├─ QUICK_START.md ⭐⭐
   │  ├─ RASPBERRY_PI_SETUP_CUSTOM.md ⭐⭐
   │  ├─ SETUP_CHECKLIST.md ⭐
   │  ├─ TROUBLESHOOTING.md ⭐⭐
   │  └─ FILE_OVERVIEW.md
   │
   ├─ MAIN PROGRAM (RUN THIS)
   │  └─ hello_ai_pi_custom.py ⭐⭐⭐
   │
   ├─ TESTING (TEST BEFORE RUNNING)
   │  ├─ test_respeaker_setup.py ⭐⭐
   │  ├─ test_tts.py
   │  └─ test_tts_improved.py
   │
   ├─ PYTHON ENVIRONMENT
   │  └─ venv/
   │     ├─ bin/
   │     │  ├─ python3
   │     │  ├─ pip
   │     │  └─ activate ← source this before running
   │     └─ lib/
   │        └─ (installed packages)
   │
   ├─ SPEECH MODELS
   │  └─ models/
   │     ├─ en/
   │     │  ├─ am/ (acoustic model)
   │     │  ├─ conf/ (configuration)
   │     │  ├─ graph/ (language model)
   │     │  └─ ivector/ (feature extractor)
   │     └─ vosk-model-*.zip (download file)
   │
   ├─ HELPER SCRIPTS
   │  ├─ install_rpi.sh (automated setup)
   │  ├─ emergency_fix.sh (fixes)
   │  └─ (other variations)
   │
   ├─ CONFIGURATION
   │  ├─ .gitignore
   │  ├─ .git/ (version control)
   │  └─ requirements_rpi.txt
   │
   └─ OTHER VERSIONS (reference)
      ├─ hello_ai.py (Mac/Linux)
      ├─ hello_ai_rpi.py (generic Pi)
      └─ hello_ai_rpi_alternative.py

                    ▼▼▼ KEY FILES ▼▼▼
        
        TO RUN:          hello_ai_pi_custom.py
        TO TEST:         test_respeaker_setup.py
        TO READ FIRST:   00_START_HERE_RASPBERRY_PI.md
        WHEN STUCK:      TROUBLESHOOTING.md
```

---

## Installation & Execution Flow

```
┌─────────────────────────────────────────────┐
│  1. SSH INTO RASPBERRY PI                   │
│     ssh pi@raspberrypi.local                │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  2. INSTALL SYSTEM DEPENDENCIES             │
│     sudo apt-get update                     │
│     sudo apt-get install portaudio19-dev... │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  3. CLONE PROJECT                           │
│     git clone https://github.com/...        │
│     cd respeaker-ai                         │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  4. CREATE VIRTUAL ENVIRONMENT              │
│     python3 -m venv venv                    │
│     source venv/bin/activate                │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  5. INSTALL PYTHON PACKAGES                 │
│     pip install vosk sounddevice genai      │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  6. DOWNLOAD VOSK SPEECH MODEL              │
│     cd models                               │
│     wget vosk-model-*.zip                   │
│     unzip && mv vosk-model-* en             │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  7. CONFIGURE API KEY                       │
│     nano hello_ai_pi_custom.py              │
│     Replace GEMINI_API_KEY value            │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  8. TEST SETUP                              │
│     python test_respeaker_setup.py          │
│     Verify ReSpeaker & speaker detected     │
└────────────┬────────────────────────────────┘
             │
┌────────────▼────────────────────────────────┐
│  9. RUN VOICE ASSISTANT                     │
│     python3 hello_ai_pi_custom.py           │
│                                              │
│  [LISTENING...]                             │
│  Say something into ReSpeaker               │
│  [YOU SAID] "hello"                         │
│  [AI RESPONSE] "Hello! How can I help?"     │
│  [SPEAKING] (response plays on speaker)     │
└─────────────────────────────────────────────┘
```

---

## Hardware Connections

```
RASPBERRY PI (Top View)
┌─────────────────────────────────────────┐
│                                          │
│   ┌─────────────────────────────────┐  │
│   │  ReSpeaker 4-Mic Array          │  │
│   │  (Mounted on GPIO pins)         │  │
│   │  USB Port ──────┐               │  │
│   └─────────────────────────────────┘  │
│                   │                      │
│          ┌────────▼─────────┐            │
│          │ Raspberry Pi     │            │
│          │ GPIO Header      │            │
│          └──────────────────┘            │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │ USB-A (3x)                       │  │
│   │ (Can also power ReSpeaker via    │  │
│   │  USB hub if needed)              │  │
│   └──────────────────────────────────┘  │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │ 3.5mm Audio Jack                 │──┼──→ JBL Speaker
│   │ (Headphone Output)               │  │
│   └──────────────────────────────────┘  │
│                                          │
└─────────────────────────────────────────┘
           │
           │ Ethernet or WiFi
           ▼
      INTERNET
      (for Gemini API)
```

---

## Runtime Behavior

```
TIME    ACTION                          COMPONENT
────────────────────────────────────────────────────────────────
0:00    Start program
        ├─ Load Vosk model              [vosk]
        ├─ Connect to Gemini            [google-generativeai]
        ├─ Initialize audio devices     [sounddevice]
        └─ Ready!                       [main program]

5:00    "[LISTENING]" message appears
        └─ ReSpeaker recording starts   [ReSpeaker]

8:00    User speaks "Hello"
        └─ Audio captured               [ReSpeaker → sounddevice]

10:00   "[YOU SAID] hello"
        └─ Vosk recognizes speech       [Vosk]

10:50   Sending to Gemini...
        └─ Text sent to API             [google-generativeai]

12:00   Waiting for response...
        └─ Gemini thinking              [Gemini API]

13:50   "[AI RESPONSE] Hello! How can I help?"
        └─ Response received            [google-generativeai]

14:00   "[SPEAKING]"
        └─ Converting to audio          [espeak]

17:00   Audio output to speaker
        └─ User hears response          [JBL Speaker]

18:00   Ready for next input
        └─ Back to listening            [ReSpeaker]
```

---

## Error Handling Flow

```
START PROGRAM
    │
    ├─ ReSpeaker not found?
    │  └─ Ask user for device index
    │
    ├─ Vosk model not found?
    │  └─ Error message + exit
    │
    ├─ Gemini API error?
    │  └─ Fallback message + retry
    │
    ├─ Audio capture error?
    │  └─ Log error + continue
    │
    └─ Speaker error?
       └─ Continue (user won't hear, but AI still works)
```

---

## Performance Metrics

```
OPERATION               TIME        STATUS
─────────────────────────────────────────────
Program startup         3-5 sec     Good
Model loading           2-3 sec     Expected
Audio recording         3-5 sec     User-controlled
Vosk recognition        1-3 sec     Varies
Gemini response         1-2 sec     Good
TTS generation          1-3 sec     Depends on length
Total per turn          ~10-15 sec  Acceptable
```

---

This system is designed to be:
✅ **Reliable** - Handles errors gracefully
✅ **Fast** - Responds in seconds
✅ **Offline-capable** - Vosk works without internet
✅ **Scalable** - Easy to add features
✅ **Maintainable** - Well-documented code

