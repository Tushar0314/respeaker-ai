# Camera Stream Troubleshooting Guide

## Quick Fix Steps

### On Raspberry Pi:

1. **Terminal 1 - Start Camera Stream:**
   ```bash
   cd ~/respeaker-ai
   python camera_stream.py
   # Select option 1: Start Streaming Server
   ```

2. **Terminal 2 - Test Locally First:**
   ```bash
   # Make script executable
   chmod +x test_tunnel.sh
   
   # Run diagnostic
   ./test_tunnel.sh
   ```

3. **Terminal 2 - Start SSH Tunnel (if tests pass):**
   ```bash
   # Make script executable
   chmod +x start_tunnel.sh
   
   # Start improved tunnel
   ./start_tunnel.sh
   ```
   
   **Look for this message:**
   ```
   debug1: remote forward success for: listen 8080, connect localhost:8080
   ```

### On Server (echo.cooperativepaddling.com):

1. **SSH to server:**
   ```bash
   ssh root@echo.cooperativepaddling.com
   ```

2. **Copy and run test script:**
   ```bash
   # Copy the content from server_test.sh and run it
   bash server_test.sh
   ```

3. **Manual tests:**
   ```bash
   # Test if tunnel is forwarding
   curl -I http://localhost:8080/stream
   
   # Should see: HTTP/1.0 200 OK
   # Should see: Content-Type: multipart/x-mixed-replace
   
   # Check what's listening on port 8080
   netstat -tlnp | grep 8080
   
   # Restart nginx
   systemctl restart nginx
   
   # Check nginx logs
   tail -f /var/log/nginx/error.log
   ```

## Common Issues

### Issue 1: SSH Tunnel Not Connected
**Symptoms:** Server test shows port 8080 not listening

**Fix:**
- On Pi, kill old tunnel: `pkill -f "ssh -R 8080"`
- Use improved script: `./start_tunnel.sh`
- Check for "remote forward success" message

### Issue 2: Camera Not Streaming
**Symptoms:** Local test fails on Pi

**Fix:**
- Restart camera: Ctrl+C in Terminal 1, then `python camera_stream.py`
- Select option 1 (Start Streaming Server)
- Verify with: `curl http://localhost:8080/`

### Issue 3: Nginx Not Proxying
**Symptoms:** localhost:8080 works but public URL doesn't

**Fix on server:**
```bash
# Check nginx config
cat /etc/nginx/sites-available/default

# Should have this location block:
# location /stream {
#     proxy_pass http://localhost:8080/stream;
#     proxy_buffering off;
#     ...
# }

# Restart nginx
systemctl restart nginx
```

### Issue 4: Firewall Blocking
**Fix on server:**
```bash
# Allow port 80
ufw allow 80/tcp

# Check firewall status
ufw status
```

## Verification Checklist

- [ ] Camera stream running on Pi (Terminal 1)
- [ ] Local test passes: `curl http://localhost:8080/stream` on Pi returns 200
- [ ] SSH tunnel shows "remote forward success" message
- [ ] Server test passes: `curl http://localhost:8080/stream` on server returns 200
- [ ] Nginx running on server: `systemctl status nginx`
- [ ] Public URL works: `curl http://echo.cooperativepaddling.com/stream` on server
- [ ] Browser shows stream at http://echo.cooperativepaddling.com/

## Debug Commands

**On Pi:**
```bash
# Check if stream is running
curl -I http://localhost:8080/stream

# Check SSH processes
ps aux | grep ssh

# Check network
netstat -an | grep 8080
```

**On Server:**
```bash
# Check tunnel connection
netstat -tlnp | grep 8080

# Test stream locally
curl -I http://localhost:8080/stream

# Test through nginx
curl -I http://localhost/stream

# Check nginx logs
tail -20 /var/log/nginx/error.log
tail -20 /var/log/nginx/access.log
```

## Expected Success Output

**On Pi (test_tunnel.sh):**
```
✅ SSH tunnel process is running
✅ Camera stream is running on localhost:8080
✅ Can reach echo.cooperativepaddling.com
```

**On Server (server_test.sh):**
```
✅ Nginx is running
✅ Port 8080 is listening
✅ Stream accessible at localhost:8080/stream (HTTP 200)
✅ Nginx configuration is valid
```

**On Browser:**
- Navigate to: http://echo.cooperativepaddling.com/
- Should see: Live video stream from Pi camera
- Green "🟢 LIVE" indicator
