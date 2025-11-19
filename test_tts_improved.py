#!/usr/bin/env python3
"""Improved TTS test with explicit voice selection"""
import pyttsx3
import subprocess

print("=== Audio Output Test ===")

# Check current audio output using system command
print("\nChecking audio output device...")
try:
    result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                          capture_output=True, text=True, timeout=5)
    print("Audio devices detected.")
except:
    print("Could not check audio devices")

# Initialize TTS
print("\nInitializing text-to-speech...")
engine = pyttsx3.init('nsss')  # Use macOS native speech synthesis

# List voices and select a clear English one
voices = engine.getProperty('voices')
print(f"Found {len(voices)} voices")

# Try to find a good English voice
preferred_voices = ['Samantha', 'Alex', 'Victoria', 'Karen', 'Daniel']
selected_voice = None

for pref in preferred_voices:
    for voice in voices:
        if pref in voice.name:
            selected_voice = voice.id
            print(f"Selected voice: {voice.name}")
            break
    if selected_voice:
        break

if not selected_voice:
    # Use first available voice
    selected_voice = voices[0].id
    print(f"Using default voice: {voices[0].name}")

engine.setProperty('voice', selected_voice)
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Test with a very clear message
print("\n🔊 TURN UP YOUR SPEAKERS NOW!")
print("Speaking test message in 2 seconds...")
import time
time.sleep(2)

test_messages = [
    "Testing. One. Two. Three.",
    "Can you hear me now?",
    "This is the Gemini voice assistant speaking."
]

for i, msg in enumerate(test_messages, 1):
    print(f"\n[Test {i}] {msg}")
    engine.say(msg)
    engine.runAndWait()
    time.sleep(0.5)

print("\n✓ Test complete!")
print("\nIf you didn't hear anything:")
print("1. Check your Mac's volume slider (should be at least 50%)")
print("2. Go to System Settings > Sound > Output")
print("3. Make sure 'MacBook Pro Speakers' or external speakers are selected")
print("4. Try saying 'test' to the hello_ai.py and listen carefully")
