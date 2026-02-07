#!/usr/bin/env python3
"""
Multi-Camera Streaming Server
Supports multiple cameras on different ports
Usage: python camera_stream_multi.py --camera 1 --port 8081
"""

import io
import logging
import socketserver
import threading
import sys
import argparse
from http import server
from threading import Condition

try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
except ImportError:
    print("Error: picamera2 not found. Install with: sudo apt install -y python3-picamera2")
    sys.exit(1)

class StreamingOutput(io.BufferedIOBase):
    """Handles the MJPEG stream output"""
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    """HTTP handler for serving the MJPEG stream"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body>')
            self.wfile.write(f'<h1>Camera {CAMERA_NUMBER} Stream</h1>'.encode())
            self.wfile.write(b'<p><a href="/stream">View Stream</a></p>')
            self.wfile.write(b'</body></html>')
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Age', '0')
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
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress access logs
        return

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Global variables
output = None
CAMERA_NUMBER = 1

def main():
    global output, CAMERA_NUMBER
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Multi-Camera Streaming Server')
    parser.add_argument('--camera', type=int, default=1, help='Camera number (1, 2, 3, etc.)')
    parser.add_argument('--port', type=int, default=8081, help='Port number (8081, 8082, 8083, etc.)')
    parser.add_argument('--width', type=int, default=1280, help='Stream width (default: 1280)')
    parser.add_argument('--height', type=int, default=720, help='Stream height (default: 720)')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second (default: 30)')
    
    args = parser.parse_args()
    
    CAMERA_NUMBER = args.camera
    PORT = args.port
    
    print(f"🎥 Starting Camera {CAMERA_NUMBER} Stream Server")
    print(f"📡 Port: {PORT}")
    print(f"📐 Resolution: {args.width}x{args.height} @ {args.fps}fps")
    print("-" * 50)
    
    # Initialize camera
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(
            main={"size": (args.width, args.height), "format": "RGB888"}
        )
        picam2.configure(config)
        
        output = StreamingOutput()
        encoder = JpegEncoder()
        picam2.start_recording(encoder, FileOutput(output))
        
        print(f"✅ Camera {CAMERA_NUMBER} initialized successfully")
        print(f"📡 Stream URL: http://localhost:{PORT}/stream")
        print(f"🌐 After SSH tunnel: http://echo.cooperativepaddling.com/live{CAMERA_NUMBER}")
        print("-" * 50)
        print("Press Ctrl+C to stop")
        
        # Start HTTP server
        address = ('', PORT)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping Camera {CAMERA_NUMBER} stream...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        try:
            picam2.stop_recording()
            picam2.close()
            print(f"✅ Camera {CAMERA_NUMBER} stopped cleanly")
        except:
            pass

if __name__ == '__main__':
    main()
