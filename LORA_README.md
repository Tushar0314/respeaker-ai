# Pi5 LoRa Communication System - Summary

## 🎯 What This Does

Your Raspberry Pi 5 can now:
1. **Send GPS coordinates** to your LoRa32 device
2. **Receive text commands** from LoRa32 and **speak them** using text-to-speech

## 📁 Files Created

| File | Description |
|------|-------------|
| **lora_transmitter.py** | Sends GPS coordinates from Pi5 to LoRa32 |
| **lora_receiver_tts.py** | Receives commands from LoRa32 and speaks them |
| **setup_lora.sh** | Automated setup script for Pi5 |
| **lora32_example.ino** | Arduino code for your LoRa32 device |
| **LORA_SETUP_GUIDE.md** | Complete setup documentation |
| **LORA_QUICK_REFERENCE.md** | Quick command reference |

---

## 🚀 Getting Started (3 Steps)

### Step 1: Setup on Raspberry Pi 5

```bash
# Run the setup script
cd ~/respeaker-ai
./setup_lora.sh

# This will:
# - Install espeak (text-to-speech)
# - Install pyserial (for LoRa communication)
# - Enable UART (for GPIO LoRa connection)
# - Configure permissions
```

**Reboot after setup!**

### Step 2: Connect Hardware

#### Option A: LoRa HAT on GPIO
```
LoRa Module → Pi5 GPIO Pins
VCC → Pin 1  (3.3V)
GND → Pin 6  (GND)
TX  → Pin 10 (RX)
RX  → Pin 8  (TX)
```
**Serial Port**: `/dev/ttyAMA0`

#### Option B: USB LoRa Module
Plug into USB port
**Serial Port**: `/dev/ttyUSB0`

### Step 3: Test It!

```bash
# Test 1: Send coordinates
python3 lora_transmitter.py location

# Test 2: Speak commands
python3 lora_receiver_tts.py test
```

---

## 💬 How It Works

### Pi5 → LoRa32 (Transmit Coordinates)

```
┌─────────────────┐
│  Raspberry Pi 5 │
│                 │
│  current_       │
│  location.json  │──→ lora_transmitter.py
│                 │         ↓
│  waypoints.json │    Format: "CURRENT:37.788,-122.432"
└────────┬────────┘         ↓
         │            ┌──────────┐
         └───UART────→│ LoRa HAT │
                      └─────┬────┘
                            │ Radio (915MHz)
                            ↓
                      ┌──────────┐
                      │ LoRa32   │
                      │ Display  │
                      │ Shows    │
                      │ lat, lon │
                      └──────────┘
```

### LoRa32 → Pi5 (Receive & Speak)

```
┌──────────┐
│ LoRa32   │
│          │
│ Button   │ Press button
│ "HOLD"   │──→ Send "hold" via LoRa
└─────┬────┘
      │ Radio (915MHz)
      ↓
┌──────────┐
│ LoRa HAT │
└─────┬────┘
      │ UART
      ↓
┌─────────────────┐
│  Raspberry Pi 5 │
│                 │
│  lora_receiver_ │
│  tts.py         │──→ espeak "hold"
│                 │         ↓
│                 │    🔊 Speaker
└─────────────────┘    Speaks: "hold"
```

---

## 🎮 Usage Examples

### Example 1: Send Current Location

```bash
python3 lora_transmitter.py location
```

**Output:**
```
[TX] Sending: CURRENT:37.788250,-122.432400
```

**LoRa32 receives:**
```
CURRENT: 37.788250, -122.432400
```

### Example 2: Continuous Coordinate Transmission

```bash
# Send coordinates every 10 seconds
python3 lora_transmitter.py continuous /dev/ttyAMA0 10
```

### Example 3: Receive & Speak Commands

```bash
# Listen for commands
python3 lora_receiver_tts.py listen
```

**When LoRa32 sends "hold":**
```
[RX] Received: hold
🔊 SPEAKING: "hold"
```

Your Pi5 speaker says: **"hold"**

### Example 4: Different Command Formats

LoRa32 can send various formats:

| LoRa32 Sends | Pi5 Speaks |
|--------------|------------|
| `hold` | "hold" |
| `SPEED:slow:Please slow down` | "Please slow down" (slowly) |
| `ALERT:Warning:Battery low` | "Warning! Battery low" (loud) |
| `{"message": "Turn left"}` | "Turn left" |

---

## 🔧 LoRa32 Setup

### Upload Code to LoRa32

1. Open `lora32_example.ino` in Arduino IDE
2. Select your board (TTGO LoRa32 / Heltec LoRa32)
3. Adjust frequency for your region:
   ```cpp
   #define LORA_FREQ   915E6  // US
   // #define LORA_FREQ   868E6  // Europe
   // #define LORA_FREQ   433E6  // Asia
   ```
4. Upload to LoRa32

### Test Communication

**On LoRa32:**
- Open Serial Monitor (115200 baud)
- You should see coordinates from Pi5 appear

**Send Commands:**
- Press the BOOT button → Sends "hold"
- Type in Serial Monitor → Sends custom command

