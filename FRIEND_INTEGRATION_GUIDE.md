# Integration Guide for Your Friend's React Native App

## What Your Friend Needs to Know

### 1. Server Configuration
**Your Mac/Pi Server Address:**
- When testing on Mac: `http://10.11.3.221:5001`
- When on Raspberry Pi (via hotspot): `http://192.168.43.1:5001`

Your friend needs to update his React Native app to send GPS data to YOUR server.

---

## 2. Code Changes for Friend's React Native App

### Option A: Send LIVE GPS (Every 5 seconds - Automatic)

Add this code to automatically send GPS updates:

```javascript
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

// Configuration - YOUR SERVER IP
const PI_SERVER = 'http://10.11.3.221:5001';  // Change to your Mac/Pi IP

function App() {
  const [location, setLocation] = useState(null);

  useEffect(() => {
    // Get location permission
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission to access location was denied');
        return;
      }
    })();

    // Send live GPS every 5 seconds
    const interval = setInterval(async () => {
      try {
        let currentLocation = await Location.getCurrentPositionAsync({});
        const { latitude, longitude } = currentLocation.coords;
        
        // Send to YOUR server
        await fetch(`${PI_SERVER}/current`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            lat: latitude,
            lon: longitude
          })
        });
        
        console.log('✅ Sent live GPS:', latitude, longitude);
        setLocation({ latitude, longitude });
      } catch (error) {
        console.error('GPS error:', error);
      }
    }, 5000); // Every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sending GPS to Pi</Text>
      {location && (
        <Text>
          📍 {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
        </Text>
      )}
    </View>
  );
}
```

---

### Option B: Send SAVED WAYPOINTS (Manual button press)

Add this code for manual waypoint saving:

```javascript
import { useState } from 'react';
import * as Location from 'expo-location';

const PI_SERVER = 'http://10.11.3.221:5001';  // Change to your Mac/Pi IP

function App() {
  const [waypoints, setWaypoints] = useState([]);

  const saveWaypoint = async () => {
    try {
      // Get current GPS
      let currentLocation = await Location.getCurrentPositionAsync({});
      const { latitude, longitude } = currentLocation.coords;
      
      // Generate waypoint name
      const wpName = `WP${waypoints.length + 1}`;
      const newWaypoint = { name: wpName, lat: latitude, lon: longitude };
      
      // Add to local list
      const updatedWaypoints = [...waypoints, newWaypoint];
      setWaypoints(updatedWaypoints);
      
      // Send to YOUR server
      const waypointString = updatedWaypoints
        .map(wp => `${wp.name}:${wp.lat},${wp.lon}`)
        .join(';');
      
      await fetch(`${PI_SERVER}/waypoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints: waypointString })
      });
      
      console.log('✅ Saved waypoint:', wpName);
      alert(`Saved ${wpName}!`);
    } catch (error) {
      console.error('Error saving waypoint:', error);
      alert('Failed to save waypoint');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Waypoint Saver</Text>
      
      <TouchableOpacity style={styles.button} onPress={saveWaypoint}>
        <Text style={styles.buttonText}>📍 Save Current Location</Text>
      </TouchableOpacity>
      
      <FlatList
        data={waypoints}
        renderItem={({ item }) => (
          <Text>{item.name}: {item.lat.toFixed(4)}, {item.lon.toFixed(4)}</Text>
        )}
        keyExtractor={(item, index) => index.toString()}
      />
    </View>
  );
}
```

---

### Option C: BOTH Live + Saved (Recommended)

Combine both approaches - send live GPS continuously AND allow manual waypoint saving:

```javascript
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

const PI_SERVER = 'http://10.11.3.221:5001';  // YOUR SERVER IP

