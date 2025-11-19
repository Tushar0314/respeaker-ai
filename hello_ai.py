import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'  # <-- Your new Gemini API key
import math
import os
import google.generativeai as genai
import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

import math
import os
import google.generativeai as genai

# Install the google-generativeai package
os.system('pip install google-generativeai')

# List devices and prompt user for MIC_INDEX before using it
print("\n=== Available audio devices ===")
devices = sd.query_devices()
for idx, d in enumerate(devices):
    io = []
    if d['max_input_channels'] > 0: io.append('IN')
    if d['max_output_channels'] > 0: io.append('OUT')
    print(f"{idx}: {d['name']} [{', '.join(io)}], max_in={d['max_input_channels']}, max_out={d['max_output_channels']}, default SR={d.get('default_samplerate')}")
print("===============================\n")
try:
    MIC_INDEX = int(input("Enter the index of your laptop's microphone (IN): "))
except Exception:
    print("Invalid input. Exiting.")
    exit(1)


# ---- auto-detect a supported sample rate from the device ----
def pick_samplerate(device_index):
    info = sd.query_devices(device_index, 'input')
    # round to integer Hz (e.g., 48000.0 -> 48000)
    sr = int(round(info.get('default_samplerate', 48000)))
    # sanity clamp
    if sr < 8000 or sr > 192000:
        sr = 48000
    return sr

RATE = pick_samplerate(MIC_INDEX)   # likely 48000 on Windows
MODEL_DIR = "models/en"

# IMPORTANT: recognizer rate must match what we capture at
model = Model(MODEL_DIR)
rec = KaldiRecognizer(model, RATE)

tts = pyttsx3.init()

# List available voices and use the first one
voices = tts.getProperty('voices')
if voices:
    print(f"[TTS] Available voices: {len(voices)}")
    tts.setProperty('voice', voices[0].id)  # Use first voice
    
# Increase TTS volume to maximum
tts.setProperty('volume', 1.0)  # Volume range is 0.0 to 1.0
# Optionally adjust speech rate (default is 200, lower is slower)
tts.setProperty('rate', 150)

# Test TTS at startup
print("[TTS Test] Testing text-to-speech...")
print("[TTS Test] TURN UP YOUR SPEAKER VOLUME NOW!")
tts.say("Text to speech is working. Can you hear me?")
tts.runAndWait()
print("[TTS Test] If you heard that, TTS is working correctly.")

genai.configure(api_key=GEMINI_API_KEY)


# List available Gemini models for this API key (after genai is imported and configured)
print("\n=== Gemini models available to your API key ===")
try:
    available_models = list(genai.list_models())
    for m in available_models:
        print(m.name)
    
    # Pick a stable model with good quota (prefer gemini-2.0-flash or similar)
    GEMINI_MODEL_NAME = None
    preferred_models = [
        'models/gemini-2.0-flash',
        'models/gemini-2.5-flash',
        'models/gemini-flash-latest',
        'models/gemini-2.0-flash-001',
        'models/gemini-2.5-flash-lite'
    ]
    
    # First try preferred models
    for preferred in preferred_models:
        for m in available_models:
            if m.name == preferred and hasattr(m, 'supported_generation_methods') and 'generateContent' in getattr(m, 'supported_generation_methods', []):
                GEMINI_MODEL_NAME = m.name
                break
        if GEMINI_MODEL_NAME:
            break
    
    # If no preferred model found, pick the first that supports generateContent
    if not GEMINI_MODEL_NAME:
        for m in available_models:
            if hasattr(m, 'supported_generation_methods') and 'generateContent' in getattr(m, 'supported_generation_methods', []):
                GEMINI_MODEL_NAME = m.name
                break
    
    if not GEMINI_MODEL_NAME:
        print("[Gemini Model List Error] No model with generateContent support found.")
    else:
        print(f"[Using Gemini Model] {GEMINI_MODEL_NAME}")
except Exception as e:
    print(f"[Gemini Model List Error] {e}")
    GEMINI_MODEL_NAME = None
