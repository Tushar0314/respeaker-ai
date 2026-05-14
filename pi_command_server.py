#!/usr/bin/env python3
"""
Pi Command Server
Receives HTTP POST from friend's ESP32 LoRa receiver and speaks the command.

Flow:
  ESP32 receives "hold" from LoRa
      → ESP32 sends HTTP POST to Pi (port 5000 /command)
      → Pi speaks "hold" via espeak
"""

import subprocess
import sys
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
HOST = "0.0.0.0"   # Listen on all network interfaces
PORT = 5000         # Must match PI_PORT in ESP32 code
CAMERA_SERVICE = "pi-camera"

# espeak voice settings
VOICE  = "en"   # en, en-us, en-gb
SPEED  = 150    # Words per minute (80-450)
PITCH  = 50     # Pitch (0-99)
VOLUME = 150    # Volume (0-200)
# ─────────────────────────────────────────


def get_audio_device():
    """Detect USB audio card number from aplay -l."""
    try:
        import re
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'usb' in line.lower() and 'card' in line.lower():
                match = re.search(r'card (\d+)', line.lower())
                if match:
                    card_num = match.group(1)
                    print(f"[Audio] Found USB headphone on card {card_num}")
                    return f"plughw:{card_num},0"
        print("[Audio] USB card not found, using default")
        return "default"
    except Exception as e:
        print(f"[Audio] Device detection failed: {e}, using default")
        return "default"


def speak(text):
    """Speak text using espeak routed to USB wired headphone."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🔊 SPEAKING: \"{text}\"")
    try:
        audio_device = get_audio_device()
        espeak = subprocess.Popen(
            ['espeak', '-v', VOICE, '-s', str(SPEED), '-p', str(PITCH), '-a', str(VOLUME), '--stdout', text],
            stdout=subprocess.PIPE
        )
        subprocess.run(
            ['aplay', '-D', audio_device],
            stdin=espeak.stdout,
            check=True
        )
        espeak.wait()
        print("[✓ Speech completed]")
    except FileNotFoundError:
        print("[ERROR] espeak or aplay not installed.")
        print("  Run:  sudo apt-get install espeak alsa-utils")
    except Exception as e:
        print(f"[ERROR] speak failed: {e}")


def get_service_active(service_name):
    """Return True if systemd service is active."""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() == 'active'
    except Exception as e:
        print(f"[WARN] Could not read service state for {service_name}: {e}")
        return False


def run_service_action(service_name, action):
    """Run a systemctl action and return (ok, message)."""
    try:
        result = subprocess.run(
            ['systemctl', action, service_name],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return True, f"{service_name} {action} OK"
        err = (result.stderr or result.stdout or "unknown error").strip()
        return False, f"{service_name} {action} failed: {err}"
    except Exception as e:
        return False, f"{service_name} {action} exception: {e}"


def handle_camera_command(command_text):
    """Map incoming text to camera service actions."""
    cmd = command_text.strip().lower()
    if cmd in {"camera", "camera status", "status camera"}:
        active = get_service_active(CAMERA_SERVICE)
        return True, "camera is running" if active else "camera is stopped"

    if cmd in {"camera on", "camera start", "start camera", "start recording"}:
        ok, msg = run_service_action(CAMERA_SERVICE, 'start')
        return ok, "camera started" if ok else msg

    if cmd in {"camera off", "camera stop", "stop camera", "stop recording"}:
        ok, msg = run_service_action(CAMERA_SERVICE, 'stop')
        return ok, "camera stopped" if ok else msg

    if cmd in {"camera restart", "restart camera"}:
        ok, msg = run_service_action(CAMERA_SERVICE, 'restart')
        return ok, "camera restarted" if ok else msg

    return None, None


class CommandHandler(BaseHTTPRequestHandler):

    def _write_json(self, status_code, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Health endpoint for quick connectivity tests from ESP32/Pi."""
        if self.path == "/health":
            camera_active = get_service_active(CAMERA_SERVICE)
            self._write_json(200, {
                "ok": True,
                "service": "pi_command_server",
                "camera_active": camera_active,
                "timestamp": datetime.now().isoformat()
            })
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        """Handle POST /command from ESP32."""
        if self.path == "/command":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8').strip()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*45}")
            print(f"[{timestamp}] Message from ESP32!")
            print(f"[Command] {body}")
            print(f"{'='*45}")

            # Send OK back to ESP32
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

            # Handle camera control command, otherwise speak incoming text.
            if body:
                camera_ok, camera_message = handle_camera_command(body)
                if camera_ok is None:
                    speak(body)
                else:
                    print(f"[Camera] {camera_message}")
                    speak(camera_message)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logs (we have our own)


def get_pi_ip():
    """Get Pi's IP address to show user."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def main():
    pi_ip = get_pi_ip()

    print("=" * 55)
    print("📡 Pi Command Server")
    print("   ESP32 LoRa Receiver → HTTP → Pi → 🔊 Speaker")
    print("=" * 55)
    print(f"\n✅ Pi IP Address : {pi_ip}")
    print(f"✅ Listening on  : http://{pi_ip}:{PORT}/command")
    print(f"✅ Health check  : http://{pi_ip}:{PORT}/health")
    print(f"\n👉 Tell your friend to set in ESP32 code:")
    print(f'     #define PI_IP   "{pi_ip}"')
    print(f'     #define PI_PORT  {PORT}')
    print(f'     #define PI_PATH  "/command"')
    print(f"\n[Waiting for commands...]\n[Press Ctrl+C to stop]\n")

    server = HTTPServer((HOST, PORT), CommandHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[✓] Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
