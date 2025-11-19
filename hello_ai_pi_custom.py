#!/usr/bin/env python3
"""
Voice Assistant for Raspberry Pi with ReSpeaker 4-Mic Array
Optimized for best performance with external JBL speaker
Works with Gemini AI for intelligent responses
"""

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import os
import subprocess
import google.generativeai as genai
import time

# ====== CONFIGURATION ======
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
MODEL_DIR = "models/en"

# ReSpeaker 4-Mic Array Settings (OPTIMIZED)
RESPEAKER_RATE = 16000  # 16kHz optimal for ReSpeaker and speech recognition
RESPEAKER_CHANNELS = 1  # Mono (use first channel of ReSpeaker)
RESPEAKER_CHUNK = 1024  # Audio chunk size

print("=" * 60)
print("🎤 Voice Assistant - Raspberry Pi + ReSpeaker 4-Mic Array")
print("🔊 Output: JBL Speaker")
print("=" * 60)

# ====== STEP 1: AUTO-DETECT RESPEAKER ======
def find_respeaker_device():
    """Auto-detect ReSpeaker 4-Mic Array device."""
    print("\n[STEP 1] Detecting ReSpeaker 4-Mic Array...")
    devices = sd.query_devices()
    
    print(f"\nAvailable audio devices ({len(devices)} total):")
    for idx, device in enumerate(devices):
        channels = device.get('max_input_channels', 0)
        if channels > 0:
            print(f"  [{idx}] {device['name']} - Input: {channels} channels, SR: {device.get('default_samplerate', 'N/A')} Hz")
    
    # Look for ReSpeaker specifically
    for idx, device in enumerate(devices):
        name = device['name'].lower()
        if device['max_input_channels'] >= 1:
            # Check for ReSpeaker patterns
            if any(pattern in name for pattern in ['respeaker', 'seeed', 'usb audio', 'usb device']):
                print(f"\n✓ Found ReSpeaker at device index: {idx}")
                print(f"  Name: {device['name']}")
                print(f"  Input channels: {device['max_input_channels']}")
                return idx
    
    # If not auto-detected, ask user to select
    print("\n⚠ ReSpeaker not auto-detected. Please select the ReSpeaker device:")
    try:
        idx = int(input("Enter device index number: "))
        if 0 <= idx < len(devices):
            print(f"✓ Selected device {idx}: {devices[idx]['name']}")
            return idx
    except:
        pass
    
    return None

# ====== STEP 2: SETUP TEXT-TO-SPEECH ======
def say(text):
    """Speak text using espeak (optimized for Raspberry Pi)."""
    if not text or text.strip() == "":
        return
    
    print(f"\n[SPEAKING] {text[:100]}{'...' if len(text) > 100 else ''}")
    
    # Try espeak first (fastest on Pi)
    try:
        subprocess.run(
            ['espeak', '-s', '150', '-a', '200', text],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60
        )
        print("[✓ Speech completed]")
        return
    except Exception as e:
        print(f"[espeak error] {e}")
    
    # Fallback to pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        print("[✓ Speech completed via pyttsx3]")
    except Exception as e:
        print(f"[pyttsx3 error] {e}")

