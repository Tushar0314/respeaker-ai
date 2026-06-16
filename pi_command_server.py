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
import logging
import time
from pathlib import Path
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
HOST = "0.0.0.0"   # Listen on all network interfaces
PORT = 5000         # Must match PI_PORT in ESP32 code
LOG_FILE = Path(__file__).with_name("pi_command_server.log")

# espeak voice settings
VOICE  = "en"   # en, en-us, en-gb
SPEED  = 150    # Words per minute (80-450)
PITCH  = 50     # Pitch (0-99)
VOLUME = 150    # Volume (0-200)
# ─────────────────────────────────────────


def set_audio_output_to_jack():
    """Force the Pi's audio output to the 3.5mm jack."""
    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                ['amixer', 'cset', 'numid=3', '1'],
                check=True,
                capture_output=True,
                text=True
            )
            LOGGER.info("audio output set to 3.5mm jack (attempt %s)", attempt)
            if result.stdout:
                LOGGER.info("amixer stdout: %s", result.stdout.strip())
            if result.stderr:
                LOGGER.info("amixer stderr: %s", result.stderr.strip())
            return True
        except FileNotFoundError:
            LOGGER.warning("amixer not installed; cannot force jack output")
            return False
        except Exception as e:
            LOGGER.warning("could not set audio output to jack (attempt %s): %s", attempt, e)
            time.sleep(0.5)

    return False


def log_audio_status(stage):
    """Log the current audio routing and speaker device info."""
    LOGGER.info("audio status check: %s", stage)

    try:
        route = subprocess.run(
            ['amixer', 'cget', 'numid=3'],
            check=False,
            capture_output=True,
            text=True
        )
        if route.stdout:
            LOGGER.info("amixer route: %s", route.stdout.strip())
        if route.stderr:
            LOGGER.info("amixer route stderr: %s", route.stderr.strip())
    except FileNotFoundError:
        LOGGER.warning("amixer not installed; cannot read audio route")
    except Exception as e:
        LOGGER.warning("could not read audio route: %s", e)

    try:
        devices = subprocess.run(
            ['aplay', '-l'],
            check=False,
            capture_output=True,
            text=True
        )
        if devices.stdout:
            LOGGER.info("aplay -l output:\n%s", devices.stdout.strip())
        if devices.stderr:
            LOGGER.info("aplay -l stderr: %s", devices.stderr.strip())
    except FileNotFoundError:
        LOGGER.warning("aplay not installed; cannot list playback devices")
    except Exception as e:
        LOGGER.warning("could not list playback devices: %s", e)


def setup_logging():
    """Configure console and file logging for the server."""
    logger = logging.getLogger("pi_command_server")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


LOGGER = setup_logging()


def speak(text):
    """Speak text using espeak."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    LOGGER.info('[%s] SPEAKING START: "%s"', timestamp, text)
    start_time = time.time()
    try:
        if not set_audio_output_to_jack():
            LOGGER.warning("continuing to speak even though jack output could not be confirmed")
        result = subprocess.run(
            ['espeak', '-v', VOICE, '-s', str(SPEED), '-p', str(PITCH), '-a', str(VOLUME), text],
            check=True,
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start_time
        LOGGER.info('[%s] SPEAKING END: completed in %.2fs', timestamp, elapsed)
        LOGGER.info("speech command return code: %s", result.returncode)
        if result.stdout:
            LOGGER.info("espeak stdout: %s", result.stdout.strip())
        if result.stderr:
            LOGGER.info("espeak stderr: %s", result.stderr.strip())
    except FileNotFoundError:
        LOGGER.error("espeak not installed. Run: sudo apt-get install espeak")
    except Exception as e:
        LOGGER.exception("speak failed: %s", e)


class CommandHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Handle POST /command from ESP32."""
        request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_ip, client_port = self.client_address
        try:
            if self.path == "/command":
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8').strip()

                LOGGER.info("%s command received from %s:%s on %s", request_time, client_ip, client_port, self.path)
                LOGGER.info("command body: %s", body if body else "<empty>")

                # Send OK back to ESP32
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                LOGGER.info("response sent to %s:%s (200 OK)", client_ip, client_port)

                # Speak the command
                if body:
                    LOGGER.info("speaking received command")
                    speak(body)
                else:
                    LOGGER.warning("received empty command body")
            else:
                LOGGER.warning("received POST for unsupported path: %s from %s:%s", self.path, client_ip, client_port)
                self.send_response(404)
                self.end_headers()
        except Exception:
            LOGGER.exception("unexpected error while handling POST from %s:%s", client_ip, client_port)
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        LOGGER.info("HTTP %s - %s", self.address_string(), format % args)


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
    set_audio_output_to_jack()
    log_audio_status("startup")
    pi_ip = get_pi_ip()

    LOGGER.info("=" * 55)
    LOGGER.info("Pi Command Server")
    LOGGER.info("ESP32 LoRa Receiver -> HTTP -> Pi -> Speaker")
    LOGGER.info("=" * 55)
    LOGGER.info("Pi IP Address : %s", pi_ip)
    LOGGER.info("Listening on  : http://%s:%s/command", pi_ip, PORT)
    LOGGER.info("Tell your friend to set in ESP32 code:")
    LOGGER.info('    #define PI_IP   "%s"', pi_ip)
    LOGGER.info('    #define PI_PORT  %s', PORT)
    LOGGER.info('    #define PI_PATH  "/command"')
    LOGGER.info("Waiting for commands...")
    LOGGER.info("Press Ctrl+C to stop")
    LOGGER.info("Log file: %s", LOG_FILE)

    server = HTTPServer((HOST, PORT), CommandHandler)
    try:
        LOGGER.info("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("server stopped by keyboard interrupt")
        server.server_close()


if __name__ == "__main__":
    main()