---

## 📱 Real-World Scenarios

### Scenario 1: Navigation Assistant
1. Friend app sends waypoints to Pi5 → `waypoints.json`
2. Pi5 transmits waypoints to LoRa32 every 10 seconds
3. LoRa32 displays waypoints on OLED screen
4. User presses button on LoRa32 → "where am I?"
5. Pi5 speaks current location

### Scenario 2: Remote Control
1. LoRa32 sends "start recording"
2. Pi5 speaks "start recording"
3. Pi5 starts camera recording
4. LoRa32 sends "stop"
5. Pi5 speaks "stop" and stops recording

### Scenario 3: Emergency Alert
1. LoRa32 detects low battery
2. Sends: `ALERT:Emergency:Battery critical`
3. Pi5 speaks loudly: "Emergency! Battery critical"

---

## ⚙️ Configuration

### Change Serial Port

If your LoRa module is on a different port:

```bash
# Find your port
ls /dev/tty* | grep -E "(ttyAMA|ttyUSB|ttyACM)"

# Use it
python3 lora_transmitter.py location /dev/ttyUSB0
python3 lora_receiver_tts.py listen /dev/ttyUSB0
```

### Adjust Speech Settings

Edit `lora_receiver_tts.py`:

```python
# Line ~75
self.speak(
    text,
    speed=150,   # Words per minute (80-450)
    pitch=50,    # Voice pitch (0-99)
    volume=100   # Volume (0-200)
)
```

### Change Transmission Interval

```bash
# Every 5 seconds instead of 10
python3 lora_transmitter.py continuous /dev/ttyAMA0 5
```

---

## 🔁 Auto-Start on Boot

Make it run automatically when Pi5 boots:

```bash
crontab -e
```

Add these lines:

```bash
# Transmit coordinates every 10 seconds
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 lora_transmitter.py continuous /dev/ttyAMA0 10 >> lora_tx.log 2>&1

# Listen for commands
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 lora_receiver_tts.py listen /dev/ttyAMA0 >> lora_rx.log 2>&1
```

Reboot and check logs:
```bash
tail -f ~/respeaker-ai/lora_tx.log
tail -f ~/respeaker-ai/lora_rx.log
```

---

## 🐛 Troubleshooting

### "Serial port not found"

```bash
# Check what ports exist
ls /dev/tty* | grep -E "(ttyAMA|ttyUSB|ttyACM)"

# Enable UART
sudo raspi-config
# Interface Options → Serial Port
# Login shell: NO
# Hardware: YES
sudo reboot
```

### "Permission denied"

```bash
sudo usermod -a -G dialout $USER
# Logout and login again
```

### "espeak not working"

```bash
# Reinstall
sudo apt-get install --reinstall espeak

# Test
espeak "test"

# Check audio
speaker-test -t wav
```

### "No data received"

Check:
- ✅ Same frequency on both devices (915/868/433 MHz)
- ✅ Antennas connected
- ✅ Correct wiring (TX → RX, RX → TX)
- ✅ Power supply stable (3.3V for LoRa)

---

## 📖 Documentation

- **Full Guide**: [LORA_SETUP_GUIDE.md](LORA_SETUP_GUIDE.md)
- **Quick Reference**: [LORA_QUICK_REFERENCE.md](LORA_QUICK_REFERENCE.md)
- **Arduino Code**: [lora32_example.ino](lora32_example.ino)

---

## 🎯 Next Steps

1. ✅ **Setup** - Run `./setup_lora.sh`
2. ✅ **Hardware** - Connect LoRa module to Pi5
3. ✅ **Test TX** - `python3 lora_transmitter.py location`
4. ✅ **Test RX** - `python3 lora_receiver_tts.py test`
5. ✅ **LoRa32** - Upload `lora32_example.ino`
6. ✅ **Test Both** - Send coordinates and commands
7. ✅ **Auto-start** - Add to crontab
8. ✅ **Deploy** - Use in real scenarios!

---

## 💡 Tips

- **Range**: LoRa can work from 1-10 km depending on environment
- **Antenna**: Use proper antenna for your frequency
- **Power**: LoRa modules need stable power supply
- **Line of sight**: Best performance with clear line of sight
- **Interference**: Avoid obstacles like buildings, trees

---

## 📞 Support Resources

**Check if everything is working:**

```bash
# 1. Check serial port
ls -l /dev/ttyAMA0

# 2. Test espeak
espeak "system check"

# 3. Test LoRa transmitter
python3 lora_transmitter.py location

# 4. Test LoRa receiver
python3 lora_receiver_tts.py test
```

---

## Summary

You now have a complete bidirectional LoRa communication system:

- 📤 **Pi5 → LoRa32**: GPS coordinates transmitted
- 📥 **LoRa32 → Pi5**: Commands received and spoken
- 🔊 **Text-to-Speech**: All commands spoken via espeak
- 🤖 **Autonomous**: Can run on boot automatically
- 📡 **Long Range**: Up to 10km range with LoRa

**Ready to go!** 🚀
