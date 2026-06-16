# Complete Setup Steps - Camera Stream to Server

## Step-by-Step Guide

### PART 1: ON RASPBERRY PI

#### Step 1: Setup SSH Connection to Server (One-time setup)

In any terminal on Pi, run:
```bash
ssh bhaven@164.92.89.157
```

When you see:
```
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Type: `yes` and press Enter

Then enter password: `bhaven.1`

Once connected, type: `exit` to close the connection.

This saves the server fingerprint so future connections work automatically.

---

#### Step 2: Start Camera Stream

**Terminal 1 on Pi:**
```bash
cd ~/respeaker-ai
python camera_stream.py
```

Select: `1` (Start Streaming Server)

You should see:
```
🎥 Camera streaming server started
📡 Stream URL: http://localhost:8080/stream
```

**Leave this terminal running!**

---

#### Step 3: Test Camera Locally (Optional)

**Terminal 2 on Pi:**
```bash
cd ~/respeaker-ai
./test_tunnel.sh
```

Should show:
```
✅ Camera stream is running on localhost:8080
```

---

#### Step 4: Start SSH Tunnel

**Terminal 2 on Pi:**
```bash
cd ~/respeaker-ai
./start_tunnel.sh
```

When asked: `Continue anyway? (y/n)` → Type `y` and press Enter

Enter password when prompted: `bhaven.1`

**IMPORTANT:** Look for this message:
```
debug1: remote forward success for: listen 8080, connect localhost:8080
```

If you see that → tunnel is working! **Leave this terminal running!**

---

### PART 2: ON YOUR SERVER (DigitalOcean)

#### Step 5: SSH to Server

From your Mac or another Pi terminal:
```bash
ssh bhaven@164.92.89.157
```

Password: `bhaven.1`

---

#### Step 6: Verify Tunnel is Connected

Once logged into server, run:
```bash
curl -I http://localhost:8080/stream
```

**Expected output:**
```
HTTP/1.0 200 OK
Content-Type: multipart/x-mixed-replace; boundary=FRAME
```

If you see this → Great! Tunnel is working!

If you get "Connection refused" → Go back to Pi and restart the tunnel (Step 4)

---

#### Step 7: Check Nginx Configuration

On the server, run:
```bash
sudo cat /etc/nginx/sites-available/default
```

**Make sure it has this section and keep buffering disabled for any live stream route:**
```nginx
location /stream {
    proxy_pass http://localhost:8080/stream;
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
}
```

If you expose a different stream path, apply the same no-buffering settings there too. Any buffering in nginx can add several seconds of delay even when the Pi is capturing fresh frames.

**If it's missing or wrong**, create the config:
```bash
sudo nano /etc/nginx/sites-available/default
```

Add the location block above inside the `server` block.

Save: `Ctrl+O`, Enter, then `Ctrl+X`

---

#### Step 8: Restart Nginx

```bash
sudo systemctl restart nginx
```

Check status:
```bash
sudo systemctl status nginx
```

Should show: `active (running)`

---

#### Step 9: Test Public Access

From the server, test:
```bash
curl -I http://echo.cooperativepaddling.com/stream
```

Should return: `HTTP/1.1 200 OK`

---

### PART 3: VIEW ON YOUR LAPTOP

#### Step 10: Open Browser

Open your browser and go to:
```
http://echo.cooperativepaddling.com/
```

You should see:
- 🟢 LIVE indicator (green)
- Live video from your Pi camera

If you see the error message instead, go back and check:
1. Camera is running on Pi (Terminal 1)
2. SSH tunnel is connected (Terminal 2 shows "remote forward success")
3. Server can access localhost:8080 (Step 6)
4. Nginx is running (Step 8)

---

## Quick Reference

### Keep These Running on Pi:
- **Terminal 1:** `python camera_stream.py` (option 1)
- **Terminal 2:** `./start_tunnel.sh` (enter password: bhaven.1)

### If Something Stops Working:

**Restart Camera (Pi Terminal 1):**
```bash
Ctrl+C
python camera_stream.py
# Select 1
```

**Restart Tunnel (Pi Terminal 2):**
```bash
Ctrl+C
./start_tunnel.sh
# Enter password: bhaven.1
```

**Restart Nginx (On Server):**
```bash
sudo systemctl restart nginx
```

---

## Troubleshooting

### Error: "Connection refused" on server
- Make sure camera is running on Pi
- Make sure SSH tunnel is connected on Pi

### Error: "502 Bad Gateway" in browser
- SSH tunnel is not connected
- Restart tunnel on Pi (Terminal 2)

### Error: "Host key verification failed"
- Run: `ssh bhaven@164.92.89.157`
- Type: `yes` when asked
- Enter password, then `exit`

### Camera not starting
```bash
# On Pi
sudo usermod -aG video voicechat
# Logout and login again
```

### Need to auto-start on boot
See the main README for systemd service setup.
