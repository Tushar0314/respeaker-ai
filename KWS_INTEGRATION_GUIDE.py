"""
Integration Guide: KWS (Keyword Spotting) with hello_ai.py

This file shows the EXACT changes needed to integrate keyword spotting
into your existing hello_ai.py to detect "WHERE" and "SPEED" keywords.

BEFORE:
  Audio → Vosk (always running) → Gemini → TTS

AFTER:  
  Audio → KWS (quick check) → Vosk (only if keyword detected) → Gemini → TTS

Benefits:
  ✓ Faster response time
  ✓ Lower CPU usage
  ✓ Fewer false positives
  ✓ Works offline
"""

# ============================================================================
# SECTION 1: IMPORTS TO ADD
# ============================================================================

# Add these imports to the top of hello_ai.py:
"""
from keyword_spotter import MultiKeywordSpotter, StreamingKeywordDetector
"""


# ============================================================================
# SECTION 2: SETUP CODE (After Vosk initialization)
# ============================================================================

def setup_keyword_spotters():
    """
    Initialize keyword spotters for "WHERE" and "SPEED" keywords.
    
    Call this function once at startup, after Vosk is initialized.
    """
    
    # Create multi-keyword detector
    kws_detector = MultiKeywordSpotter()
    
    # Add spotter for "WHERE" keyword
    try:
        kws_detector.add_spotter(
            keyword='where',
            model_path='models/kws/where.tflite',
            threshold=0.85  # Adjust 0-1 (lower = more sensitive, more false positives)
        )
    except Exception as e:
        print(f"⚠️  Could not load WHERE model: {e}")
    
    # Add spotter for "SPEED" keyword  
    try:
        kws_detector.add_spotter(
            keyword='speed',
            model_path='models/kws/speed.tflite',
            threshold=0.85
        )
    except Exception as e:
        print(f"⚠️  Could not load SPEED model: {e}")
    
    return kws_detector


# ============================================================================
# SECTION 3: AUDIO PROCESSING LOOP MODIFICATION
# ============================================================================

"""
CURRENT CODE in hello_ai.py:

    with sd.InputStream(device=MIC_INDEX, samplerate=RATE, channels=1, blocksize=4096):
        recognizer = KaldiRecognizer(model, RATE)
        recognizer.SetWords(wlist)
        
        print("Listening... (Ctrl+C to exit)")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("result", [])
                ...


MODIFIED CODE:

    with sd.InputStream(device=MIC_INDEX, samplerate=RATE, channels=1, blocksize=4096):
        recognizer = KaldiRecognizer(model, RATE)
        recognizer.SetWords(wlist)
        
        # Initialize keyword spotters
        kws_detector = setup_keyword_spotters()  # ← ADD THIS LINE
        
        print("Listening... (Ctrl+C to exit)")
        while True:
            data = q.get()
            
            # ============ ADD THIS SECTION ============
            # Convert audio to numpy array for KWS
            import numpy as np
            audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Check for keywords
            detected_keyword = kws_detector.detect_any(audio_array)
            
            if detected_keyword:
                print(f"✓ '{detected_keyword.upper()}' detected!")
            # =========================================
            
            # Only run Vosk if keyword detected
            # (OPTIONAL: For energy saving on RPi)
            # if not detected_keyword:
            #     continue  # Skip Vosk processing if no keyword
            
            # Original Vosk processing
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("result", [])
                ...
"""


# ============================================================================
# SECTION 4: COMPLETE EXAMPLE FILE
# ============================================================================

EXAMPLE_CODE = """
# hello_ai_with_kws.py - Complete example with keyword spotting

import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3
import numpy as np
import google.generativeai as genai
from keyword_spotter import MultiKeywordSpotter

# ... existing imports and setup ...

# SETUP KEYWORD SPOTTERS
def setup_keyword_spotters():
    kws_detector = MultiKeywordSpotter()
    try:
        kws_detector.add_spotter('where', 'models/kws/where.tflite', threshold=0.85)
        kws_detector.add_spotter('speed', 'models/kws/speed.tflite', threshold=0.85)
        return kws_detector
    except Exception as e:
        print(f"⚠️  KWS models not found: {e}")
        return None

# AUDIO CALLBACK
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio error: {status}")
    q.put(bytes(indata))

# MAIN LISTENING LOOP
def main():
    model = Model("models/en")
    recognizer = KaldiRecognizer(model, RATE)
    
    # Initialize KWS
    kws_detector = setup_keyword_spotters()
    
    print("🎤 Listening for keywords: 'WHERE' and 'SPEED'...")
    
    with sd.InputStream(
        device=MIC_INDEX,
        samplerate=RATE,
        channels=1,
        blocksize=4096,
        callback=audio_callback
    ):
        while True:
            data = q.get()
            
            # === KEYWORD DETECTION ===
            if kws_detector:
                audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                detected_keyword = kws_detector.detect_any(audio_array)
                
                if not detected_keyword:
                    continue  # Skip Vosk if no keyword (saves CPU)
            
            # === VOSK SPEECH RECOGNITION ===
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("result", [])
                
                if text:
                    speech_text = ' '.join(text)
                    print(f"🗣️  You said: {speech_text}")
                    
                    # === GEMINI AI PROCESSING ===
                    genai.configure(api_key=GEMINI_API_KEY)
                    model_ai = genai.GenerativeModel('gemini-pro')
                    response = model_ai.generate_content(speech_text)
                    ai_text = response.text
                    
                    print(f"🤖 AI says: {ai_text}")
                    
                    # === TEXT-TO-SPEECH ===
                    engine = pyttsx3.init()
                    engine.say(ai_text)
                    engine.runAndWait()

if __name__ == "__main__":
    main()
"""


