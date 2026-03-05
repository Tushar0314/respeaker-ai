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
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
HOST = "0.0.0.0"   # Listen on all network interfaces
PORT = 5000         # Must match PI_PORT in ESP32 code

# espeak voice settings
VOICE  = "en"   # en, en-us, en-gb
SPEED  = 150    # Words per minute (80-450)
PITCH  = 50     # Pitch (0-99)
VOLUME = 150    # Volume (0-200)
# ─────────────────────────────────────────


def speak(text):
    """Speak text using espeak and route audio to USB speaker (card 2)."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🔊 SPEAKING: \"{text}\"")
    try:
        # Generate speech audio with espeak and pipe to USB speaker (card 2)
        espeak = subprocess.Popen(
            ['espeak', '-v', VOICE, '-s', str(SPEED), '-p', str(PITCH), '-a', str(VOLUME), '--stdout', text],
            stdout=subprocess.PIPE
        )
        subprocess.run(
            ['aplay', '-D', 'plughw:2,0'],
            stdin=espeak.stdout,
            check=True
        )
        espeak.wait()
    except FileNotFoundError:
        print("[ERROR] espeak or aplay not installed.")
        print("  Run:  sudo apt-get install espeak alsa-utils")
    except Exception as e:
        print(f"[ERROR] speak failed: {e}")


class CommandHandler(BaseHTTPRequestHandler):

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

            # Speak the command
            if body:
                speak(body)
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
