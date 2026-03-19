#!/usr/bin/env python3
"""
LoRa Transmitter - Send GPS coordinates from Pi5 to LoRa32
Reads coordinates from current_location.json and waypoints.json
Transmits via serial connection to LoRa module
"""

import serial
import json
import time
import os
import sys
from datetime import datetime

class LoRaTransmitter:
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200):
        """
        Initialize LoRa transmitter.
        
        Args:
            port: Serial port for LoRa module (e.g., /dev/ttyAMA0 for GPIO UART, /dev/ttyUSB0 for USB)
            baudrate: Communication speed (default 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connect()
    
    def connect(self):
        """Establish serial connection to LoRa module."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print(f"[✓] Connected to LoRa module on {self.port}")
            time.sleep(2)  # Wait for LoRa module to initialize
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to LoRa module: {e}")
            print(f"[HINT] Check if LoRa module is connected to {self.port}")
            return False
    
    def read_current_location(self):
        """Read current GPS coordinates from current_location.json."""
        try:
            if not os.path.exists('current_location.json'):
                print("[WARNING] current_location.json not found")
                return None
            
            with open('current_location.json', 'r') as f:
                data = json.load(f)
            
            return {
                'lat': data.get('lat'),
                'lon': data.get('lon'),
                'last_updated': data.get('last_updated')
            }
        except Exception as e:
            print(f"[ERROR] Failed to read current location: {e}")
            return None
    
    def read_waypoints(self):
        """Read all waypoints from waypoints.json."""
        try:
            if not os.path.exists('waypoints.json'):
                print("[WARNING] waypoints.json not found")
                return None
            
            with open('waypoints.json', 'r') as f:
                data = json.load(f)
            
            return data.get('waypoints', [])
        except Exception as e:
            print(f"[ERROR] Failed to read waypoints: {e}")
            return None
    
    def format_coordinate_message(self, lat, lon, name="CURRENT"):
        """
        Format coordinates for LoRa transmission.
        Format: NAME:lat,lon
        Example: CURRENT:37.788250,-122.432400
        """
        return f"{name}:{lat:.6f},{lon:.6f}"
    
    def format_waypoints_message(self, waypoints):
        """
        Format multiple waypoints for LoRa transmission.
        Format: WP1:lat,lon;WP2:lat,lon;WP3:lat,lon
        """
        wp_strings = []
        for wp in waypoints:
            wp_str = f"{wp['name']}:{wp['lat']:.6f},{wp['lon']:.6f}"
            wp_strings.append(wp_str)
        
        return ";".join(wp_strings)
    
    def send_message(self, message):
        """Send message via LoRa."""
        try:
            if not self.ser or not self.ser.is_open:
                print("[ERROR] Serial port not open")
                return False
            
            # Add newline for message termination
            message_bytes = (message + '\n').encode('utf-8')
            
            print(f"[TX] Sending: {message}")
            self.ser.write(message_bytes)
            self.ser.flush()
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False
    
    def send_current_location(self):
        """Send current location to LoRa32."""
        location = self.read_current_location()
        
        if not location:
            print("[SKIP] No location data available")
            return False
        
        message = self.format_coordinate_message(
            location['lat'], 
            location['lon'], 
            "CURRENT"
        )
        
        print(f"📍 Current Location: {location['lat']:.6f}, {location['lon']:.6f}")
        return self.send_message(message)
    
    def send_waypoints(self):
        """Send all waypoints to LoRa32."""
        waypoints = self.read_waypoints()
        
        if not waypoints:
            print("[SKIP] No waypoints available")
            return False
        
        message = self.format_waypoints_message(waypoints)
        
        print(f"📍 Sending {len(waypoints)} waypoints:")
        for wp in waypoints:
            print(f"   - {wp['name']}: {wp['lat']:.6f}, {wp['lon']:.6f}")
        
        return self.send_message(message)
    
    def send_custom_coordinate(self, lat, lon, name="CUSTOM"):
        """Send custom coordinate to LoRa32."""
        message = self.format_coordinate_message(lat, lon, name)
        print(f"📍 Custom Location ({name}): {lat:.6f}, {lon:.6f}")
        return self.send_message(message)
    
    def continuous_transmission(self, interval=10, mode='location'):
        """
        Continuously transmit coordinates at specified interval.
        
        Args:
            interval: Seconds between transmissions
            mode: 'location' for current location, 'waypoints' for all waypoints
        """
        print(f"\n[CONTINUOUS MODE] Transmitting every {interval} seconds")
        print(f"[MODE] {mode}")
        print("[Press Ctrl+C to stop]\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n--- {timestamp} ---")
                
                if mode == 'location':
                    self.send_current_location()
                elif mode == 'waypoints':
                    self.send_waypoints()
                else:
                    print(f"[ERROR] Unknown mode: {mode}")
                
                print(f"[Waiting {interval}s...]")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n[✓] Transmission stopped by user")
    
    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[✓] Serial connection closed")

