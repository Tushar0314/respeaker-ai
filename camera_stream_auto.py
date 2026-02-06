#!/usr/bin/env python3
"""
Auto-start camera streaming for Raspberry Pi 5
Automatically starts streaming when Pi boots
Uploads frames to remote server at http://echo.cooperativepaddling.com/
"""

import io
import time
import threading
import requests
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# ====== CONFIGURATION ======
CAMERA_RESOLUTION = (1920, 1080)  # Full HD
CAMERA_FRAMERATE = 30
CAMERA_ROTATION = 0
STREAM_PORT = 8080
JPEG_QUALITY = 85

# Remote server configuration
REMOTE_SERVER = "http://echo.cooperativepaddling.com/upload.php"
UPLOAD_ENABLED = True  # Set to True to upload to server
UPLOAD_INTERVAL = 0.5  # Upload every 0.5 seconds

print("=" * 70)
print("📷 AUTO-START CAMERA STREAMER")
print(f"   Streaming on port {STREAM_PORT}")
print(f"   Remote server: {REMOTE_SERVER}")
print("=" * 70)

# ====== CAMERA SETUP ======
try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    print("[✓] picamera2 loaded")
    CAMERA_AVAILABLE = True
except ImportError:
    print("[!] picamera2 not installed")
    CAMERA_AVAILABLE = False
    exit(1)

# ====== STREAMING OUTPUT ======
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()
    
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# ====== HTTP HANDLER ======
class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pi Camera - Live</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        background: #0a0a0a;
                        color: #fff;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                        padding: 10px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        border-radius: 12px;
                        margin-bottom: 15px;
                        text-align: center;
                    }}
                    h1 {{
                        font-size: 24px;
                        margin-bottom: 5px;
                    }}
                    .status {{
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        background: rgba(0,255,0,0.1);
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 14px;
                        margin-top: 10px;
                    }}
                    .live-dot {{
                        width: 10px;
                        height: 10px;
                        background: #0f0;
                        border-radius: 50%;
                        animation: pulse 2s infinite;
                    }}
                    @keyframes pulse {{
                        0%, 100% {{ opacity: 1; }}
                        50% {{ opacity: 0.3; }}
                    }}
                    .video-container {{
                        position: relative;
                        background: #000;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
                    }}
                    img {{
                        width: 100%;
                        height: auto;
                        display: block;
                    }}
                    .info {{
                        background: #1a1a1a;
                        padding: 15px;
                        border-radius: 12px;
                        margin-top: 15px;
                    }}
                    .info-row {{
                        display: flex;
                        justify-content: space-between;
                        padding: 8px 0;
                        border-bottom: 1px solid #333;
                    }}
                    .info-row:last-child {{
                        border-bottom: none;
                    }}
                    .label {{
                        color: #999;
                        font-size: 13px;
                    }}
                    .value {{
                        color: #fff;
                        font-weight: 600;
                        font-size: 13px;
                    }}
                    @media (max-width: 768px) {{
                        body {{ padding: 8px; }}
                        h1 {{ font-size: 20px; }}
                        .header {{ padding: 15px; }}
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📷 Raspberry Pi Camera</h1>
                    <div class="status">
                        <div class="live-dot"></div>
                        LIVE STREAM
                    </div>
                </div>
                
                <div class="video-container">
                    <img src="/stream" alt="Live Camera Feed">
                </div>
                
                <div class="info">
                    <div class="info-row">
                        <span class="label">Resolution</span>
                        <span class="value">{CAMERA_RESOLUTION[0]}×{CAMERA_RESOLUTION[1]}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Frame Rate</span>
                        <span class="value">{CAMERA_FRAMERATE} FPS</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Device</span>
                        <span class="value">Pi 5 + Camera Module 3</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Stream URL</span>
                        <span class="value" style="font-size: 11px;">http://YOUR_PI_IP:{STREAM_PORT}/stream</span>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/stream':
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
            except:
                pass
        
        elif self.path == '/status':
            # JSON status endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            status = {
                'status': 'online',
                'resolution': CAMERA_RESOLUTION,
                'framerate': CAMERA_FRAMERATE,
                'timestamp': datetime.now().isoformat(),
                'upload_enabled': UPLOAD_ENABLED,
                'remote_server': REMOTE_SERVER
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        return

class StreamingServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# ====== UPLOAD TO SERVER ======
def upload_to_server():
    """Periodically upload frames to remote server."""
    last_upload = 0
    
    while True:
        try:
            current_time = time.time()
            
            if current_time - last_upload >= UPLOAD_INTERVAL:
                with output.condition:
                    output.condition.wait(timeout=1)
                    if output.frame:
                        frame = output.frame
                
                # Try to upload
                try:
                    files = {'image': ('camera.jpg', frame, 'image/jpeg')}
                    data = {
                        'timestamp': datetime.now().isoformat(),
                        'device': 'raspberry-pi-5',
                        'camera': 'module-3',
                        'resolution': f'{CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}'
                    }
                    
                    response = requests.post(
                        f"{REMOTE_SERVER}/upload",
                        files=files,
                        data=data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"[✓] Uploaded frame to server")
                    else:
                        print(f"[!] Upload failed: {response.status_code}")
                
                except requests.exceptions.RequestException as e:
                    print(f"[!] Upload error: {e}")
                
                last_upload = current_time
            
            time.sleep(0.1)
        
        except Exception as e:
            print(f"[Upload Error] {e}")
            time.sleep(5)

# ====== MAIN ======
def main():
    global output, picam2
    
    print("\n[Camera] Initializing...")
    
    # Initialize camera
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": CAMERA_RESOLUTION, "format": "RGB888"},
        controls={"FrameRate": CAMERA_FRAMERATE}
    )
    picam2.configure(config)
    
    if CAMERA_ROTATION != 0:
        picam2.set_controls({"Transform": CAMERA_ROTATION})
    
    # Create output
    output = StreamingOutput()
    
    # Start camera
    picam2.start_recording(JpegEncoder(q=JPEG_QUALITY), FileOutput(output))
    print("[✓] Camera started")
    
    # Start upload thread if enabled
    if UPLOAD_ENABLED:
        print(f"[Upload] Starting upload thread (every {UPLOAD_INTERVAL}s)")
        upload_thread = threading.Thread(target=upload_to_server, daemon=True)
        upload_thread.start()
    
    # Get IP address
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "localhost"
    
    print(f"\n{'=' * 70}")
    print("📺 CAMERA STREAM IS LIVE!")
    print(f"{'=' * 70}")
    print(f"\n🌐 View in browser:")
    print(f"   http://{local_ip}:{STREAM_PORT}/")
    print(f"\n📹 Direct stream URL:")
    print(f"   http://{local_ip}:{STREAM_PORT}/stream")
    print(f"\n📊 Status API:")
    print(f"   http://{local_ip}:{STREAM_PORT}/status")
    
    if UPLOAD_ENABLED:
        print(f"\n📤 Uploading to: {REMOTE_SERVER}")
        print(f"   Interval: {UPLOAD_INTERVAL} seconds")
    
    print(f"\n{'=' * 70}\n")
    
    # Start HTTP server
    try:
        address = ('', STREAM_PORT)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Stopping] Shutting down...")
    finally:
        picam2.stop_recording()
        print("[✓] Camera stopped")

if __name__ == "__main__":
    main()
