# LoRa Communication Setup Guide - Pi5 ↔ LoRa32

## Overview

This guide helps you set up bidirectional communication between your Raspberry Pi 5 and LoRa32 device:
- **Pi5 → LoRa32**: Transmit GPS coordinates
- **LoRa32 → Pi5**: Receive commands and speak them via text-to-speech

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 5                            │
│  ┌────────────────────┐         ┌─────────────────────┐    │
│  │  lora_transmitter  │         │ lora_receiver_tts   │    │
│  │  (Send coords)     │◄───────►│  (Receive commands) │    │
│  └────────┬───────────┘         └──────────┬──────────┘    │
│           │                                  │               │
│           │  current_location.json          │               │
│           │  waypoints.json                 │ espeak (TTS)  │
│           │                                  ▼               │
│           │                          🔊 Speaker Output       │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      LoRa Module (GPIO UART / USB)                  │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      │ LoRa Radio (433/868/915 MHz)
                      │
                      ▼
            ┌─────────────────┐
            │    LoRa32       │
            │  (ESP32+LoRa)   │
            │                 │
            │  - Receives GPS │
            │  - Sends cmds   │
            └─────────────────┘
```

---

## Hardware Requirements

### 1. LoRa Module for Raspberry Pi 5

Choose one of these:
- **LoRa HAT** (Waveshare SX1262/SX1268 LoRa HAT)
- **LoRa USB dongle** (RA-02/E32 with USB-Serial adapter)
- **Standalone LoRa module** (SX1276/SX1278 connected to GPIO)

### 2. Connections

#### Option A: GPIO UART (Recommended)
```
LoRa Module    →    Raspberry Pi 5
─────────────────────────────────
VCC (3.3V)     →    Pin 1  (3.3V)
GND            →    Pin 6  (GND)
TX             →    Pin 10 (GPIO15 - RX)
RX             →    Pin 8  (GPIO14 - TX)
```

**Serial Port**: `/dev/ttyAMA0` or `/dev/serial0`

#### Option B: USB Connection
```
LoRa USB Module  →  Pi5 USB Port
```

**Serial Port**: `/dev/ttyUSB0` or `/dev/ttyACM0`

### 3. LoRa32 Device
- ESP32 with LoRa module (e.g., TTGO LoRa32, Heltec LoRa32)
- Same frequency as Pi5 LoRa module (433/868/915 MHz)

---

## Software Setup on Raspberry Pi 5

### Step 1: Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install espeak for text-to-speech
sudo apt-get install -y espeak

# Install Python serial library
pip install pyserial

# Test espeak
espeak "Hello, I am your Raspberry Pi assistant"
```

### Step 2: Enable UART (for GPIO connection)

```bash
# Run Raspberry Pi configuration
sudo raspi-config

# Navigate to:
# 3. Interface Options
#   → I6. Serial Port
#     → "Would you like a login shell accessible over serial?" → NO
#     → "Would you like the serial port hardware enabled?" → YES

# Reboot
sudo reboot
```

### Step 3: Verify Serial Port

```bash
# List all serial ports
ls /dev/tty*

# You should see one of:
# /dev/ttyAMA0  - GPIO UART
# /dev/ttyUSB0  - USB LoRa module
# /dev/serial0  - Symlink to UART

# Test serial port (replace with your port)
sudo cat /dev/ttyAMA0
# Press Ctrl+C to stop
```

### Step 4: Set Permissions

```bash
# Add user to dialout group (for serial access)
sudo usermod -a -G dialout $USER

# Logout and login again for changes to take effect
```

---

## Usage

### 1. Transmit GPS Coordinates to LoRa32

#### One-time transmission:

```bash
# Send current location
python3 lora_transmitter.py location

# Send all waypoints
python3 lora_transmitter.py waypoints
```

#### Continuous transmission:

```bash
# Send current location every 10 seconds
python3 lora_transmitter.py continuous /dev/ttyAMA0 10

# Send waypoints every 5 seconds
python3 lora_transmitter.py auto /dev/ttyAMA0 5
```

#### Custom serial port:

```bash
# For USB LoRa module
python3 lora_transmitter.py location /dev/ttyUSB0
```

### 2. Receive Commands and Speak

```bash
# Listen for commands from LoRa32
python3 lora_receiver_tts.py listen

# With custom serial port
python3 lora_receiver_tts.py listen /dev/ttyUSB0

# Test text-to-speech
python3 lora_receiver_tts.py test
```

