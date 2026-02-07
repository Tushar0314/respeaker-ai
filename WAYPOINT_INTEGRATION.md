# Waypoint Integration Setup

## Complete System Flow:

### 1. Friend's React Native App → Raspberry Pi

**In your friend's React Native app, add this code:**

```javascript
// Function to send waypoint to Raspberry Pi
const sendWaypointToPi = async (latitude, longitude, waypointNumber) => {
  try {
    const waypointName = `WP${waypointNumber}`;
    const piIpAddress = '192.168.43.1'; // Pi's IP on hotspot
    
    const response = await fetch(`http://${piIpAddress}:5001/waypoint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        waypoints: `${waypointName}:${latitude},${longitude}`
      }),
    });
    
    if (response.ok) {
      console.log('✅ Waypoint sent to Pi');
    } else {
      console.error('❌ Pi did not respond');
    }
  } catch (error) {
    console.error('Connection failed:', error);
  }
};

// Call this when user marks a waypoint:
// sendWaypointToPi(37.7749, -122.4194, 1);
```

**Where to add it in friend's app:**
- Find where they get GPS coordinates
- Find their "Save Waypoint" or similar button
- Call `sendWaypointToPi(lat, lon, wpNumber)` there

---

### 2. Raspberry Pi Setup

**On your Raspberry Pi, you need TWO programs running:**

#### Program 1: Flask Server (Receives Waypoints)
File: `waypoint_receiver.py`

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import threading

app = Flask(__name__)
CORS(app)

waypoints_data = {"waypoints": [], "last_updated": None}

@app.route('/waypoint', methods=['POST'])
def receive_waypoint():
    try:
        data = request.json
        waypoint_string = data.get('waypoints', '')
        
        print(f"\n📍 RECEIVED WAYPOINT: {waypoint_string}")
        
        # Parse waypoints
        waypoints = []
        for wp in waypoint_string.split(';'):
            if ':' in wp:
                name, coords = wp.split(':')
                lat, lon = coords.split(',')
                waypoints.append({
                    'name': name,
                    'lat': float(lat),
                    'lon': float(lon)
                })
        
        waypoints_data['waypoints'] = waypoints
        waypoints_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open('waypoints.json', 'w') as f:
            json.dump(waypoints_data, f, indent=2)
        
        print(f"✅ Saved {len(waypoints)} waypoints")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

def run_server():
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    print("🚀 Waypoint Receiver Starting on port 5001...")
    run_server()
```

**Install dependencies:**
```bash
pip3 install flask flask-cors
```

**Run it:**
```bash
python3 waypoint_receiver.py
```

---

#### Program 2: Voice Assistant (Speaks Waypoints)
File: `hello_ai_pi_custom.py` (already updated!)

The voice assistant now automatically:
1. Checks for `waypoints.json` file
2. If it exists, uses waypoint data
3. When you ask "where am I?", it speaks the waypoints!

**Run it:**
```bash
python3 hello_ai_pi_custom.py
```

---

### 3. What Pi Will Say

**Example conversation:**

**You:** "Hey Pi, where am I?"

**Pi speaks:** 
> "You are at WP2. Coordinates: latitude 37.7749, longitude minus 122.4194. You have 2 waypoints saved. Your waypoints are: WP1, WP2."

---

### 4. On The Boat - Complete Setup

**Step 1: Create iPhone Hotspot**
- Settings → Personal Hotspot → Turn On
- iPhone gets IP: `192.168.43.1`

**Step 2: Connect Pi to Hotspot**
- On Pi: Click WiFi → Select your iPhone hotspot
- Pi gets IP: `192.168.43.x` (check with `hostname -I`)

**Step 3: Start Both Programs on Pi**

Terminal 1:
```bash
python3 waypoint_receiver.py
```

Terminal 2:
```bash
python3 hello_ai_pi_custom.py
```

Or run both in background:
```bash
python3 waypoint_receiver.py &
python3 hello_ai_pi_custom.py
```

**Step 4: Friend's App Sends Waypoint**
- Friend navigates to fishing spot
- Taps "Save Waypoint" in their app
- App sends GPS to `http://192.168.43.1:5001/waypoint`

**Step 5: Ask Pi**
- You: "Where am I?"
- Pi tells you the waypoint location!

---

### 5. Testing on Mac (Before Boat Trip)

**What we just did:**
1. ✅ Created web app for iPhone
2. ✅ Flask server receives waypoints
3. ✅ Updated Pi code to speak waypoints

**To test end-to-end on Mac:**
```bash
# Terminal 1: Flask receiver
cd ~/Desktop/AI/respeaker-ai
python3 test_waypoint_receiver.py

# iPhone: Send waypoints via web app
# http://10.11.3.221:8080

# Check waypoints.json was created
cat waypoints.json
```

---

### 6. Summary

**Flow:**
```
Friend's Phone (GPS) 
    ↓
Friend's React Native App (add fetch code)
    ↓
WiFi Hotspot
    ↓
Raspberry Pi (Flask server on port 5001)
    ↓
Saves to waypoints.json
    ↓
Voice Assistant reads waypoints.json
    ↓
You ask "where am I?"
    ↓
Pi speaks waypoint location! 🔊
```

**Files you need on Pi:**
1. `waypoint_receiver.py` - Receives waypoints from friend's app
2. `hello_ai_pi_custom.py` - Voice assistant (speaks waypoints)
3. `waypoints.json` - Auto-created when waypoints received

**Code friend needs to add:**
- ~10 lines of JavaScript (the `sendWaypointToPi` function above)
