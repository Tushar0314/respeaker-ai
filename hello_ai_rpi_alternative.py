#!/usr/bin/env python3
"""
Voice Assistant for Raspberry Pi 3 with ReSpeaker Microphone Array
ALTERNATIVE VERSION - Uses speech_recognition instead of Vosk
Works with any Python version on Raspberry Pi
"""

import queue
import sounddevice as sd
import speech_recognition as sr
import os
import subprocess
import google.generativeai as genai

# Configuration
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'

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

def tts_espeak(text):
    """Use espeak for text-to-speech on Raspberry Pi (lightweight)."""
    try:
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

def say(text):
    """Speak text using available TTS engine."""
    print(f"[TTS] -> {text}")
    tts_espeak(text)

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

def listen_once(mic_index, seconds=3.0):
    """Capture audio and return recognized text using speech_recognition."""
    recognizer = sr.Recognizer()
    
    try:
        # Use sounddevice to capture audio
        print(f"[Listening for {seconds} seconds...]")
        audio_data = sd.rec(int(seconds * RESPEAKER_RATE), 
                           samplerate=RESPEAKER_RATE, 
                           channels=RESPEAKER_CHANNELS,
                           dtype='int16',
                           device=mic_index)
        sd.wait()
        
        # Convert to AudioData format for speech_recognition
        audio = sr.AudioData(audio_data.tobytes(), RESPEAKER_RATE, 2)
        
        # Use Google Speech Recognition (free, no API key needed)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return ""  # Silence or couldn't understand
        except sr.RequestError as e:
            print(f"[ASR Error] {e}")
            return ""
            
    except Exception as e:
        print(f"[Audio Error] {e}")
        return ""

def main():
    print("=" * 50)
    print("Voice Assistant for Raspberry Pi + ReSpeaker")
    print("(Alternative Version - No Vosk Required)")
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
    
    # Initialize Gemini
    model_name = init_gemini()
    if not model_name:
        print("[Error] Cannot start without Gemini API")
        return
    
    print(f"\n[Setup Complete]")
    print(f"  Mic Index: {RESPEAKER_INDEX}")
    print(f"  Sample Rate: {RESPEAKER_RATE} Hz")
    print(f"  Gemini Model: {model_name}")
    print(f"  Speech Recognition: Google Speech API")
    
    say("Voice assistant ready")
    print("\nListening... (Press Ctrl+C to stop)")
    
    try:
        while True:
            print("\n[Listening...]")
            text = listen_once(RESPEAKER_INDEX, seconds=3.0)
            
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

if __name__ == "__main__":
    main()