print("==============================================\n")

def gemini_response(prompt):
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-gemini-api-key-here':
        return "No Gemini API key set. Please set GEMINI_API_KEY."
    if not GEMINI_MODEL_NAME:
        return "No Gemini model available. Please check your API key and project."
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Error] {e}"

def say(text: str):
    """Speak text using TTS with error handling and reinitialization."""
    print(f"[TTS] -> {text}")
    
    # Try macOS native 'say' command first (most reliable on Mac)
    try:
        import subprocess
        import shlex
        print("[TTS] Using macOS native 'say' command...")
        # Escape the text properly for shell
        subprocess.run(['say', text], check=True, timeout=30)
        print("[TTS] Finished speaking via macOS say.")
        return
    except Exception as e:
        print(f"[TTS] macOS say failed: {e}, falling back to pyttsx3...")
    
    # Fallback to pyttsx3
    try:
        # Reinitialize TTS engine for each call to avoid issues
        tts_engine = pyttsx3.init('nsss')  # Use macOS native speech synthesis
        tts_engine.setProperty('volume', 1.0)
        tts_engine.setProperty('rate', 150)
        
        # Split long text into shorter chunks to avoid issues
        max_length = 200
        if len(text) > max_length:
            # Split by sentences or chunks
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            for chunk in chunks:
                print(f"[TTS Chunk] Speaking: {chunk[:50]}...")
                tts_engine.say(chunk)
                tts_engine.runAndWait()
        else:
            tts_engine.say(text)
            tts_engine.runAndWait()
        
        print("[TTS] Finished speaking.")
    except Exception as e:
        print(f"[TTS Error] {e}")
        print("[TTS] Trying fallback...")
        try:
            # Fallback: just try once more with a fresh engine
            tts_engine = pyttsx3.init()
            tts_engine.say(text[:200])  # Only first 200 chars
            tts_engine.runAndWait()
        except:
            print("[TTS] Complete failure. Text not spoken.")

def listen_once(seconds=2.5):
    """Capture ~seconds of audio, return recognized text string."""
    q = queue.Queue()
    def cb(indata, frames, time, status):
        # indata is int16 raw bytes; push to queue
        q.put(bytes(indata))

    rec.Reset()
    frames_needed = int(RATE * seconds)
    got = 0

    # smaller blocksize reduces latency; mono channel; int16 for Vosk
    with sd.RawInputStream(device=MIC_INDEX, samplerate=RATE, blocksize=1024,
                           dtype='int16', channels=1, callback=cb):
        while got < frames_needed:
            buf = q.get()
            got += len(buf) // 2  # bytes -> samples (2 bytes per int16)
            # feed chunks to recognizer
            if rec.AcceptWaveform(buf):
                break

    res = json.loads(rec.FinalResult())
    return (res.get("text") or "").strip()

def main():
    print("\n=== Available audio devices ===")
    import sounddevice as sd
    devices = sd.query_devices()
    for idx, d in enumerate(devices):
        io = []
        if d['max_input_channels'] > 0: io.append('IN')
        if d['max_output_channels'] > 0: io.append('OUT')
        print(f"{idx}: {d['name']} [{', '.join(io)}], max_in={d['max_input_channels']}, max_out={d['max_output_channels']}, default SR={d.get('default_samplerate')}")
    print(f"Mic device index: {MIC_INDEX}, using sample rate: {RATE} Hz")
    say("Ready")
    print("Say something to chat with the AI (Gemini). Press Ctrl+C to stop.")
    while True:
        text = listen_once(2.5)
        print(f"[ASR] '{text}'")
        if not text:
            continue
        print("[DEBUG] Sending to Gemini...")
        ai_reply = gemini_response(text)
        print(f"[Gemini] {ai_reply}")
        say(ai_reply)
        print("[DEBUG] Finished speaking Gemini reply.")

if __name__ == "__main__":
    try:
        main()``
    except KeyboardInterrupt:          
        print("\nExiting.")
