#!/usr/bin/env python3
"""Test TTS audio output on macOS"""
import pyttsx3

print("Testing pyttsx3 text-to-speech on macOS...")
print("Make sure your Mac's volume is turned UP!")

# Initialize engine
engine = pyttsx3.init()

# Get available voices
voices = engine.getProperty('voices')
print(f"\nAvailable voices: {len(voices)}")
for i, voice in enumerate(voices[:5]):  # Show first 5
    print(f"  {i}: {voice.name}")

# Set properties
engine.setProperty('rate', 150)     # Speed of speech
engine.setProperty('volume', 1.0)   # Volume (0.0 to 1.0)

# Test speech
print("\n[TEST 1] Speaking with default voice...")
engine.say("Hello! This is a test of text to speech. Can you hear me?")
engine.runAndWait()

print("\n[TEST 2] Speaking a longer sentence...")
engine.say("If you can hear this, then text to speech is working correctly on your Mac.")
engine.runAndWait()

print("\n[TEST 3] Speaking with increased volume...")
engine.setProperty('volume', 1.0)
engine.say("Testing maximum volume. This should be loud and clear.")
engine.runAndWait()

print("\n✓ TTS test complete!")
print("Did you hear the voice? If not, check your Mac's sound settings.")
