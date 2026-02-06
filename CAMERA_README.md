# 📷 Raspberry Pi Camera Streaming

Live video streaming from Raspberry Pi 5 + Camera Module 3

---

## 🚀 Quick Start (On Raspberry Pi)

```bash
# 1. Run setup script
chmod +x setup_camera.sh
./setup_camera.sh

# 2. Start streaming
python3 camera_stream.py
# Choose option 1: Start HTTP Stream

# 3. View stream
# Open browser: http://YOUR_PI_IP:8080/
```

---

## 📱 View Stream

### On Same WiFi:
```
http://192.168.1.XXX:8080/
```
(Replace XXX with your Pi's IP)

### From Internet:
1. Forward port 8080 on your router
2. Visit: `http://YOUR_PUBLIC_IP:8080/`

### On Phone/Tablet:
Just open the URL in any browser!

---

## 🎥 Features

✅ **Live HTTP Stream** - View in any web browser  
✅ **HD Quality** - 1920×1080 @ 30fps  
✅ **Mobile Friendly** - Responsive design  
✅ **Auto-Start** - Can run on boot  
✅ **Remote Upload** - Send frames to server  
✅ **Low Latency** - ~1-2 second delay  

---

## 📂 Files

- **`camera_stream.py`** - Main streaming script (interactive menu)
- **`camera_stream_auto.py`** - Auto-start version (runs on boot)
- **`setup_camera.sh`** - Setup script for Pi
- **`CAMERA_SETUP_GUIDE.md`** - Complete documentation

---

## 🔧 Configuration

Edit `camera_stream.py` or `camera_stream_auto.py`:

```python
# Resolution
CAMERA_RESOLUTION = (1920, 1080)  # Full HD
CAMERA_RESOLUTION = (1280, 720)   # HD (lower bandwidth)

# Frame rate
CAMERA_FRAMERATE = 30  # Smooth
CAMERA_FRAMERATE = 15  # Lower bandwidth

# Rotation
CAMERA_ROTATION = 0    # Normal
CAMERA_ROTATION = 180  # Upside down

# Port
STREAM_PORT = 8080

# Remote server upload
REMOTE_SERVER = "http://echo.cooperativepaddling.com"
UPLOAD_ENABLED = True
UPLOAD_INTERVAL = 5  # Seconds
```

---

## 🤖 Auto-Start on Boot

### Method 1: Systemd Service

```bash
sudo nano /etc/systemd/system/camera-stream.service
```

Add:
```ini
[Unit]
Description=Camera Streaming
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/respeaker-ai
ExecStart=/usr/bin/python3 /home/pi/respeaker-ai/camera_stream_auto.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable camera-stream.service
sudo systemctl start camera-stream.service
```

### Method 2: Cron

```bash
crontab -e
```

Add:
```bash
@reboot sleep 30 && cd /home/pi/respeaker-ai && python3 camera_stream_auto.py >> camera.log 2>&1
```

---

## 🌐 Access URLs

Once running:

| URL | Description |
|-----|-------------|
| `http://PI_IP:8080/` | Main viewer page |
| `http://PI_IP:8080/stream` | Raw MJPEG stream |
| `http://PI_IP:8080/status` | JSON status info |

---

## 🛠️ Troubleshooting

### Camera not working
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot

# Test camera
libcamera-hello
```

### Cannot access from other devices
```bash
# Check Pi IP
hostname -I

# Open firewall
sudo ufw allow 8080

# Make sure on same WiFi network
```

### Stream freezes
- Lower resolution: `CAMERA_RESOLUTION = (1280, 720)`
- Lower framerate: `CAMERA_FRAMERATE = 15`
- Reduce quality: `JPEG_QUALITY = 70`

---

## 📊 Performance

| Resolution | FPS | CPU Usage | Bandwidth |
|-----------|-----|-----------|-----------|
| 640×480   | 15  | ~15%      | 0.5 Mbps  |
| 1280×720  | 30  | ~25%      | 3 Mbps    |
| 1920×1080 | 30  | ~40%      | 6 Mbps    |

Pi 5 handles HD streaming easily!

---

## 🔐 Security

For public access, add authentication:

```python
# See CAMERA_SETUP_GUIDE.md for authentication code
```

Or use VPN/SSH tunnel for secure access.

---

## 💡 Use Cases

### 🚢 Boat Camera
Stream while sailing, check from anywhere

### 🏠 Security Camera
Monitor your home remotely

### 🐾 Pet Camera
Watch your pets while away

### 🌳 Wildlife Camera
Observe nature remotely

---

## 📖 Full Documentation

See **`CAMERA_SETUP_GUIDE.md`** for:
- Complete setup instructions
- Advanced configurations
- Multiple streaming methods (RTSP, etc.)
- Remote access options
- Recording options

---

## 🎯 Integration with Server

To upload frames to your server at `http://echo.cooperativepaddling.com/`:

1. Edit `camera_stream_auto.py`:
   ```python
   UPLOAD_ENABLED = True
   UPLOAD_INTERVAL = 5  # Upload every 5 seconds
   REMOTE_SERVER = "http://echo.cooperativepaddling.com"
   ```

2. Your server should have an endpoint: `POST /upload`
   - Accepts: `multipart/form-data`
   - File field: `image` (JPEG)
   - Data fields: `timestamp`, `device`, `camera`

---

## ✅ Quick Checklist

- [ ] Camera Module 3 connected to Pi 5
- [ ] Camera enabled in raspi-config
- [ ] Ran setup script: `./setup_camera.sh`
- [ ] Can run: `python3 camera_stream.py`
- [ ] Can view stream: `http://PI_IP:8080/`
- [ ] Works from other devices on same network
- [ ] (Optional) Port forwarding for internet access
- [ ] (Optional) Auto-start configured

---

## 🎉 You're Ready!

Your camera is now streaming! Anyone on your WiFi can watch the live feed.

**View stream:** `http://YOUR_PI_IP:8080/`

**Questions?** Check `CAMERA_SETUP_GUIDE.md`

---

**Happy Streaming! 📹✨**
