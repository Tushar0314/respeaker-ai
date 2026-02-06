# 📍 Location & Waypoint Integration Guide

## Overview

Your Raspberry Pi voice assistant can now detect waypoints sent from your friend's React Native app and speak your location when you ask "where am I?" or simply "where".

## How It Works

### The Flow:

```
Friend's React Native App → BLE/ESP32 → Raspberry Pi → Voice Assistant
     (sends waypoints)     (receives)   (JSON files)   (speaks location)
```

1. **Friend's App** (React Native): Sends GPS waypoints via BLE to ESP32
2. **ESP32/BLE Device**: Receives waypoints and sends to Raspberry Pi
3. **Raspberry Pi**: Updates JSON files with waypoint data
4. **Voice Assistant**: Reads waypoints and speaks location when asked

---

## 🚀 Quick Start

### 1. Test the System (Without Hardware)

Run the waypoint receiver in test mode:

```bash
python3 waypoint_receiver.py test
```

This creates sample waypoint data. Then ask your voice assistant:
- "Where am I?"
- "Where?"
- "What's my location?"

### 2. Manual Input Mode

For testing with real data from the React Native app:

```bash
python3 waypoint_receiver.py manual
```

Then paste the waypoint data when prompted.

### 3. Automatic Mode (ESP32 Serial Connection)

If your ESP32 is connected via USB to the Pi:

```bash
python3 waypoint_receiver.py serial /dev/ttyUSB0
```

This continuously listens for waypoint data from the ESP32.

---

## 📱 React Native App Integration

### Data Format

The React Native app sends waypoints in this format:
```
WP1:37.788250,-122.432400;WP2:37.789000,-122.433000;WP3:37.790500,-122.434500
```

Each waypoint has:
- **Name**: WP1, WP2, WP3, etc.
- **Coordinates**: latitude,longitude

### JSON Files Created

#### `waypoints.json`
Stores all waypoints from your route:
```json
{
  "waypoints": [
    {
      "name": "WP1",
      "lat": 37.788250,
      "lon": -122.432400,
      "saved_at": "2025-01-29T10:30:00"
    },
    {
      "name": "WP2",
      "lat": 37.789000,
      "lon": -122.433000,
      "saved_at": "2025-01-29T10:30:00"
    }
  ],
  "last_updated": "2025-01-29T10:30:00"
}
```

#### `current_location.json`
Stores your current position (first waypoint):
```json
{
  "lat": 37.788250,
  "lon": -122.432400,
  "last_updated": "2025-01-29T10:30:00"
}
```

---

## 🗣️ Voice Commands

Ask your Pi any of these questions:

### Basic Location
- "Where am I?"
- "Where?"
- "What's my location?"
- "Tell me where I am"
- "Current location"

### Waypoint Specific
- "Where am I?" → "You are at waypoint WP1"
- "GPS coordinates" → Includes exact lat/lon
- "Show all waypoints" → Lists all waypoints in route

### Smart Responses

The assistant gives intelligent responses based on distance:

- **< 10 meters**: "You are at waypoint WP1"
- **< 50 meters**: "You are very close to waypoint WP1, about 30 meters away"
- **< 500 meters**: "You are near waypoint WP1, approximately 200 meters away"
- **> 500 meters**: "The nearest waypoint is WP1, about 1.2 kilometers away"

---

## 🔧 Enhanced Features

### Distance Calculation

The voice assistant now:
- Calculates distance to nearest waypoint using Haversine formula
- Provides natural language responses based on proximity
- Automatically finds the closest waypoint to your current position

### Multiple Waypoints

When you have multiple waypoints:
- First waypoint = Source/Starting point
- Last waypoint = Destination
- Middle waypoints = Route points

The assistant can:
- Tell you how many waypoints you have
- List all waypoints when asked
- Identify which waypoint is nearest

---

## 🛠️ Setup & Installation

### Prerequisites

Make sure you have these Python packages:
```bash
pip install pyserial  # For ESP32 serial communication (if using serial)
```

### File Structure

```
respeaker-ai/
├── hello_ai_pi_custom.py      # Main voice assistant (enhanced)
├── waypoint_receiver.py        # Receives waypoints from app
├── waypoints.json              # Stored waypoints
├── current_location.json       # Current position
└── LOCATION_WAYPOINT_GUIDE.md  # This guide
```

---

## 📡 ESP32 Integration Options

### Option 1: Serial via USB
ESP32 connected to Pi via USB cable:
```bash
python3 waypoint_receiver.py serial /dev/ttyUSB0
```

### Option 2: BLE Direct (Advanced)
For direct BLE communication between Pi and ESP32, you'll need:
- BLE library on Pi (bluepy or similar)
- ESP32 configured as BLE server
- Pi configured as BLE client

### Option 3: WiFi/Network
Send waypoint data via HTTP/MQTT from ESP32 to Pi.

