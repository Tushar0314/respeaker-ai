# 🗺️ Voice-Activated Waypoint Navigation System

## Overview

Your Raspberry Pi voice assistant can now **speak your location** based on GPS waypoints sent from your friend's React Native app! Just ask **"Where am I?"** or **"Where?"** and get instant location feedback.

---

## 🎯 What's New

### Enhanced Features:
✅ **Waypoint Detection** - Reads GPS waypoints from React Native app  
✅ **Distance Calculation** - Calculates distance to nearest waypoint  
✅ **Smart Responses** - Natural language based on proximity  
✅ **Multiple Waypoints** - Handles entire navigation routes  
✅ **Voice Commands** - Many ways to ask about location  

### New Files Created:
1. **`waypoint_receiver.py`** - Receives waypoints from app/ESP32
2. **`LOCATION_WAYPOINT_GUIDE.md`** - Complete documentation
3. **`QUICK_START_LOCATION.md`** - Quick start guide
4. **`SYSTEM_DIAGRAM.txt`** - Visual system architecture
5. **Enhanced `hello_ai_pi_custom.py`** - Voice assistant with waypoint support

---

## 🚀 Quick Start (30 Seconds)

### 1. Test with Sample Data
```bash
cd /Users/tusharbhaliya/Desktop/AI/respeaker-ai
python3 waypoint_receiver.py test
```

### 2. Run Voice Assistant
```bash
python3 hello_ai_pi_custom.py
```

### 3. Ask Your Question
🗣️ **"Where am I?"**

### 4. Hear the Response
🔊 **"You are at waypoint WP1. You have 3 waypoints in your route."**

---

## 📱 Integration with Friend's React Native App

### The Complete Flow:

```
[Friend's Phone App]
        ↓ (BLE)
    [ESP32 Device]
        ↓ (Serial/WiFi)
  [Raspberry Pi]
        ↓ (JSON Files)
  [Voice Assistant]
        ↓ (Speech)
   "You are at WP1"
```

### How It Works:

1. **Friend's App** (https://github.com/BhavenChheda790/React-Native-App):
   - Shows map interface
   - User taps to add waypoints
   - Sends via BLE: `WP1:lat,lon;WP2:lat,lon;WP3:lat,lon`

2. **ESP32/BLE Device**:
   - Receives waypoint data via BLE
   - Forwards to Raspberry Pi via Serial/WiFi

3. **Waypoint Receiver** (`waypoint_receiver.py`):
   - Listens for incoming data
   - Parses waypoint format
   - Updates JSON files

4. **Voice Assistant** (`hello_ai_pi_custom.py`):
   - Reads `waypoints.json` and `current_location.json`
   - Calculates distance to nearest waypoint
   - Speaks location when asked

---

## 🎤 Voice Commands

Ask your Pi any of these:

| Command | Response |
|---------|----------|
| "Where am I?" | Current waypoint location |
| "Where?" | Same as above (shortest!) |
| "What's my location?" | Current position |
| "GPS coordinates" | Includes exact lat/lon |
| "Show all waypoints" | Lists all route waypoints |
| "Current location" | Your position |
| "Waypoint" | Waypoint information |
| "Destination" | Final waypoint |

---

## 📡 Setup Options

### Option 1: Test Mode (No Hardware)
Perfect for testing without ESP32 or React Native app:
```bash
python3 waypoint_receiver.py test
```
Creates sample waypoints instantly.

### Option 2: Manual Input
For testing with real data from the app:
```bash
python3 waypoint_receiver.py manual
# Paste: WP1:37.7749,-122.4194;WP2:37.7750,-122.4195
```

### Option 3: Serial from ESP32 (Recommended)
ESP32 connected to Pi via USB:
```bash
python3 waypoint_receiver.py serial /dev/ttyUSB0
```
Leave running in background to continuously receive updates.

---

## 📊 Data Format

### From React Native App:
```
WP1:37.788250,-122.432400;WP2:37.789000,-122.433000;WP3:37.790500,-122.434500
```

### Stored in `waypoints.json`:
```json
{
  "waypoints": [
    {
      "name": "WP1",
      "lat": 37.788250,
      "lon": -122.432400,
      "saved_at": "2026-01-29T10:30:00"
    }
  ],
  "last_updated": "2026-01-29T10:30:00"
}
```

### Stored in `current_location.json`:
```json
{
  "lat": 37.788250,
  "lon": -122.432400,
  "last_updated": "2026-01-29T10:30:00"
}
```

---

## 🧠 Smart Distance Responses

The voice assistant calculates distance and responds naturally:

- **< 10 meters**: "You are at waypoint WP1"
- **< 50 meters**: "Very close to WP1, about 30 meters away"
- **< 500 meters**: "Near WP1, approximately 200 meters away"
- **> 500 meters**: "Nearest waypoint is WP1, about 1.2 kilometers away"

Uses **Haversine formula** for accurate GPS distance calculation.

---

## 🗂️ File Structure

