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
import re
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
USB_SPEAKER_KEYWORDS = ["usb", "respeaker", "seeed", "jbl", "headset", "speaker"]
MONITOR_KEYWORDS = ["hdmi", "monitor", "vc4"]
# ─────────────────────────────────────────


def _parse_aplay_devices(aplay_output):
    """Parse `aplay -l` output into a list of ALSA device records."""
    devices = []
    pattern = re.compile(r"card\s+(\d+):\s+(.+?)\s+\[(.+?)\],\s+device\s+(\d+):\s+(.+)")

    for line in aplay_output.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        card_number = match.group(1)
        card_short_name = match.group(2).strip()
        card_description = match.group(3).strip()
        device_number = match.group(4)
        device_description = match.group(5).strip()
        devices.append({
            "card": card_number,
            "device": device_number,
            "card_short_name": card_short_name,
            "card_description": card_description,
            "device_description": device_description,
        })

    return devices


def _score_playback_device(device):
    """Prefer USB speaker devices and strongly de-prioritize monitor outputs."""
    haystack = " ".join([
        device["card_short_name"],
        device["card_description"],
        device["device_description"],
    ]).lower()

    if any(keyword in haystack for keyword in USB_SPEAKER_KEYWORDS):
        return 3
    if any(keyword in haystack for keyword in MONITOR_KEYWORDS):
        return 0
    return 1


def select_speaker_device():
    """Return a USB speaker ALSA device and refuse monitor/HDMI-only routing."""
    try:
        result = subprocess.run(['aplay', '-l'], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        LOGGER.warning("aplay not installed; cannot inspect playback devices")
        return None
    except Exception as e:
        LOGGER.warning("could not list playback devices: %s", e)
        return None

    devices = _parse_aplay_devices(result.stdout)
    if not devices:
        LOGGER.warning("no playback devices found in `aplay -l` output")
        return None

    ranked_devices = sorted(devices, key=_score_playback_device, reverse=True)
    usb_candidates = []
    for device in ranked_devices:
        haystack = " ".join([
            device["card_short_name"],
            device["card_description"],
            device["device_description"],
        ]).lower()
        if any(keyword in haystack for keyword in MONITOR_KEYWORDS):
            continue
        if any(keyword in haystack for keyword in USB_SPEAKER_KEYWORDS):
            usb_candidates.append(device)

    if not usb_candidates:
        LOGGER.error("no USB speaker device found; refusing to use monitor/HDMI output")
        for device in ranked_devices:
            LOGGER.info(
                "available playback device: card=%s device=%s (%s / %s / %s)",
                device["card"],
                device["device"],
                device["card_short_name"],
                device["card_description"],
                device["device_description"],
            )
        return None

    chosen = usb_candidates[0]
    chosen_device = f"plughw:{chosen['card']},{chosen['device']}"
    LOGGER.info(
        "selected playback device: %s (%s / %s / %s)",
        chosen_device,
        chosen["card_short_name"],
        chosen["card_description"],
        chosen["device_description"],
    )
    return chosen_device


def log_audio_status(stage):
    """Log speaker device info before startup/speech."""
    LOGGER.info("audio status check: %s", stage)

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


def speak_via_device(text, device):
    """Speak text by piping espeak output into a specific ALSA playback device."""
    espeak_cmd = [
        'espeak', '--stdout',
        '-v', VOICE,
        '-s', str(SPEED),
        '-p', str(PITCH),
        '-a', str(VOLUME),
        text,
    ]
    aplay_cmd = ['aplay', '-q', '-D', device]

    LOGGER.info("speech route: %s -> %s", ' '.join(espeak_cmd[:-1] + ['<text>']), ' '.join(aplay_cmd))

    espeak_process = subprocess.Popen(espeak_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        aplay_process = subprocess.Popen(aplay_cmd, stdin=espeak_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        espeak_process.stdout.close()
        aplay_stdout, aplay_stderr = aplay_process.communicate()
        espeak_stderr = espeak_process.stderr.read() if espeak_process.stderr else b''
        espeak_return = espeak_process.wait()

        if espeak_return != 0:
            LOGGER.warning("espeak exited with code %s", espeak_return)
        if aplay_process.returncode != 0:
            LOGGER.warning("aplay exited with code %s", aplay_process.returncode)
        if espeak_stderr:
            LOGGER.info("espeak stderr: %s", espeak_stderr.decode('utf-8', errors='replace').strip())
        if aplay_stdout:
            LOGGER.info("aplay stdout: %s", aplay_stdout.decode('utf-8', errors='replace').strip())
        if aplay_stderr:
            LOGGER.info("aplay stderr: %s", aplay_stderr.decode('utf-8', errors='replace').strip())

        return aplay_process.returncode == 0 and espeak_return == 0
    finally:
        try:
            if espeak_process.stderr:
                espeak_process.stderr.close()
        except Exception:
            pass


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
        log_audio_status("before speech")
        selected_device = select_speaker_device()
        if selected_device is None:
            elapsed = time.time() - start_time
            LOGGER.error('[%s] SPEAKING ABORTED: no USB speaker found after %.2fs', timestamp, elapsed)
            return

        success = speak_via_device(text, selected_device)
        elapsed = time.time() - start_time
        LOGGER.info('[%s] SPEAKING END: completed in %.2fs', timestamp, elapsed)
        LOGGER.info("speech completed via explicit playback device: %s", selected_device)
        if not success:
            LOGGER.warning("speech may not have played cleanly on %s", selected_device)
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
