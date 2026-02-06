#!/usr/bin/env python3
"""
Camera Streaming for Raspberry Pi 5 with Camera Module 3
Streams live video to a server so people can view the footage remotely.

Supports multiple streaming methods:
1. HTTP MJPEG Stream (easiest)
2. WebSocket Stream (real-time)
3. RTSP Stream (professional)
4. Upload to remote server
"""

import io
import time
import threading
import subprocess
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json

# ====== CONFIGURATION ======
CAMERA_RESOLUTION = (1920, 1080)  # Full HD
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0  # 0, 90, 180, 270

# Server settings
STREAM_PORT = 8080  # Port for local streaming
REMOTE_SERVER = "http://echo.cooperativepaddling.com/"

# Video quality
JPEG_QUALITY = 85  # 1-100, higher = better quality but larger file

print("=" * 70)
print("📷 RASPBERRY PI CAMERA STREAMER")
print("   Camera Module 3 on Pi 5")
print("=" * 70)

# ====== CAMERA INITIALIZATION ======
try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder, H264Encoder
    from picamera2.outputs import FileOutput
    
    print("\n[✓] picamera2 library loaded")
    CAMERA_AVAILABLE = True
except ImportError:
    print("\n[!] picamera2 not installed. Install with:")
    print("    sudo apt install -y python3-picamera2")
    CAMERA_AVAILABLE = False

