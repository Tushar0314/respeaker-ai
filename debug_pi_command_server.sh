#!/bin/bash
set -e

echo "========================================"
echo "Pi Command Server Diagnostics"
echo "========================================"

echo "\n[1] Network addresses"
hostname -I || true

PI_IP=$(hostname -I | awk '{print $1}')
if [ -z "$PI_IP" ]; then
  PI_IP="127.0.0.1"
fi

echo "Detected Pi IP: $PI_IP"

echo "\n[2] Service status (pi-speaker)"
sudo systemctl status pi-speaker --no-pager || true

echo "\n[3] Last logs (pi-speaker)"
sudo journalctl -u pi-speaker -n 80 --no-pager || true

echo "\n[4] Port check (:5000)"
ss -ltnp | grep :5000 || true

echo "\n[5] Local health check"
curl -sS -m 3 http://127.0.0.1:5000/health || echo "Local health check failed"

echo "\n[6] LAN health check"
curl -sS -m 3 "http://$PI_IP:5000/health" || echo "LAN health check failed"

echo "\n[7] Test command POST"
curl -sS -m 3 -X POST http://127.0.0.1:5000/command -d "hold" || echo "POST test failed"

echo "\n[8] UFW status (if installed)"
sudo ufw status || true

echo "\n========================================"
echo "Done."
echo "If ESP32 still shows -1, verify ESP32 uses:"
echo "  PI_IP   = $PI_IP"
echo "  PI_PORT = 5000"
echo "  PI_PATH = /command"
echo "========================================"