---

## Command Formats from LoRa32

The Pi5 can receive and speak commands in multiple formats:

### Format 1: Simple Text
```
hold
```
**Pi5 speaks**: "hold"

### Format 2: JSON
```json
{"command": "hold", "message": "Please hold your position"}
```
**Pi5 speaks**: "Please hold your position"

### Format 3: With Speed Control
```
SPEED:slow:Please slow down
```
**Pi5 speaks**: "Please slow down" (at slow speed)

Speed options: `slow`, `normal`, `fast`, `very_fast`

### Format 4: Alert Messages
```
ALERT:Warning:Low battery
```
**Pi5 speaks**: "Warning! Low battery" (with higher pitch and volume)

---

## LoRa32 Arduino Code Example

### Basic Sender (LoRa32 → Pi5)

```cpp
#include <LoRa.h>

#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

void setup() {
  Serial.begin(115200);
  
  // Initialize LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(915E6)) {  // 915MHz for US, 868MHz for EU, 433MHz for Asia
    Serial.println("LoRa init failed!");
    while (1);
  }
  
  Serial.println("LoRa OK!");
}

void loop() {
  // Send simple command
  LoRa.beginPacket();
  LoRa.print("hold");
  LoRa.endPacket();
  
  delay(5000);
  
  // Send alert
  LoRa.beginPacket();
  LoRa.print("ALERT:Warning:Turn left ahead");
  LoRa.endPacket();
  
  delay(5000);
}
```

### Basic Receiver (LoRa32 receives from Pi5)

```cpp
#include <LoRa.h>

#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

void setup() {
  Serial.begin(115200);
  
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(915E6)) {
    Serial.println("LoRa init failed!");
    while (1);
  }
  
  Serial.println("Waiting for GPS coordinates...");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    String received = "";
    
    while (LoRa.available()) {
      received += (char)LoRa.read();
    }
    
    Serial.print("Received: ");
    Serial.println(received);
    
    // Parse coordinates
    // Format: CURRENT:37.788250,-122.432400
    if (received.startsWith("CURRENT:") || 
        received.startsWith("WP1:")) {
      parseCoordinates(received);
    }
  }
}

void parseCoordinates(String data) {
  int colonPos = data.indexOf(':');
  int commaPos = data.indexOf(',');
  
  if (colonPos > 0 && commaPos > colonPos) {
    String name = data.substring(0, colonPos);
    String latStr = data.substring(colonPos + 1, commaPos);
    String lonStr = data.substring(commaPos + 1);
    
    float lat = latStr.toFloat();
    float lon = lonStr.toFloat();
    
    Serial.print(name);
    Serial.print(": ");
    Serial.print(lat, 6);
    Serial.print(", ");
    Serial.println(lon, 6);
  }
}
```

---

## Auto-Start on Boot

### Run transmitter on boot:

```bash
# Edit crontab
crontab -e

# Add this line to send coordinates every 10 seconds
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 lora_transmitter.py continuous /dev/ttyAMA0 10 >> lora_tx.log 2>&1
```

### Run receiver on boot:

```bash
# Edit crontab
crontab -e

# Add this line to listen for commands
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 lora_receiver_tts.py listen /dev/ttyAMA0 >> lora_rx.log 2>&1
```

---

## Testing

### Test 1: Text-to-Speech

```bash
# Test espeak directly
espeak "Testing text to speech"

# Test with LoRa receiver
python3 lora_receiver_tts.py test
```

### Test 2: Serial Communication

```bash
# Terminal 1: Listen on serial port
python3 -m serial.tools.miniterm /dev/ttyAMA0 115200

# Terminal 2: Send test data
echo "hold" > /dev/ttyAMA0
```

### Test 3: LoRa Range

```bash
# On Pi5
python3 lora_receiver_tts.py listen

# On LoRa32, send:
# - From 10m away
# - From 50m away  
# - From 100m away
# Check signal strength and reliability
```

---

## Troubleshooting

### Issue 1: Serial Port Not Found

**Error**: `[ERROR] Failed to connect to LoRa module: [Errno 2] No such file or directory: '/dev/ttyAMA0'`