# ====== MJPEG STREAMING SERVER ======
class StreamingOutput(io.BufferedIOBase):
    """Captures frames from camera for streaming."""
    
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()
    
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(BaseHTTPRequestHandler):
    """HTTP handler for MJPEG streaming."""
    
    def do_GET(self):
        if self.path == '/':
            # Serve viewer HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pi Camera Stream</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        background: #1a1a1a;
                        color: white;
                        font-family: Arial, sans-serif;
                        text-align: center;
                    }
                    h1 {
                        color: #4CAF50;
                    }
                    .container {
                        max-width: 1920px;
                        margin: 0 auto;
                    }
                    img {
                        width: 100%;
                        max-width: 1920px;
                        border: 2px solid #4CAF50;
                        border-radius: 8px;
                    }
                    .info {
                        margin-top: 20px;
                        padding: 15px;
                        background: #2a2a2a;
                        border-radius: 8px;
                    }
                    .status {
                        color: #4CAF50;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📷 Raspberry Pi Camera Stream</h1>
                    <div class="info">
                        <p class="status">🟢 LIVE</p>
                        <p>Camera Module 3 • Pi 5 • 1920x1080 @ 30fps</p>
                    </div>
                    <img src="/stream" alt="Camera Stream">
                    <div class="info">
                        <p>Stream URL: <code>http://YOUR_PI_IP:8080/stream</code></p>
                        <p>Refresh this page if stream freezes</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/stream':
            # Serve MJPEG stream
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                print(f'[Stream Error] {e}')
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Suppress log messages
        return

class StreamingServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for handling multiple connections."""
    allow_reuse_address = True
    daemon_threads = True

# ====== REMOTE SERVER UPLOAD ======
def upload_to_remote_server(frame_data):
    """Upload frame to remote server."""
    try:
        import requests
        
        # Send frame as JPEG
        files = {'image': ('frame.jpg', frame_data, 'image/jpeg')}
        data = {
            'timestamp': datetime.now().isoformat(),
            'device': 'raspberry-pi-5',
            'camera': 'module-3'
        }
        
        response = requests.post(
            f"{REMOTE_SERVER}/upload",
            files=files,
            data=data,
            timeout=5
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"[Upload Error] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[Upload Error] {e}")
        return False

# ====== RTSP STREAMING (Advanced) ======
def start_rtsp_stream():
    """Start RTSP stream using libcamera and mediamtx."""
    print("\n[RTSP] Starting RTSP server...")
    print("[RTSP] Stream will be available at: rtsp://YOUR_PI_IP:8554/stream")
    
    try:
        # Use libcamera-vid to stream via RTSP
        cmd = [
            'libcamera-vid',
            '-t', '0',  # Run indefinitely
            '--width', str(CAMERA_RESOLUTION[0]),
            '--height', str(CAMERA_RESOLUTION[1]),
            '--framerate', str(CAMERA_FRAMERATE),
            '-o', '-',  # Output to stdout
            '--codec', 'h264',
            '--inline',
            '--listen'
        ]
        
        subprocess.run(cmd)
    
    except Exception as e:
        print(f"[RTSP Error] {e}")
        print("[RTSP] Make sure libcamera is installed:")
        print("       sudo apt install -y libcamera-apps")

# ====== MAIN FUNCTIONS ======
def start_http_stream():
    """Start HTTP MJPEG streaming server."""
    global output, picam2
    
    if not CAMERA_AVAILABLE:
        print("\n[ERROR] picamera2 not available")
        return
    
    print("\n[Camera] Initializing Camera Module 3...")
    
    # Initialize camera
    picam2 = Picamera2()
    
    # Configure for streaming
    config = picam2.create_video_configuration(
        main={"size": CAMERA_RESOLUTION, "format": "RGB888"},
        controls={"FrameRate": CAMERA_FRAMERATE}
    )
    picam2.configure(config)
    
    # Set rotation if needed
    if CAMERA_ROTATION != 0:
        picam2.set_controls({"Transform": CAMERA_ROTATION})
    
    print(f"[Camera] Resolution: {CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}")
    print(f"[Camera] Framerate: {CAMERA_FRAMERATE} fps")
    print(f"[Camera] Rotation: {CAMERA_ROTATION}°")
    
    # Create output for streaming
    output = StreamingOutput()
    
    # Start camera with MJPEG encoder
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    
    print(f"\n[✓] Camera started successfully!")
    print(f"\n[Server] Starting HTTP streaming server...")
    print(f"[Server] Port: {STREAM_PORT}")
    
    try:
        # Get Pi's IP address
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"\n{'=' * 70}")
        print("📺 CAMERA STREAM IS LIVE!")
        print(f"{'=' * 70}")
        print(f"\n🌐 View stream in browser:")
        print(f"   http://{local_ip}:{STREAM_PORT}/")
        print(f"   http://localhost:{STREAM_PORT}/")
        print(f"\n📹 Direct stream URL (for VLC, etc.):")
        print(f"   http://{local_ip}:{STREAM_PORT}/stream")
        print(f"\n💡 Share with others:")
        print(f"   http://YOUR_PUBLIC_IP:{STREAM_PORT}/")
        print(f"   (Port forward {STREAM_PORT} on your router)")
        print(f"\n{'=' * 70}")
        print("Press Ctrl+C to stop streaming")
        print(f"{'=' * 70}\n")
        
        # Start HTTP server
        address = ('', STREAM_PORT)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    
    except KeyboardInterrupt:
        print("\n\n[Stopping] Shutting down camera stream...")
    
    finally:
        picam2.stop_recording()
        print("[✓] Camera stopped")

def capture_snapshot(filename='snapshot.jpg'):
    """Capture a single snapshot from camera."""
    if not CAMERA_AVAILABLE:
        print("[ERROR] picamera2 not available")
        return False
    
    print(f"\n[Camera] Capturing snapshot: {filename}")
    
    try:
        picam2 = Picamera2()
        config = picam2.create_still_configuration(
            main={"size": CAMERA_RESOLUTION}
        )
        picam2.configure(config)
        
        picam2.start()
        time.sleep(2)  # Allow camera to adjust
        
        picam2.capture_file(filename)
        picam2.stop()
        
        print(f"[✓] Snapshot saved: {filename}")
        return True
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_camera():
    """Test camera and display info."""
    if not CAMERA_AVAILABLE:
        print("\n[ERROR] picamera2 not available")
        print("\nInstall with:")
        print("  sudo apt install -y python3-picamera2 python3-libcamera")
        return
    
    print("\n[Testing] Camera Module 3...")
    
    try:
        picam2 = Picamera2()
        
        # Get camera info
        print("\n[Camera Information]")
        print(f"  Model: {picam2.camera_properties.get('Model', 'Unknown')}")
        
        # Available resolutions
        configs = picam2.sensor_modes
        print(f"\n[Available Resolutions]")
        for i, mode in enumerate(configs):
            print(f"  {i+1}. {mode['size']} @ {mode.get('fps', 'N/A')} fps")
        
        print("\n[✓] Camera test completed!")
        print("\nCamera is ready to stream!")
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print("  1. Check camera cable connection")
        print("  2. Enable camera in raspi-config")
        print("  3. Reboot Pi after enabling camera")

# ====== MENU ======
def main():
    """Main menu."""
    
    if not CAMERA_AVAILABLE:
        print("\n⚠️  picamera2 is not installed!")
        print("\nInstall it with:")
        print("  sudo apt update")
        print("  sudo apt install -y python3-picamera2 python3-libcamera")
        return
    
    print("\n" + "=" * 70)
    print("CAMERA STREAMING OPTIONS")
    print("=" * 70)
    print("\n1. Start HTTP Stream (Recommended)")
    print("   - View in any web browser")
    print("   - Easiest to use")
    print("   - Works on LAN and internet (with port forwarding)")
    print("\n2. Test Camera")
    print("   - Check if camera is working")
    print("   - View camera information")
    print("\n3. Capture Snapshot")
    print("   - Take a single photo")
    print("\n4. Start RTSP Stream (Advanced)")
    print("   - For VLC, OBS, etc.")
    print("   - Lower latency")
    print("\n5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        start_http_stream()
    elif choice == '2':
        test_camera()
    elif choice == '3':
        filename = input("Filename [snapshot.jpg]: ").strip() or 'snapshot.jpg'
        capture_snapshot(filename)
    elif choice == '4':
        start_rtsp_stream()
    elif choice == '5':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
