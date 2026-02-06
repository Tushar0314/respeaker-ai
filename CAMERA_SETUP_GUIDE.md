# 📷 Camera Streaming Setup Guide

## Raspberry Pi 5 + Camera Module 3 Live Streaming

This guide will help you stream live video from your Raspberry Pi Camera Module 3 so anyone can view the footage remotely.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /Users/tusharbhaliya/Desktop/AI/respeaker-ai

# Install picamera2 (should already be on Pi OS)
sudo apt update
sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps

# Install optional packages for remote streaming
pip3 install requests flask
```

### 2. Enable Camera
```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot
```

### 3. Test Camera
```bash
# Quick test
libcamera-hello

# Test with Python script
python3 camera_stream.py
# Choose option 2: Test Camera
```

### 4. Start Streaming
```bash
python3 camera_stream.py
# Choose option 1: Start HTTP Stream
```

### 5. View Stream
Open browser and go to:
- `http://YOUR_PI_IP:8080/`
- Example: `http://192.168.1.100:8080/`

---

## 📡 Streaming Methods

### Method 1: HTTP MJPEG Stream (Recommended ⭐)

**Best for:** Simple web viewing, easy setup

**Pros:**
- Works in any web browser
- No special software needed
- Easy to share link
- Built-in viewer webpage

**Cons:**
- Higher bandwidth usage
- 1-2 second latency

**How to use:**
```bash
python3 camera_stream.py
# Select option 1

# Then open browser:
http://YOUR_PI_IP:8080/
```

**Share with others:**
- On same WiFi: `http://192.168.1.100:8080/`
- Over internet: Forward port 8080 on router → `http://YOUR_PUBLIC_IP:8080/`

---

### Method 2: RTSP Stream (Advanced)

**Best for:** VLC, OBS, professional streaming

**Pros:**
- Lower latency (~500ms)
- Better quality
- Standard protocol

**Cons:**
- Requires player software (VLC)
- More complex setup

**Setup:**
```bash
# Install mediamtx (RTSP server)
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_arm64v8.tar.gz
tar -xzf mediamtx_v1.5.0_linux_arm64v8.tar.gz
sudo mv mediamtx /usr/local/bin/

# Create config
mkdir -p ~/.mediamtx
nano ~/.mediamtx/mediamtx.yml
```

**Config file:**
```yaml
paths:
  cam:
    source: publisher
    sourceProtocol: tcp
```

**Start streaming:**
```bash
# Terminal 1: Start mediamtx
mediamtx

# Terminal 2: Stream from camera
libcamera-vid -t 0 --width 1920 --height 1080 --framerate 30 -o - | \
  ffmpeg -f h264 -i - -c:v copy -f rtsp rtsp://localhost:8554/cam
```

**View in VLC:**
```
Media → Open Network Stream
rtsp://YOUR_PI_IP:8554/cam
```

---

## 🌐 Remote Access Options

### Option 1: Port Forwarding (Simple)

1. Find your Pi's local IP:
   ```bash
   hostname -I
   ```

2. Log into your router (usually 192.168.1.1 or 192.168.0.1)

3. Forward port 8080:
   - External port: 8080
   - Internal port: 8080
   - Internal IP: YOUR_PI_IP

4. Find your public IP:
   ```bash
   curl ifconfig.me
   ```

5. Share stream:
   ```
   http://YOUR_PUBLIC_IP:8080/
   ```

**Security Note:** Add authentication if streaming publicly!

---

### Option 2: Ngrok (Easy Tunneling)

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar -xzf ngrok-v3-stable-linux-arm64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at ngrok.com and get auth token
ngrok config add-authtoken YOUR_TOKEN

# Start stream
python3 camera_stream.py  # Option 1

# In another terminal, create tunnel
ngrok http 8080

# Share the ngrok URL (e.g., https://abc123.ngrok.io)
```

---

### Option 3: Upload to Your Server

Modify `camera_stream.py` to upload frames to your server:

```python
# In camera_stream.py, add periodic upload
def upload_loop():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        
        upload_to_remote_server(frame)
        time.sleep(1)  # Upload every second

# Start upload thread
threading.Thread(target=upload_loop, daemon=True).start()
```

---

## 🎥 Camera Settings

### Resolution Options

```python
# In camera_stream.py, change CAMERA_RESOLUTION:

# 4K (if supported)
CAMERA_RESOLUTION = (3840, 2160)

# Full HD (Recommended)
CAMERA_RESOLUTION = (1920, 1080)

# HD
CAMERA_RESOLUTION = (1280, 720)