function App() {
  const [location, setLocation] = useState(null);
  const [waypoints, setWaypoints] = useState([]);
  const [liveTracking, setLiveTracking] = useState(true);

  // Live GPS tracking
  useEffect(() => {
    if (!liveTracking) return;

    const interval = setInterval(async () => {
      try {
        let currentLocation = await Location.getCurrentPositionAsync({});
        const { latitude, longitude } = currentLocation.coords;
        
        await fetch(`${PI_SERVER}/current`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lat: latitude, lon: longitude })
        });
        
        setLocation({ latitude, longitude });
      } catch (error) {
        console.error('GPS error:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [liveTracking]);

  // Manual waypoint saving
  const saveWaypoint = async () => {
    try {
      let currentLocation = await Location.getCurrentPositionAsync({});
      const { latitude, longitude } = currentLocation.coords;
      
      const wpName = `WP${waypoints.length + 1}`;
      const newWaypoint = { name: wpName, lat: latitude, lon: longitude };
      const updatedWaypoints = [...waypoints, newWaypoint];
      setWaypoints(updatedWaypoints);
      
      const waypointString = updatedWaypoints
        .map(wp => `${wp.name}:${wp.lat},${wp.lon}`)
        .join(';');
      
      await fetch(`${PI_SERVER}/waypoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints: waypointString })
      });
      
      alert(`Saved ${wpName}!`);
    } catch (error) {
      alert('Failed to save waypoint');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>GPS Tracker</Text>
      
      {/* Live tracking toggle */}
      <View style={styles.row}>
        <Text>Live Tracking:</Text>
        <Switch value={liveTracking} onValueChange={setLiveTracking} />
      </View>
      
      {/* Current location */}
      {location && (
        <Text style={styles.gps}>
          📍 {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
        </Text>
      )}
      
      {/* Save waypoint button */}
      <TouchableOpacity style={styles.button} onPress={saveWaypoint}>
        <Text style={styles.buttonText}>💾 Save Waypoint</Text>
      </TouchableOpacity>
      
      {/* Waypoint list */}
      <FlatList
        data={waypoints}
        renderItem={({ item }) => (
          <Text>{item.name}: {item.lat.toFixed(4)}, {item.lon.toFixed(4)}</Text>
        )}
        keyExtractor={(item, index) => index.toString()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  gps: {
    fontSize: 18,
    color: '#2196F3',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
```

---

## 3. What Friend Needs to Install

In his React Native project:

```bash
npm install expo-location
```

Or if using plain React Native:

```bash
npm install @react-native-community/geolocation
```

---

## 4. Network Requirements

**IMPORTANT:** Your friend's phone and your Mac/Pi must be on the **same WiFi network** OR you need to:

### Option A: Same WiFi
- Both phones connect to same WiFi
- Use your Mac's local IP: `10.11.3.221:5001`

### Option B: Mobile Hotspot (Recommended for boat)
1. Create hotspot on your Mac/Pi
2. Friend connects to YOUR hotspot
3. Use hotspot IP: `http://192.168.43.1:5001`

---

## 5. Testing

Once friend's app is running:

1. **Check Flask server logs** - You'll see:
   ```
   📍 LIVE LOCATION UPDATE: 37.7749, -122.4194
   ✅ Current location updated
   ```

2. **Check files on your Mac/Pi:**
   ```bash
   cat current_location.json    # Live GPS
   cat waypoints.json           # Saved waypoints
   ```

3. **Ask your voice assistant:**
   - "where am I?" → Should respond with friend's GPS coordinates

---

## 6. Summary for Friend

**Tell your friend:**

> "Just add this code to your React Native app and change `PI_SERVER` to my IP address. 
> When you're on the boat, connect to my WiFi hotspot and your GPS will automatically 
> send to my Raspberry Pi. When I ask my voice assistant 'where am I?', it will 
> tell me YOUR GPS coordinates!"

---

## API Key Note

Your friend does NOT need YOUR Gemini API key. He only needs to:
1. Send GPS data to your server IP
2. Be on the same network as your Mac/Pi

The Gemini API key is only used on YOUR Mac/Pi for the voice assistant.
