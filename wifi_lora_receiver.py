#!/usr/bin/env python3
"""
WiFi LoRa Message Receiver - Pi Side
Receives messages from friend's ESP32 via MQTT over WiFi and speaks them.

Flow:
  Friend presses "hold" button on ESP32
      → ESP32 publishes "hold" to MQTT topic
      → Pi receives it
      → Pi speaks "hold" via espeak
"""

import subprocess
import time
import sys
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("[ERROR] paho-mqtt not installed.")
    print("Install it with:  pip3 install paho-mqtt")
    sys.exit(1)

# ─────────────────────────────────────────
# CONFIGURATION — Edit these to match your friend's setup
# ─────────────────────────────────────────
MQTT_BROKER   = "192.168.1.100"   # IP address of MQTT broker (ask your friend)
MQTT_PORT     = 1883               # Default MQTT port
MQTT_TOPIC    = "lora/commands"    # Topic your friend's ESP32 publishes to
MQTT_USERNAME = ""                 # Leave empty if no username
MQTT_PASSWORD = ""                 # Leave empty if no password

# TTS (espeak) Settings
VOICE   = "en"   # en, en-us, en-gb
SPEED   = 150    # Words per minute (80-450)
PITCH   = 50     # Voice pitch (0-99)
VOLUME  = 150    # Volume (0-200)
# ─────────────────────────────────────────


def speak(text):
    """Speak text using espeak."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🔊 SPEAKING: \"{text}\"")

    try:
        subprocess.run(
            ['espeak', '-v', VOICE, '-s', str(SPEED), '-p', str(PITCH), '-a', str(VOLUME), text],
            check=True
        )
    except FileNotFoundError:
        print("[ERROR] espeak not found. Install with:  sudo apt-get install espeak")
    except Exception as e:
        print(f"[ERROR] speak failed: {e}")


def on_connect(client, userdata, flags, rc):
    """Called when Pi connects to MQTT broker."""
    if rc == 0:
        print(f"[✓] Connected to MQTT broker at {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"[✓] Subscribed to topic: '{MQTT_TOPIC}'")
        print(f"\n[WAITING] Listening for messages from friend's ESP32...")
        print("[Press Ctrl+C to stop]\n")
    else:
        codes = {
            1: "Wrong protocol version",
            2: "Invalid client ID",
            3: "Broker unavailable",
            4: "Wrong username/password",
            5: "Not authorized"
        }
        print(f"[ERROR] Connection failed: {codes.get(rc, f'Code {rc}')}")


def on_message(client, userdata, msg):
    """Called when a message arrives from ESP32."""
    raw = msg.payload.decode('utf-8').strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*50}")
    print(f"[{timestamp}] Message received!")
    print(f"[Topic]   {msg.topic}")
    print(f"[Message] {raw}")
    print(f"{'='*50}")

    if raw:
        speak(raw)


def on_disconnect(client, userdata, rc):
    """Called when disconnected."""
    if rc != 0:
        print(f"\n[WARNING] Unexpectedly disconnected. Reconnecting...")


def main():
    print("=" * 55)
    print("📡 WiFi LoRa Receiver — Pi Side")
    print("   Friend's ESP32 → MQTT → Pi → 🔊 Speaker")
    print("=" * 55)
    print(f"\nBroker : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic  sss : {MQTT_TOPIC}\n")

    # Setup MQTT client
    client = mqtt.Client()

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    # Connect
    try:
        print(f"[Connecting to {MQTT_BROKER}...]")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"\n[ERROR] Could not connect to broker: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure Pi and ESP32 are on the same WiFi")
        print(f"  2. Check broker IP — update MQTT_BROKER in this file")
        print("  3. If using phone hotspot, find broker IP with:  hostname -I")
        sys.exit(1)

    # Start listening loop
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n[✓] Stopped.")
        client.disconnect()


if __name__ == "__main__":
    main()