---

## 🧪 Testing Workflow

### Complete Test Sequence:

1. **Generate Test Waypoints**:
   ```bash
   python3 waypoint_receiver.py test
   ```

2. **Start Voice Assistant**:
   ```bash
   python3 hello_ai_pi_custom.py
   ```

3. **Ask Questions**:
   - "Where am I?"
   - "What's my location?"
   - "Show all waypoints"

4. **Update with Real Data**:
   ```bash
   python3 waypoint_receiver.py manual
   # Paste: WP1:37.7749,-122.4194;WP2:37.7750,-122.4195
   ```

5. **Ask Again**:
   Voice assistant will speak the new waypoints!

---

## 🔍 Troubleshooting

### "I cannot find the location right now"

**Possible causes:**
- No `waypoints.json` file exists
- No `current_location.json` file exists
- JSON files are empty or corrupted
- No internet connection (for Google Maps API fallback)

**Solutions:**
```bash
# Check if files exist
ls -l waypoints.json current_location.json

# View file contents
cat waypoints.json
cat current_location.json

# Recreate with test data
python3 waypoint_receiver.py test
```

### Serial Port Not Found

**Error:** `Serial connection failed: [Errno 2] No such file or directory: '/dev/ttyUSB0'`

**Solutions:**
```bash
# List available serial ports
ls /dev/tty*

# Common ESP32 ports:
# - /dev/ttyUSB0
# - /dev/ttyACM0
# - /dev/serial0

# Check ESP32 is connected
dmesg | grep tty
```

### Waypoint Data Not Parsing

**Check the format:**
- Must be: `WP1:lat,lon;WP2:lat,lon`
- Latitude: -90 to 90
- Longitude: -180 to 180
- Separated by semicolons (`;`)

---

## 📊 Data Format Reference

### React Native App Output
```
WP1:37.788250,-122.432400;WP2:37.789000,-122.433000;WP3:37.790500,-122.434500
```

### Base64 Encoded (from BLE)
```
V1AxOjM3Ljc4ODI1MCwtMTIyLjQzMjQwMDtXUDI6MzcuNzg5MDAwLC0xMjIuNDMzMDAwO1dQMzozNy43OTA1MDAsLTEyMi40MzQ1MDA=
```

The waypoint receiver automatically detects and decodes base64 data.

---

## 🎯 Example Conversations

### Example 1: Simple Query
**You:** "Where am I?"  
**Pi:** "You are at waypoint WP1. You have 3 waypoints in your route."

### Example 2: Detailed Location
**You:** "GPS coordinates"  
**Pi:** "You are at waypoint WP1. Coordinates: latitude 37.7883, longitude -122.4324."

### Example 3: Route Information
**You:** "Show all waypoints"  
**Pi:** "You are at waypoint WP1. You have 3 waypoints in your route. Your waypoints are: WP1, WP2, WP3."

### Example 4: Distance Check
**You:** "Where?"  
**Pi:** "You are very close to waypoint WP2, about 45 meters away. You have 3 waypoints in your route."

---

## 🚢 Integration with Friend's App

### Your Friend's App Must:

1. **Send GPS waypoints** via BLE to ESP32
2. **Use the correct format**: `WP1:lat,lon;WP2:lat,lon;...`
3. **Update regularly** so Pi knows current position

### On the Raspberry Pi:

1. **Receive waypoints** from ESP32 (via serial/BLE/WiFi)
2. **Update JSON files** with `waypoint_receiver.py`
3. **Voice assistant reads** waypoints automatically

### Workflow:

```
[Friend's Phone]
      ↓ (BLE)
  [ESP32 on Boat]
      ↓ (Serial/WiFi)
[Raspberry Pi]
      ↓ (Reads JSON)
 [Voice Assistant]
      ↓ (Speaks)
   "You are at WP1"
```

---

## 💡 Tips & Best Practices

### Auto-Start Waypoint Receiver

To automatically start the receiver when Pi boots:

```bash
# Edit crontab
crontab -e

# Add line:
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 waypoint_receiver.py serial /dev/ttyUSB0 >> waypoint.log 2>&1
```

### Periodic Updates

For real-time position tracking, update `current_location.json` frequently (every few seconds) with the latest GPS position from your friend's app.

### Battery Considerations

On a boat with limited power:
- Use lower update frequency (every 10-30 seconds)
- Turn off BLE scanning when not needed
- Use sleep mode between waypoints

---

## 📝 Summary

You now have:

✅ **Voice assistant** that speaks waypoint locations  
✅ **Smart distance calculation** to nearest waypoint  
✅ **Natural language responses** based on proximity  
✅ **Multiple ways to ask** about location  
✅ **Easy testing** with sample data  
✅ **Integration ready** for React Native app  

**Just ask your Pi "where am I?" and it will tell you your location based on the waypoints sent from your friend's app!** 🎉
