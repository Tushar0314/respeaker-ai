#!/bin/bash
# ─────────────────────────────────────────────────────────
# Pi Auto-start Setup
# Creates systemd services for camera, speaker, and LoRa.
# Run once on the Pi:  sudo bash setup_autostart.sh
# ─────────────────────────────────────────────────────────

set -e

USER_NAME="voicechat"
PROJECT_DIR="/home/$USER_NAME/respeaker-ai"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
SYSTEMD_DIR="/etc/systemd/system"

echo "======================================================"
echo " Pi Auto-start Setup"
echo "======================================================"
echo ""

# ── Verify project directory ──────────────────────────────
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[ERROR] Project directory not found: $PROJECT_DIR"
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[ERROR] venv python not found: $VENV_PYTHON"
    echo "  Make sure you have run:  python3 -m venv venv"
    exit 1
fi

echo "[✓] Project directory: $PROJECT_DIR"
echo "[✓] Python venv:       $VENV_PYTHON"
echo ""

# ── 1. Camera Service ─────────────────────────────────────
echo "[1/3] Creating pi-camera.service ..."
cat > "$SYSTEMD_DIR/pi-camera.service" << EOF
[Unit]
Description=Pi Camera Stream
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PYTHON camera_stream_auto.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
echo "[✓] pi-camera.service created"

# ── 2. Speaker / Command Server Service ───────────────────
echo "[2/3] Creating pi-speaker.service ..."
cat > "$SYSTEMD_DIR/pi-speaker.service" << EOF
[Unit]
Description=Pi Command Server (USB Headphone TTS)
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PYTHON pi_command_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
echo "[✓] pi-speaker.service created"

# ── 3. WiFi LoRa MQTT Receiver Service ────────────────────
echo "[3/3] Creating pi-lora.service ..."
cat > "$SYSTEMD_DIR/pi-lora.service" << EOF
[Unit]
Description=Pi WiFi LoRa MQTT Receiver
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PYTHON wifi_lora_receiver.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
echo "[✓] pi-lora.service created"
echo ""

# ── Enable & Start All Services ───────────────────────────
echo "Reloading systemd daemon ..."
systemctl daemon-reload

echo "Enabling services (auto-start on boot) ..."
systemctl enable pi-camera pi-speaker pi-lora

echo "Starting services now ..."
systemctl start pi-camera pi-speaker pi-lora

echo ""
echo "======================================================"
echo " All services are running!"
echo "======================================================"
echo ""
echo " Check status:"
echo "   sudo systemctl status pi-camera"
echo "   sudo systemctl status pi-speaker"
echo "   sudo systemctl status pi-lora"
echo ""
echo " View live logs:"
echo "   journalctl -u pi-camera  -f"
echo "   journalctl -u pi-speaker -f"
echo "   journalctl -u pi-lora    -f"
echo ""
echo " Stop a service:"
echo "   sudo systemctl stop pi-camera"
echo ""
echo " Restart a service:"
echo "   sudo systemctl restart pi-speaker"
echo "======================================================"
