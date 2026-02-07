# Multi-Camera Setup Guide

## Overview

This setup allows you to stream multiple cameras:
- **Main Dashboard**: http://echo.cooperativepaddling.com/
- **Camera 1**: http://echo.cooperativepaddling.com/live1
- **Camera 2**: http://echo.cooperativepaddling.com/live2
- **Camera 3**: http://echo.cooperativepaddling.com/live3
- And so on...

## Port Assignments

Each camera uses a unique port:
- Camera 1: Port 8081
- Camera 2: Port 8082
- Camera 3: Port 8083
- etc.

---

## Setup Instructions

### PART 1: Raspberry Pi Setup (For Each Camera)

#### For Camera 1:

**Terminal 1 - Start Camera:**
```bash
cd ~/respeaker-ai
./start_camera.sh 1
```

**Terminal 2 - Start SSH Tunnel:**
```bash
cd ~/respeaker-ai
./start_tunnel_multi.sh 1
```
Password: `bhaven.1`

---

#### For Camera 2 (if you have it):

**Terminal 3 - Start Camera:**
```bash
cd ~/respeaker-ai
./start_camera.sh 2
```

**Terminal 4 - Start SSH Tunnel:**
```bash
cd ~/respeaker-ai
./start_tunnel_multi.sh 2
```
Password: `bhaven.1`

---

#### For Camera 3 (if you have it):

**Terminal 5 - Start Camera:**
```bash
cd ~/respeaker-ai
./start_camera.sh 3
```

**Terminal 6 - Start SSH Tunnel:**
```bash
cd ~/respeaker-ai
./start_tunnel_multi.sh 3
```
Password: `bhaven.1`

---

### PART 2: Server Configuration

#### Step 1: SSH to Server
```bash
ssh bhaven@164.92.89.157
```
Password: `bhaven.1`

#### Step 2: Upload HTML Files

Create the dashboard page:
```bash
sudo nano /var/www/html/index.html
```

Paste the content from `index_multi.html` (from this repo)

Save: `Ctrl+O`, Enter, `Ctrl+X`

Create the camera viewer page:
```bash
sudo nano /var/www/html/camera.html
```

Paste the content from `live_camera.html` (from this repo)

Save: `Ctrl+O`, Enter, `Ctrl+X`

#### Step 3: Configure Nginx

Edit nginx config:
```bash
sudo nano /etc/nginx/sites-available/default
```

Replace the entire file with this:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm;

    server_name echo.cooperativepaddling.com;

    # Main dashboard
    location / {
        try_files $uri $uri/ =404;
    }

    # Camera 1 page
    location /live1 {
        alias /var/www/html/camera.html;
        default_type text/html;
    }

    # Camera 1 stream
    location /stream1 {
        proxy_pass http://localhost:8081/stream;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # Camera 2 page
    location /live2 {
        alias /var/www/html/camera.html;
        default_type text/html;
    }

    # Camera 2 stream
    location /stream2 {
        proxy_pass http://localhost:8082/stream;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # Camera 3 page
    location /live3 {
        alias /var/www/html/camera.html;
        default_type text/html;
    }

    # Camera 3 stream
    location /stream3 {
        proxy_pass http://localhost:8083/stream;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

#### Step 4: Test and Restart Nginx

```bash
# Test configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

#### Step 5: Verify on Server

For each camera that's running, test:
```bash
# Camera 1
curl -I http://localhost:8081/stream

# Camera 2
curl -I http://localhost:8082/stream

# Camera 3
curl -I http://localhost:8083/stream
```

Should return: `HTTP/1.0 200 OK`

---

## Access Your Cameras

### Dashboard (Shows all cameras):
```
http://echo.cooperativepaddling.com/
```

### Individual Cameras:
```
http://echo.cooperativepaddling.com/live1
http://echo.cooperativepaddling.com/live2
http://echo.cooperativepaddling.com/live3
```

---

## Customization

### Update Camera Names and Locations

Edit `index_multi.html` around line 125:
```javascript
const cameras = [
    { number: 1, name: "Front Door", location: "Main Entrance", url: "/live1" },
    { number: 2, name: "Backyard", location: "Garden Area", url: "/live2" },
    { number: 3, name: "Garage", location: "Parking", url: "/live3" },
];
```

Upload the updated file to server:
```bash
sudo nano /var/www/html/index.html
# Paste updated content
```

---

## Quick Start (1 Camera Only)

If you only have Camera 1 right now:

**On Pi:**
```bash
# Terminal 1
./start_camera.sh 1

# Terminal 2
./start_tunnel_multi.sh 1
```

**On Server:**
- Upload HTML files
- Configure nginx (include all 3 cameras for future use)
- Restart nginx

**Access:**
- Dashboard: http://echo.cooperativepaddling.com/
- Camera 1: http://echo.cooperativepaddling.com/live1

Cameras 2 and 3 will show as "OFFLINE" until you connect them.

---

## Adding More Cameras Later

1. **On Pi:** Run `./start_camera.sh <number>` and `./start_tunnel_multi.sh <number>`
2. **On Server:** No changes needed (if you already added all locations in nginx)
3. **Refresh Dashboard:** The new camera will appear automatically

---

## Troubleshooting

### Camera shows as OFFLINE on dashboard
- Check if camera script is running on Pi
- Check if SSH tunnel is connected
- Verify on server: `curl http://localhost:808X/stream` (replace X with camera number)

### Stream not loading
- Restart nginx: `sudo systemctl restart nginx`
- Check nginx logs: `sudo tail -f /var/log/nginx/error.log`

### SSH tunnel disconnects
- Make sure you're using `start_tunnel_multi.sh` (has keepalive settings)
- Check network connection on Pi

---

## Auto-Start on Boot

To make cameras start automatically when Pi boots, see systemd service setup in main troubleshooting guide.