# ============================================================================
# SECTION 5: STEP-BY-STEP INTEGRATION CHECKLIST
# ============================================================================

INTEGRATION_CHECKLIST = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    INTEGRATION CHECKLIST                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: PREPARE MODELS
  ☐ Verify models directory: ls -la models/
  ☐ Create models/kws/ directory: mkdir -p models/kws
  ☐ Place trained models:
     - models/kws/where.tflite
     - models/kws/speed.tflite
    
    NOTE: You can get these models by:
    Option A) Train using KWS-DS-CNN repo:
      git clone https://github.com/PeterMS123/KWS-DS-CNN-for-embedded.git
      python train.py --keywords where,speed
    
    Option B) Download pre-trained from TensorFlow Hub
    Option C) Use TensorFlow Model Maker for transfer learning

STEP 2: INSTALL DEPENDENCIES
  ☐ pip install tensorflow
  ☐ OR: pip install tflite-runtime  (lighter weight)
  ☐ pip install numpy
  ☐ pip install -r requirements_rpi.txt

STEP 3: ADD KEYWORD SPOTTER MODULE
  ☐ Verify keyword_spotter.py exists in project root
  ☐ Test: python keyword_spotter.py
  ☐ Should show "Next Steps" message with no errors

STEP 4: MODIFY hello_ai.py
  ☐ Add import: from keyword_spotter import MultiKeywordSpotter
  ☐ Add setup_keyword_spotters() function (from Section 2 above)
  ☐ Initialize kws_detector in main loop (one line)
  ☐ Add audio conversion: audio_array = np.frombuffer(...)
  ☐ Add keyword detection: detected_keyword = kws_detector.detect_any(...)
  ☐ Optional: Skip Vosk if no keyword detected

STEP 5: TEST
  ☐ Run: python hello_ai.py
  ☐ Say "WHERE" near microphone
  ☐ Verify: "WHERE detected!" appears
  ☐ Say "SPEED" near microphone
  ☐ Verify: "SPEED detected!" appears
  ☐ Test with noise to verify threshold is correct

STEP 6: TUNE THRESHOLDS
  If getting false positives (detecting when shouldn't):
    ☐ Increase threshold: 0.85 → 0.90 → 0.95
  
  If not detecting keywords:
    ☐ Decrease threshold: 0.85 → 0.80 → 0.75

STEP 7: OPTIMIZE (FOR RASPBERRY PI)
  ☐ Replace TensorFlow with tflite-runtime (smaller)
  ☐ Test on actual RPi with ReSpeaker hardware
  ☐ Measure CPU/memory usage
  ☐ Add skip logic: if not detected_keyword: continue

STEP 8: DEPLOY
  ☐ Update requirements_rpi.txt with new dependencies
  ☐ Test on Raspberry Pi hardware
  ☐ Create backup: cp hello_ai.py hello_ai.py.backup
  ☐ Deploy to production

╚════════════════════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# SECTION 6: TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    TROUBLESHOOTING GUIDE                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

PROBLEM: "ModuleNotFoundError: No module named 'tensorflow'"
SOLUTION:
  pip install tensorflow
  OR (for Raspberry Pi, use lightweight version):
  pip install tflite-runtime

PROBLEM: "FileNotFoundError: models/kws/where.tflite not found"
SOLUTION:
  1. Create directory: mkdir -p models/kws
  2. Place your model files there
  3. Use absolute paths if needed:
     /Users/tusharbhaliya/Desktop/AI/respeaker-ai/models/kws/where.tflite

PROBLEM: "Keyword never detected (threshold too high)"
SOLUTION:
  Lower threshold value: 0.90 → 0.80
  Test with: kws_detector.detect_all_confidences(audio_array)
  See actual confidence scores

PROBLEM: "Too many false positives"
SOLUTION:
  Raise threshold value: 0.85 → 0.95
  Test sensitivity with various inputs

PROBLEM: "Audio processing is slow / high CPU usage"
SOLUTION:
  Option 1: Skip Vosk when no keyword:
    if not detected_keyword:
        continue  # Don't run Vosk
  
  Option 2: Use tflite-runtime instead of TensorFlow
  
  Option 3: Increase buffer size for KWS (process less frequently)

PROBLEM: "Vosk and KWS running simultaneously = double processing"
SOLUTION:
  Use the skip logic:
    if kws_detector and not detected_keyword:
        continue  # Don't run Vosk until keyword detected

╚════════════════════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# SECTION 7: PERFORMANCE COMPARISON
# ============================================================================

PERFORMANCE_DATA = """
╔════════════════════════════════════════════════════════════════════════════╗
║              BEFORE vs AFTER INTEGRATION                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

METRIC                  | WITHOUT KWS        | WITH KWS           | BENEFIT
────────────────────────┼──────────────────┼──────────────────┼─────────────────
Response Time           | ~500ms (always)    | ~100ms (keyword)   | 5x faster
CPU Usage (Vosk)        | 100% continuous    | 10% (standby)      | 10x less
Memory (Both Models)    | ~50MB              | ~55MB              | +5MB only
False Positives         | High (always on)   | Low (gated)        | Much better
Power Draw (RPi)        | ~2W                | ~0.5W (idle)       | 4x efficiency
Latency if Detected     | ~500ms             | ~550ms             | +50ms only
────────────────────────┴──────────────────┴──────────────────┴─────────────────

⚠️  NOTE: These are estimated values. Actual performance depends on:
  - Model size and architecture
  - Audio sample rate
  - Hardware (laptop vs Raspberry Pi)
  - Threshold settings

╚════════════════════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    print(INTEGRATION_CHECKLIST)
    print("\n" + "="*80 + "\n")
    print(TROUBLESHOOTING)
    print("\n" + "="*80 + "\n")
    print(PERFORMANCE_DATA)
