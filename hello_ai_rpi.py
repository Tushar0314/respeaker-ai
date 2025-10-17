#!/usr/bin/env python3
"""
Voice Assistant for Raspberry Pi 3 with ReSpeaker Microphone Array
Optimized for 32-bit Raspberry Pi OS
"""

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import os
import subprocess
import google.generativeai as genai

# Configuration
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
MODEL_DIR = "models/en"  # Download Vosk model for Raspberry Pi

# ReSpeaker typically uses these settings
RESPEAKER_RATE = 16000  # 16kHz is optimal for ReSpeaker
RESPEAKER_CHANNELS = 1  # Mono
RESPEAKER_INDEX = None  # Will auto-detect

def find_respeaker_device():
    """Find ReSpeaker device index automatically."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        name = device['name'].lower()
        # Look for ReSpeaker or USB Audio Device
        if 'respeaker' in name or 'seeed' in name or ('usb' in name and device['max_input_channels'] >= 1):
            print(f"[Device] Found potential ReSpeaker at index {idx}: {device['name']}")
            return idx
    print("[Device] ReSpeaker not found, listing all input devices:")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  {idx}: {device['name']} (IN channels: {device['max_input_channels']})")
    return None

def setup_respeaker():
    """Configure ReSpeaker hardware (LEDs, etc) if available."""
    try:
        # Try to import ReSpeaker library
        from respeaker import Microphone
        print("[ReSpeaker] Hardware library found, initializing...")
        return Microphone()
    except ImportError:
        print("[ReSpeaker] Hardware library not found (install python3-respeaker-python-library if needed)")
        return None
    except Exception as e:
        print(f"[ReSpeaker] Could not initialize hardware: {e}")
        return None

def tts_espeak(text):
    """Use espeak for text-to-speech on Raspberry Pi (lightweight)."""
    try:
        # espeak is pre-installed on most Raspberry Pi OS
        subprocess.run(['espeak', '-s', '150', '-a', '200', text], 
                      check=False, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        print("[TTS] espeak not found. Install with: sudo apt-get install espeak")
        return False
    except Exception as e:
        print(f"[TTS] espeak error: {e}")
        return False

def tts_pyttsx3(text):
    """Fallback TTS using pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[TTS] pyttsx3 error: {e}")
        return False

def say(text):
    """Speak text using available TTS engine."""
    print(f"[TTS] -> {text}")
    
    # Try espeak first (faster and lighter on Raspberry Pi)
    if tts_espeak(text):
        return
    
    # Fallback to pyttsx3
    if tts_pyttsx3(text):
        return
    
    print("[TTS] All TTS engines failed")

def init_gemini():
    """Initialize Gemini API and select best model."""
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("\n=== Initializing Gemini AI ===")
    try:
        available_models = list(genai.list_models())
        
        # Preferred models for Raspberry Pi (lighter/faster)
        preferred_models = [
            'models/gemini-2.0-flash',
            'models/gemini-2.5-flash',
            'models/gemini-flash-latest',
        ]
        
        for preferred in preferred_models:
            for m in available_models:
                if m.name == preferred and hasattr(m, 'supported_generation_methods') and \
                   'generateContent' in getattr(m, 'supported_generation_methods', []):
                    print(f"[Gemini] Using model: {m.name}")
                    return m.name
        
        # Fallback to first available
        for m in available_models:
            if hasattr(m, 'supported_generation_methods') and \
               'generateContent' in getattr(m, 'supported_generation_methods', []):
                print(f"[Gemini] Using model: {m.name}")
                return m.name
        
        print("[Gemini] No suitable model found!")
        return None
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return None

def gemini_response(prompt, model_name):
    """Get response from Gemini AI."""
    if not model_name:
        return "Gemini model not available"
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def listen_once(mic_index, rate, seconds=3.0):
    """Capture audio and return recognized text."""
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if status:
            print(f"[Audio] {status}")
        q.put(bytes(indata))
    
    # Initialize recognizer
    model = Model(MODEL_DIR)
    rec = KaldiRecognizer(model, rate)
    rec.Reset()
    
    frames_needed = int(rate * seconds)
    got = 0
    
    try:
        with sd.RawInputStream(device=mic_index, 
                              samplerate=rate, 
                              blocksize=2048,
                              dtype='int16', 
                              channels=RESPEAKER_CHANNELS, 
                              callback=callback):
            while got < frames_needed:
                buf = q.get()
                got += len(buf) // 2
                if rec.AcceptWaveform(buf):
                    break
        
        result = json.loads(rec.FinalResult())
        return result.get("text", "").strip()
    except Exception as e:
        print(f"[Audio] Error: {e}")
        return ""

def main():
    print("=" * 50)
    print("Voice Assistant for Raspberry Pi + ReSpeaker")
    print("=" * 50)
    
    # Find ReSpeaker device
    global RESPEAKER_INDEX
    RESPEAKER_INDEX = find_respeaker_device()
    
    if RESPEAKER_INDEX is None:
        print("\n[Error] Could not find ReSpeaker device!")
        print("Please enter device index manually:")
        devices = sd.query_devices()
        for idx, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                print(f"  {idx}: {d['name']}")
        try:
            RESPEAKER_INDEX = int(input("Enter device index: "))
        except:
            print("Invalid input. Exiting.")
            return
    
    # Setup ReSpeaker hardware (optional)
    mic_hw = setup_respeaker()
    
    # Initialize Gemini
    model_name = init_gemini()
    if not model_name:
        print("[Error] Cannot start without Gemini API")
        return
    
    # Check Vosk model
    if not os.path.exists(MODEL_DIR):
        print(f"\n[Error] Vosk model not found at {MODEL_DIR}")
        print("Download from: https://alphacephei.com/vosk/models")
        print("Recommended: vosk-model-small-en-us-0.15")
        return
    
    print(f"\n[Setup Complete]")
    print(f"  Mic Index: {RESPEAKER_INDEX}")
    print(f"  Sample Rate: {RESPEAKER_RATE} Hz")
    print(f"  Gemini Model: {model_name}")
    
    say("Voice assistant ready")
    print("\nListening... (Press Ctrl+C to stop)")
    
    try:
        while True:
            print("\n[Listening...]")
            text = listen_once(RESPEAKER_INDEX, RESPEAKER_RATE, seconds=3.0)
            
            if text:
                print(f"[You] {text}")
                print("[Thinking...]")
                
                response = gemini_response(text, model_name)
                print(f"[AI] {response}")
                
                say(response)
            else:
                print("[Silence detected]")
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        say("Goodbye")
    except Exception as e:
        print(f"\n[Error] {e}")
    finally:
        if mic_hw:
            try:
                mic_hw.close()
            except:
                pass

if __name__ == "__main__":
    main()