# ====== STEP 3: INITIALIZE GEMINI ======
def init_gemini():
    """Initialize Gemini API with best model."""
    print("\n[STEP 2] Connecting to Gemini AI...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List available models
        available_models = list(genai.list_models())
        print(f"  Available models: {len(available_models)}")
        
        # Prefer faster models for Pi
        preferred_models = [
            'models/gemini-2.0-flash',
            'models/gemini-2.5-flash',
            'models/gemini-flash-latest',
        ]
        
        # Find best model
        for preferred in preferred_models:
            for m in available_models:
                if m.name == preferred:
                    if hasattr(m, 'supported_generation_methods'):
                        if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                            print(f"  ✓ Using model: {m.name}")
                            return m.name
        
        # Fallback
        for m in available_models:
            if hasattr(m, 'supported_generation_methods') and 'generateContent' in getattr(m, 'supported_generation_methods', []):
                print(f"  ✓ Using model: {m.name}")
                return m.name
        
        print("  ✗ No suitable model found")
        return None
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

# ====== STEP 4: SPEECH RECOGNITION ======
def listen_once(mic_index, rate=RESPEAKER_RATE, seconds=3.0):
    """Capture audio from ReSpeaker and recognize speech."""
    q = queue.Queue()
    
    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"[Audio warning] {status}")
        q.put(bytes(indata))
    
    try:
        # Load Vosk model
        model = Model(MODEL_DIR)
        rec = KaldiRecognizer(model, rate)
        rec.Reset()
        
        frames_needed = int(rate * seconds)
        got = 0
        
        # Capture audio
        with sd.RawInputStream(
            device=mic_index,
            samplerate=rate,
            blocksize=RESPEAKER_CHUNK,
            dtype='int16',
            channels=RESPEAKER_CHANNELS,
            callback=audio_callback
        ):
            while got < frames_needed:
                try:
                    buf = q.get(timeout=1)
                    got += len(buf) // 2
                    
                    if rec.AcceptWaveform(buf):
                        break
                except queue.Empty:
                    break
        
        # Get final result
        result = json.loads(rec.FinalResult())
        text = result.get("text", "").strip()
        return text
        
    except Exception as e:
        print(f"[Listen error] {e}")
        return ""

# ====== STEP 5: GET GEMINI RESPONSE ======
def get_ai_response(prompt, model_name):
    """Get response from Gemini AI."""
    if not model_name:
        return "AI model not available"
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, stream=False)
        return response.text
    except Exception as e:
        return f"Error getting response: {e}"

# ====== STEP 6: MAIN LOOP ======
def main():
    """Main voice assistant loop."""
    
    # Step 1: Find ReSpeaker
    mic_index = find_respeaker_device()
    if mic_index is None:
        print("\n✗ Cannot find ReSpeaker device. Exiting.")
        return
    
    # Step 2: Initialize Gemini
    model_name = init_gemini()
    if not model_name:
        print("\n✗ Cannot connect to Gemini. Check API key. Exiting.")
        return
    
    # Step 3: Check Vosk model
    if not os.path.exists(MODEL_DIR):
        print(f"\n✗ Vosk model not found at {MODEL_DIR}")
        print("  Download: wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        return
    
    # Step 4: Ready to go!
    print("\n" + "=" * 60)
    print("[✓ SETUP COMPLETE]")
    print(f"  Microphone: ReSpeaker (device {mic_index})")
    print(f"  Sample Rate: {RESPEAKER_RATE} Hz")
    print(f"  AI Model: {model_name}")
    print(f"  Speaker: JBL (via Pi audio output)")
    print("=" * 60)
    
    # Test audio
    print("\n[STARTUP TEST]")
    say("Voice assistant ready. Listening for commands.")
    
    print("\n[READY] Say something to the ReSpeaker microphone...")
    print("       Press Ctrl+C to stop\n")
    
    conversation_count = 0
    
    try:
        while True:
            print("\n" + "=" * 60)
            print(f"[LISTENING #{conversation_count + 1}...]")
            print("=" * 60)
            
            # Listen for speech
            recognized_text = listen_once(mic_index, RESPEAKER_RATE, seconds=5.0)
            
            if recognized_text:
                print(f"\n[YOU SAID] {recognized_text}")
                
                # Get AI response
                print(f"\n[AI THINKING...]")
                response = get_ai_response(recognized_text, model_name)
                
                print(f"\n[AI RESPONSE] {response}")
                
                # Speak response
                say(response)
                
                conversation_count += 1
            else:
                print("\n[NO SPEECH DETECTED] Listening again...")
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("[SHUTTING DOWN]")
        print("=" * 60)
        say("Voice assistant shutting down. Goodbye!")
        print("Goodbye!")
    
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")

# ====== RUN ======
if __name__ == "__main__":
    main()
