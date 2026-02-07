# Code for Friend's React Native App

## Two Modes: Live Tracking + Saved Waypoints

Your friend needs to add this code to their React Native app.

---

### **Part 1: Live Tracking (Automatic - Every 5 Seconds)**

```javascript
// At the top of their app file
import { useEffect } from 'react';
import Geolocation from 'react-native-geolocation';

const PI_IP = '192.168.43.1';  // Your Pi's IP on hotspot
const PI_PORT = '5001';

// Live tracking component
const LiveTracking = () => {
  useEffect(() => {
    // Start watching GPS position
    const watchId = Geolocation.watchPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        
        // Send to Pi automatically
        sendLiveLocationToPi(lat, lon);
      },
      (error) => console.error(error),
      {
        enableHighAccuracy: true,
        distanceFilter: 10, // Update when move 10+ meters
        interval: 5000       // Check every 5 seconds
      }
    );
    
    // Cleanup when component unmounts
    return () => Geolocation.clearWatch(watchId);
  }, []);
  
  return null; // This component doesn't render anything
};

// Function to send live location
const sendLiveLocationToPi = async (lat, lon) => {
  try {
    await fetch(`http://${PI_IP}:${PI_PORT}/current`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ lat, lon })
    });
    console.log('📍 Live location sent to Pi');
  } catch (error) {
    console.error('Could not send to Pi:', error);
  }
};

export default LiveTracking;
```

---

### **Part 2: Save Waypoint (Manual - When Friend Taps Button)**

```javascript
// Function to save a waypoint
const saveWaypointToPi = async (waypointNumber) => {
  Geolocation.getCurrentPosition(
    async (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const waypointName = `WP${waypointNumber}`;
      
      try {
        await fetch(`http://${PI_IP}:${PI_PORT}/waypoint`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            waypoints: `${waypointName}:${lat},${lon}`
          })
        });
        
        console.log(`✅ ${waypointName} saved to Pi`);
        Alert.alert('Success', `Waypoint ${waypointNumber} saved!`);
      } catch (error) {
        Alert.alert('Error', 'Could not save waypoint to Pi');
      }
    },
    (error) => console.error(error),
    { enableHighAccuracy: true }
  );
};

// Button in UI
<Button 
  title="💾 Save Waypoint" 
  onPress={() => saveWaypointToPi(1)} // Save as WP1
/>
```

---

### **Part 3: Complete Example (Both Together)**

```javascript
import React, { useState, useEffect } from 'react';
import { View, Button, Text, Alert } from 'react-native';
import Geolocation from 'react-native-geolocation';

const PI_IP = '192.168.43.1';
const PI_PORT = '5001';

const FriendApp = () => {
  const [waypointCount, setWaypointCount] = useState(0);
  const [liveTracking, setLiveTracking] = useState(false);
  
  // Live tracking effect
  useEffect(() => {
    if (!liveTracking) return;
    
    const watchId = Geolocation.watchPosition(
      (position) => {
        sendLiveLocation(position.coords.latitude, position.coords.longitude);
      },
      (error) => console.error(error),
      { enableHighAccuracy: true, distanceFilter: 10, interval: 5000 }
    );
    
    return () => Geolocation.clearWatch(watchId);
  }, [liveTracking]);
  
  // Send live location
  const sendLiveLocation = async (lat, lon) => {
    try {
      await fetch(`http://${PI_IP}:${PI_PORT}/current`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ lat, lon })
      });
      console.log('📍 Live location sent');
    } catch (error) {
      console.error('Live tracking error:', error);
    }
  };
  
  // Save waypoint
  const saveWaypoint = () => {
    Geolocation.getCurrentPosition(
      async (position) => {
        const newCount = waypointCount + 1;
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        
        try {
          await fetch(`http://${PI_IP}:${PI_PORT}/waypoint`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              waypoints: `WP${newCount}:${lat},${lon}`
            })
          });
          
          setWaypointCount(newCount);
          Alert.alert('Success', `Waypoint ${newCount} saved!`);
        } catch (error) {
          Alert.alert('Error', 'Could not save to Pi');
        }
      },
      (error) => console.error(error),
      { enableHighAccuracy: true }
    );
  };
  
  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20, marginBottom: 20 }}>
        Raspberry Pi GPS Sender
      </Text>
      
      <Button
        title={liveTracking ? '🟢 Stop Live Tracking' : '⚪ Start Live Tracking'}
        onPress={() => setLiveTracking(!liveTracking)}
        color={liveTracking ? '#4CAF50' : '#999'}
      />
      
      <View style={{ height: 20 }} />
      
      <Button
        title={`💾 Save Waypoint ${waypointCount + 1}`}
        onPress={saveWaypoint}
        color="#FF9800"
      />
      
      <Text style={{ marginTop: 20, color: '#666' }}>
        Waypoints saved: {waypointCount}
      </Text>
    </View>
  );
};

export default FriendApp;
```

---

## **How Friend Uses This:**

1. **Start Live Tracking:**
   - Friend opens app
   - Taps "Start Live Tracking" button
   - App sends GPS to your Pi every 5 seconds
   - You can ask Pi "where am I?" anytime → Get current location

2. **Save Important Spots:**
   - Friend arrives at good fishing spot
   - Taps "Save Waypoint" button
   - Pi permanently saves that location as WP1
   - Later you can ask "where is waypoint 1?"

3. **On the Boat:**
   - Friend's iPhone connected to your iPhone hotspot
   - Pi connected to same hotspot
   - Everything works automatically!

---

## **Testing Without Friend's App:**

Use the web app on your iPhone:
1. Safari → `http://10.11.3.221:8080`
2. Toggle "Live Tracking" ON
3. Add waypoints manually
4. Test both modes!

---

## **Next Steps:**

1. ✅ Flask server running (both modes work)
2. ✅ Web app updated (can test on iPhone)
3. ⏳ Friend adds code to their React Native app
4. ⏳ Update Pi voice assistant to handle both modes

Ready to test or update the Pi voice code?
