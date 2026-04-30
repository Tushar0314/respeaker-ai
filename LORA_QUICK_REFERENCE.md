# LoRa Quick Reference Card

## 🚀 Quick Start

### On Raspberry Pi 5:

```bash
# 1. Run setup (first time only)
./setup_lora.sh

# 2. Transmit coordinates to LoRa32
python3 lora_transmitter.py location

# 3. Listen for commands and speak them
python3 lora_receiver_tts.py listen
```

---

## 📤 Transmit GPS Coordinates (Pi5 → LoRa32)

```bash
# Send current location once
python3 lora_transmitter.py location

# Send all waypoints once
python3 lora_transmitter.py waypoints

# Continuous transmission (every 10 seconds)
python3 lora_transmitter.py continuous /dev/ttyAMA0 10

# Auto waypoint transmission (every 5 seconds)
python3 lora_transmitter.py auto /dev/ttyAMA0 5
```

---

## 📥 Receive Commands & Speak (LoRa32 → Pi5)

```bash
# Listen for commands
python3 lora_receiver_tts.py listen

# Test text-to-speech
python3 lora_receiver_tts.py test

# With custom serial port
python3 lora_receiver_tts.py listen /dev/ttyUSB0
```

---

## 📋 Command Formats (send from LoRa32)

| Format | Example | Pi5 Speaks |
|--------|---------|------------|
| Simple | `hold` | "hold" |
| JSON | `{"message": "Please hold"}` | "Please hold" |
| Speed | `SPEED:slow:Slow down` | "Slow down" (slow) |
| Alert | `ALERT:Warning:Battery low` | "Warning! Battery low" |

---

## 🔧 Common Serial Ports

| Connection Type | Port |
|----------------|------|
| GPIO UART | `/dev/ttyAMA0` or `/dev/serial0` |
| USB LoRa | `/dev/ttyUSB0` |
| USB-Serial | `/dev/ttyACM0` |

Check available ports:
```bash
ls /dev/tty* | grep -E "(ttyAMA|ttyUSB|ttyACM)"
```

---

## 🔌 GPIO Pinout (for LoRa HAT)

```
LoRa Module    →    Pi5 GPIO
─────────────────────────────
VCC (3.3V)     →    Pin 1
GND            →    Pin 6
TX             →    Pin 10 (RX)
RX             →    Pin 8  (TX)
```

---

## 🐛 Quick Troubleshooting

### Permission denied?
```bash
sudo usermod -a -G dialout $USER
# Logout and login
```

### Port not found?
```bash
# Enable UART
sudo raspi-config
# Interface → Serial → NO (login) + YES (hardware)
sudo reboot
```

### No audio?
```bash
# Test espeak
espeak "test"

# Check audio
speaker-test -t wav
```

---

## 🤖 Auto-Start on Boot

```bash
# Edit crontab
crontab -e

# Add these lines:

# Transmit coordinates every 10 sec
@reboot sleep 30 && cd ~/respeaker-ai && python3 lora_transmitter.py continuous /dev/ttyAMA0 10 >> lora_tx.log 2>&1

# Listen for commands
@reboot sleep 30 && cd ~/respeaker-ai && python3 lora_receiver_tts.py listen /dev/ttyAMA0 >> lora_rx.log 2>&1
```

---

## 📦 What You Need

### Hardware:
- ✅ Raspberry Pi 5
- ✅ LoRa module (HAT or USB)
- ✅ LoRa32 device (ESP32 + LoRa)
- ✅ Antennas for both
- ✅ Speaker (for TTS)

### Software:
- ✅ Python 3
- ✅ pyserial (`pip install pyserial`)
- ✅ espeak (`sudo apt-get install espeak`)

---

## 📁 Files

| File | Purpose |
|------|---------|
| `lora_transmitter.py` | Send GPS coordinates |
| `lora_receiver_tts.py` | Receive commands & speak |
| `setup_lora.sh` | Setup script |
| `LORA_SETUP_GUIDE.md` | Full documentation |
| `current_location.json` | Current GPS position |
| `waypoints.json` | Saved waypoints |

---

## 💡 Example Workflow

1. **Friend sends waypoints** (via Friend app) → `waypoints.json`
2. **Pi5 transmits** coordinates to LoRa32 → LoRa radio
3. **LoRa32 displays** location on screen
4. **User sends command** (via LoRa32) → "hold"
5. **Pi5 receives & speaks**: "hold"

---

## 🎯 Use Cases

- 🚁 **Drone control** - Send waypoints, receive status
- 🥾 **Hiking** - Track position, send alerts
- 🤖 **Robot navigation** - Coordinate sharing
- 📡 **Long-range IoT** - Communicate without WiFi/cellular

---

## 📞 Help

```bash
# Show help for transmitter
python3 lora_transmitter.py -h

# Show help for receiver
python3 lora_receiver_tts.py -h
```

Full guide: [LORA_SETUP_GUIDE.md](LORA_SETUP_GUIDE.md)