def main():
    """Main function."""
    print("=" * 70)
    print("📡 LoRa TRANSMITTER - Pi5 → LoRa32")
    print("=" * 70)
    print("\nSend GPS coordinates to LoRa32 device\n")
    
    # Parse command line arguments
    port = '/dev/ttyAMA0'  # Default GPIO UART on Pi5
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage:")
            print("  python3 lora_transmitter.py [mode] [port] [interval]")
            print("\nModes:")
            print("  location    - Send current location once")
            print("  waypoints   - Send all waypoints once")
            print("  continuous  - Continuously send current location")
            print("  auto        - Continuous waypoint transmission")
            print("\nExamples:")
            print("  python3 lora_transmitter.py location")
            print("  python3 lora_transmitter.py waypoints")
            print("  python3 lora_transmitter.py continuous /dev/ttyAMA0 10")
            print("  python3 lora_transmitter.py auto /dev/ttyUSB0 5")
            sys.exit(0)
    
    # Initialize transmitter
    transmitter = LoRaTransmitter(port)
    
    if not transmitter.ser:
        print("\n[FAILED] Could not initialize LoRa transmitter")
        print("\nTroubleshooting:")
        print("1. Check LoRa module connection")
        print("2. Verify serial port (ls /dev/tty*)")
        print("3. Enable UART on Pi5 (raspi-config → Interface → Serial)")
        sys.exit(1)
    
    # Determine mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'location':
            transmitter.send_current_location()
        
        elif mode == 'waypoints':
            transmitter.send_waypoints()
        
        elif mode == 'continuous':
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            if len(sys.argv) > 2:
                transmitter.port = sys.argv[2]
            transmitter.continuous_transmission(interval, 'location')
        
        elif mode == 'auto':
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            if len(sys.argv) > 2:
                transmitter.port = sys.argv[2]
            transmitter.continuous_transmission(interval, 'waypoints')
        
        else:
            print(f"[ERROR] Unknown mode: {mode}")
            print("Use -h for help")
    
    else:
        # Interactive mode
        print("Choose mode:")
        print("  1. Send current location (once)")
        print("  2. Send all waypoints (once)")
        print("  3. Continuous location transmission")
        print("  4. Continuous waypoint transmission")
        print("  5. Exit\n")
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            transmitter.send_current_location()
        
        elif choice == '2':
            transmitter.send_waypoints()
        
        elif choice == '3':
            interval = input("Interval in seconds [10]: ").strip()
            interval = int(interval) if interval else 10
            transmitter.continuous_transmission(interval, 'location')
        
        elif choice == '4':
            interval = input("Interval in seconds [10]: ").strip()
            interval = int(interval) if interval else 10
            transmitter.continuous_transmission(interval, 'waypoints')
        
        elif choice == '5':
            print("Goodbye!")
        
        else:
            print("Invalid choice")
    
    # Cleanup
    transmitter.close()

if __name__ == "__main__":
    main()