```
respeaker-ai/
├── hello_ai_pi_custom.py          # Voice assistant (ENHANCED)
├── waypoint_receiver.py            # Waypoint receiver (NEW)
├── waypoints.json                  # Waypoint storage (AUTO-CREATED)
├── current_location.json           # Current position (AUTO-CREATED)
├── LOCATION_WAYPOINT_GUIDE.md     # Full documentation (NEW)
├── QUICK_START_LOCATION.md        # Quick start guide (NEW)
├── SYSTEM_DIAGRAM.txt             # System diagram (NEW)
└── README_WAYPOINT_INTEGRATION.md # This file (NEW)
```

---

## 🔧 Code Enhancements

### In `hello_ai_pi_custom.py`:

1. **Added `calculate_distance()` function**:
   - Haversine formula for GPS distance
   - Accurate for navigation

2. **Enhanced `get_waypoint_location()` function**:
   - Reads from both `waypoints.json` and `current_location.json`
   - Finds nearest waypoint based on current position
   - Returns distance information

3. **Improved `handle_location_query()` function**:
   - More natural language patterns
   - Distance-based responses
   - Support for multiple waypoints

### New `waypoint_receiver.py`:

1. **`parse_waypoint_data()`** - Parses app data format
2. **`save_waypoints()`** - Updates JSON files
3. **`listen_for_waypoints_serial()`** - Serial port listener
4. **`manual_input()`** - Manual testing mode
5. **`test_with_sample_data()`** - Quick testing

---

## 🎓 Example Conversations

### Example 1: At Waypoint
```
You: "Where am I?"
Pi:  "You are at waypoint WP1. You have 3 waypoints in your route."
```

### Example 2: Near Waypoint
```
You: "Where?"
Pi:  "You are very close to waypoint WP2, about 35 meters away. 
      You have 3 waypoints in your route."
```

### Example 3: With Coordinates
```
You: "GPS coordinates"
Pi:  "You are at waypoint WP1. Coordinates: latitude 37.7883, 
      longitude -122.4324."
```

### Example 4: List All Waypoints
```
You: "Show all waypoints"
Pi:  "You are at waypoint WP1. You have 3 waypoints in your route. 
      Your waypoints are: WP1, WP2, WP3."
```

---

## 🛠️ Troubleshooting

### Problem: "I cannot find the location right now"

**Cause:** No waypoint data available

**Solution:**
```bash
python3 waypoint_receiver.py test
```

### Problem: Waypoint receiver not receiving data

**Check:**
- ESP32 connected via USB? (`ls /dev/tty*`)
- Correct serial port? (try `/dev/ttyUSB0`, `/dev/ttyACM0`)
- React Native app sending data? (check ESP32 logs)

**Solution:**
```bash
# Find correct port
ls -l /dev/tty* | grep USB

# Use correct port
python3 waypoint_receiver.py serial /dev/ttyACM0
```

### Problem: Voice assistant not responding

**Check:**
- ReSpeaker microphone detected?
- Speaking clearly and loud enough?
- Vosk model installed?

**Solution:**
```bash
# Test microphone
arecord -l

# Restart voice assistant
python3 hello_ai_pi_custom.py
```

---

## 🚢 Use Case: Boat Navigation

Perfect for sailing/boating with GPS waypoints:

1. **Before Departure:**
   - Friend plans route on React Native app
   - Sets waypoints for navigation
   - Sends to your Pi via BLE/ESP32

2. **During Voyage:**
   - Ask "Where am I?" anytime
   - Get instant position feedback
   - Hands-free navigation updates

3. **Benefits:**
   - No need to look at screens
   - Voice-controlled route tracking
   - Works while sailing/fishing
   - Battery efficient

---

## ⚙️ Advanced: Auto-Start on Boot

To automatically start waypoint receiver when Pi boots:

```bash
# Edit crontab
crontab -e

# Add this line:
@reboot sleep 30 && cd /Users/tusharbhaliya/Desktop/AI/respeaker-ai && python3 waypoint_receiver.py serial /dev/ttyUSB0 >> waypoint.log 2>&1
```

---

## 📚 Documentation

- **`QUICK_START_LOCATION.md`** - Quick start guide
- **`LOCATION_WAYPOINT_GUIDE.md`** - Comprehensive documentation
- **`SYSTEM_DIAGRAM.txt`** - Visual architecture
- **Friend's App**: https://github.com/BhavenChheda790/React-Native-App

---

## 🎉 Summary

You now have:

✅ **Voice-activated location system**  
✅ **Integration with React Native app**  
✅ **Smart distance calculation**  
✅ **Natural language responses**  
✅ **Multiple waypoint support**  
✅ **Easy testing without hardware**  

**Just ask "Where am I?" and navigate with confidence!** 🗺️⛵

---

## 🔗 Links

- **React Native App**: https://github.com/BhavenChheda790/React-Native-App
- **BLE Protocol**: Service UUID `12345678-1234-1234-1234-1234567890ab`
- **Data Format**: `WP1:lat,lon;WP2:lat,lon;WP3:lat,lon`

---

**Happy navigating! 🧭**