**Solutions**:
```bash
# Check available ports
ls /dev/tty* | grep -E "(ttyAMA|ttyUSB|ttyACM)"

# Try alternative ports
python3 lora_transmitter.py location /dev/serial0
python3 lora_transmitter.py location /dev/ttyUSB0

# Enable UART in raspi-config
sudo raspi-config
# Interface Options → Serial Port → Enable hardware
```

### Issue 2: Permission Denied

**Error**: `[ERROR] Failed to connect to LoRa module: [Errno 13] Permission denied: '/dev/ttyAMA0'`

**Solutions**:
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again

# Or run with sudo (temporary)
sudo python3 lora_transmitter.py location
```

### Issue 3: No Data Received

**Check**:
1. LoRa modules on same frequency (433/868/915 MHz)
2. Correct wiring (TX → RX, RX → TX)
3. Power supply adequate (LoRa needs stable 3.3V)
4. Antennas connected

```bash
# Monitor serial port
sudo cat /dev/ttyAMA0

# Check LoRa32 is transmitting
# Use LoRa scanner or another LoRa device
```

### Issue 4: espeak Not Working

```bash
# Reinstall espeak
sudo apt-get install --reinstall espeak

# Test audio output
speaker-test -t wav -c 2

# Check audio device
aplay -l

# Set default audio device
sudo raspi-config
# System Options → Audio → Select output
```

---

## Advanced Features

### 1. Custom Commands with Actions

Edit `lora_receiver_tts.py` and modify the `custom_callback` function:

```python
def custom_callback(raw_data, command):
    """Custom actions based on commands."""
    
    text_lower = command['text'].lower()
    
    # Emergency stop
    if 'emergency' in text_lower:
        print("[!!!] EMERGENCY STOP")
        # Add your emergency action here
        # e.g., stop motors, send alert, etc.
    
    # Return to home
    elif 'home' in text_lower:
        print("[HOME] Returning to home position")
        # Trigger navigation to home coordinates
    
    # Start recording
    elif 'record' in text_lower:
        print("[RECORD] Starting camera recording")
        # Start camera or audio recording
```

### 2. Two-Way Communication

Create a combined script that both sends and receives:

```bash
# Run both in background
python3 lora_transmitter.py continuous &
python3 lora_receiver_tts.py listen &
```

### 3. GPS Integration

If you have a GPS module on Pi5:

```python
import gpsd

# Connect to GPS daemon
gpsd.connect()

# Get current position
packet = gpsd.get_current()
lat = packet.lat
lon = packet.lon

# Update current_location.json
# Then transmit via LoRa
```

---

## Example Use Cases

### Use Case 1: Remote Navigation Assistant
- LoRa32 receives GPS coordinates from Pi5
- User navigates using LoRa32 display
- User sends voice commands via LoRa32 button
- Pi5 speaks instructions

### Use Case 2: Drone Control
- Pi5 on ground station
- LoRa32 on drone
- Pi5 sends waypoints to drone
- Drone sends status messages (spoken on Pi5)

### Use Case 3: Hiking Companion
- Pi5 at campsite
- LoRa32 with hiker
- Pi5 tracks hiker's position
- Emergency commands spoken on Pi5

---

## Files Created

1. **lora_transmitter.py** - Transmit coordinates to LoRa32
2. **lora_receiver_tts.py** - Receive commands and speak them
3. **LORA_SETUP_GUIDE.md** - This guide

## Related Files

- `current_location.json` - Current GPS position
- `waypoints.json` - Saved waypoints
- `lora_command_history.json` - Log of received commands

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Connect LoRa module to Pi5
3. ✅ Test serial communication
4. ✅ Test text-to-speech
5. ✅ Send coordinates from Pi5
6. ✅ Receive commands on Pi5
7. ⬜ Program LoRa32 with Arduino
8. ⬜ Test bidirectional communication
9. ⬜ Set up auto-start
10. ⬜ Deploy and test in field

---

## Support

If you encounter issues:

1. Check troubleshooting section above
2. Verify hardware connections
3. Check serial port permissions
4. Test individual components (espeak, serial, LoRa)

## References

- [LoRa Documentation](https://lora-alliance.org/)
- [Raspberry Pi UART Guide](https://www.raspberrypi.com/documentation/computers/configuration.html#uart)
- [espeak Manual](http://espeak.sourceforge.net/commands.html)
- [pyserial Documentation](https://pyserial.readthedocs.io/)
