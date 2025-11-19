#!/usr/bin/env python3
"""
ReSpeaker 4-Mic Array Detection and Calibration Test
Run this on Raspberry Pi to verify your setup
"""

import sounddevice as sd
import subprocess
import sys

print("\n" + "=" * 70)
print("🎤 ReSpeaker 4-Mic Array - Detection & Calibration Test")
print("=" * 70)

# Step 1: List all audio devices
print("\n[STEP 1] Audio Devices Detected:")
print("-" * 70)
devices = sd.query_devices()

mic_devices = []
speaker_devices = []

for idx, device in enumerate(devices):
    in_ch = device.get('max_input_channels', 0)
    out_ch = device.get('max_output_channels', 0)
    sr = device.get('default_samplerate', 'N/A')
    
    device_type = []
    if in_ch > 0:
        device_type.append(f"IN({in_ch}ch)")
        mic_devices.append((idx, device['name']))
    if out_ch > 0:
        device_type.append(f"OUT({out_ch}ch)")
        speaker_devices.append((idx, device['name']))
    
    if device_type:
        print(f"[{idx}] {device['name']:<40} {', '.join(device_type):<20} SR: {sr}")

# Step 2: Identify ReSpeaker
print("\n[STEP 2] ReSpeaker Detection:")
print("-" * 70)

respeaker_idx = None
for idx, name in mic_devices:
    if any(keyword in name.lower() for keyword in ['respeaker', 'seeed', 'usb audio']):
        print(f"✓ ReSpeaker found at device index: {idx}")
        print(f"  Device name: {name}")
        respeaker_idx = idx
        break

if respeaker_idx is None:
    print("⚠ ReSpeaker not auto-detected")
    print("  Available microphones:")
    for idx, name in mic_devices:
        print(f"    [{idx}] {name}")
    print("\n  If you see 'USB Audio Device' or similar, that's your ReSpeaker!")

# Step 3: Identify Speaker
print("\n[STEP 3] Speaker Detection:")
print("-" * 70)

speaker_idx = None
for idx, name in speaker_devices:
    print(f"  [{idx}] {name}")
    if speaker_idx is None:
        speaker_idx = idx
        print(f"      ^ Will use this as default speaker")

# Step 4: Check espeak (for text-to-speech)
print("\n[STEP 4] Text-to-Speech Setup:")
print("-" * 70)

try:
    result = subprocess.run(['which', 'espeak'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ espeak found at: {result.stdout.strip()}")
        print("  (Lightweight TTS for Raspberry Pi)")
    else:
        print("✗ espeak not found")
        print("  Install with: sudo apt-get install espeak")
except Exception as e:
    print(f"✗ Could not check espeak: {e}")

# Step 5: Test microphone
print("\n[STEP 5] Microphone Test:")
print("-" * 70)

if respeaker_idx is not None:
    print(f"Testing microphone at device {respeaker_idx}...")
    print("Speak something for 3 seconds...")
    
    try:
        import numpy as np
        
        def test_mic():
            duration = 3  # seconds
            fs = 16000
            print(f"Recording {duration} seconds...")
            
            try:
                audio = sd.rec(int(fs * duration), samplerate=fs, channels=1, 
                              device=respeaker_idx, dtype='int16')
                sd.wait()
                
                # Calculate volume
                volume = np.abs(audio).mean()
                peak = np.abs(audio).max()
                
                print(f"\n✓ Recording successful!")
                print(f"  Average volume: {volume:.0f}")
                print(f"  Peak volume: {peak:.0f}")
                
                if volume > 100:
                    print(f"  ✓ Good microphone level detected")
                else:
                    print(f"  ⚠ Low microphone level (check microphone placement)")
                
                return True
            except Exception as e:
                print(f"✗ Recording error: {e}")
                return False
        
        if test_mic():
            print("\nTesting speaker output...")
            try:
                subprocess.run(['espeak', '-s', '150', 'Microphone test successful'],
                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✓ Speaker test completed")
            except:
                print("⚠ Could not test speaker (espeak not available)")
    
    except ImportError:
        print("⚠ numpy not found, skipping detailed microphone test")
else:
    print("⚠ ReSpeaker not detected, skipping microphone test")

# Step 6: Summary
print("\n[SUMMARY]")
print("-" * 70)

print("\n✓ Your Setup:")
if respeaker_idx is not None:
    print(f"  Microphone: ReSpeaker at device index {respeaker_idx}")
else:
    print(f"  Microphone: NOT DETECTED (you'll be asked to select manually)")

if speaker_idx is not None:
    print(f"  Speaker: Device index {speaker_idx}")
else:
    print(f"  Speaker: Not detected")

print("\n📝 Next Steps:")
print("  1. Make sure your ReSpeaker is connected to Raspberry Pi")
print("  2. Connect your JBL speaker to Raspberry Pi's audio jack")
print("  3. Run the voice assistant:")
print("\n    source venv/bin/activate")
print("    python3 hello_ai_pi_custom.py")

print("\n" + "=" * 70 + "\n")