# Standard
CAMERA_RESOLUTION = (640, 480)
```

### Framerate

```python
# Higher FPS = smoother but more bandwidth
CAMERA_FRAMERATE = 60  # Smooth
CAMERA_FRAMERATE = 30  # Recommended
CAMERA_FRAMERATE = 15  # Lower bandwidth
```

### Rotation

```python
# Rotate camera image
CAMERA_ROTATION = 0    # Normal
CAMERA_ROTATION = 90   # Clockwise 90°
CAMERA_ROTATION = 180  # Upside down
CAMERA_ROTATION = 270  # Counter-clockwise 90°
```

---

## 🔧 Auto-Start on Boot

### Method 1: Systemd Service

Create service file:
```bash
sudo nano /etc/systemd/system/camera-stream.service
```

Add:
```ini
[Unit]
Description=Camera Streaming Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/respeaker-ai
ExecStart=/usr/bin/python3 /home/pi/respeaker-ai/camera_stream_auto.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable camera-stream.service
sudo systemctl start camera-stream.service

# Check status
sudo systemctl status camera-stream.service
```

---

## 📱 View Stream on Phone/Tablet

### iOS (Safari):
```
http://YOUR_PI_IP:8080/
```

### Android (Chrome):
```
http://YOUR_PI_IP:8080/
```

### VLC App:
```
Open Network Stream
rtsp://YOUR_PI_IP:8554/cam
```

---

## 🛠️ Troubleshooting

### Camera not detected

```bash
# Check camera connection
libcamera-hello

# If error, check cable and enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Stream freezes

```bash
# Reduce resolution or framerate
# Edit camera_stream.py:
CAMERA_RESOLUTION = (1280, 720)
CAMERA_FRAMERATE = 15
```

### Cannot access from other devices

```bash
# Check firewall
sudo ufw allow 8080

# Check Pi IP
hostname -I

# Make sure devices on same network
```

### High CPU usage

```bash
# Use H.264 encoding (GPU accelerated)
# Install mediamtx and use RTSP method

# Or reduce quality in HTTP method
JPEG_QUALITY = 70  # Lower = less CPU
CAMERA_FRAMERATE = 15
```

---

## 🎯 Use Cases

### 1. Security Camera
```bash
# Continuous streaming
python3 camera_stream.py  # Option 1

# Auto-start on boot (see Auto-Start section)
```

### 2. Boat Camera (Your Use Case!)
```bash
# Stream while sailing
python3 camera_stream.py

# Access via phone:
http://PI_IP:8080/

# Or setup port forwarding for remote access
```

### 3. Wildlife Camera
```bash
# Low power mode
CAMERA_FRAMERATE = 5
CAMERA_RESOLUTION = (640, 480)
```

---

## 📊 Bandwidth Requirements

| Resolution | FPS | Bandwidth (approx) |
|-----------|-----|-------------------|
| 640×480   | 15  | 0.5 Mbps          |
| 1280×720  | 15  | 1.5 Mbps          |
| 1280×720  | 30  | 3 Mbps            |
| 1920×1080 | 15  | 3 Mbps            |
| 1920×1080 | 30  | 6 Mbps            |

**Mobile data:** Use lower resolution/FPS to save data

---

## 🔐 Adding Authentication

To secure your stream, add password protection:

```python
# In camera_stream.py, add to StreamingHandler class:

def do_GET(self):
    # Check authentication
    auth_header = self.headers.get('Authorization')
    if not self.check_auth(auth_header):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Camera"')
        self.end_headers()
        return
    
    # ... rest of code ...

def check_auth(self, auth_header):
    import base64
    if not auth_header:
        return False
    
    try:
        auth_decoded = base64.b64decode(auth_header.split()[1]).decode()
        username, password = auth_decoded.split(':')
        return username == 'admin' and password == 'yourpassword'
    except:
        return False
```

---

## 🎬 Recording While Streaming

Save stream to file:

```bash
# Using libcamera
libcamera-vid -t 0 --width 1920 --height 1080 -o stream.h264 --listen

# Or use the Python script with recording enabled
```

---

## 📚 Additional Resources

- **picamera2 docs**: https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
- **libcamera guide**: https://www.raspberrypi.com/documentation/computers/camera_software.html
- **mediamtx**: https://github.com/bluenviron/mediamtx

---

## ✅ Quick Checklist

- [ ] Camera Module 3 connected to Pi 5
- [ ] Camera enabled in raspi-config
- [ ] picamera2 installed
- [ ] Python script runs without errors
- [ ] Can view stream on Pi (localhost:8080)
- [ ] Can view stream from other device on same network
- [ ] (Optional) Port forwarding configured for remote access
- [ ] (Optional) Authentication added for security

---

**You're ready to stream! 📹🚀**

Run `python3 camera_stream.py` and choose option 1 to start streaming!
