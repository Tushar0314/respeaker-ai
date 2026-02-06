#!/usr/bin/env python3
"""
Waypoint Receiver - Receives GPS waypoints from React Native app via BLE/Serial
Updates waypoints.json and current_location.json for voice assistant

This script receives data in the format sent by the React Native app:
WP1:lat,lon;WP2:lat,lon;WP3:lat,lon...
"""

import json
import base64
from datetime import datetime
import os
import sys

def parse_waypoint_data(raw_data):
    """
    Parse waypoint data from React Native app format.
    Format: WP1:lat,lon;WP2:lat,lon;WP3:lat,lon
    Example: WP1:37.788250,-122.432400;WP2:37.789000,-122.433000
    """
    try:
        # If data is base64 encoded, decode it first
        try:
            decoded = base64.b64decode(raw_data).decode('utf-8')
            print(f"[Decoded base64] {decoded}")
            raw_data = decoded
        except:
            # Not base64, use as is
            pass
        
        waypoints = []
        
        # Split by semicolon to get each waypoint
        waypoint_strings = raw_data.strip().split(';')
        
        for wp_str in waypoint_strings:
            if ':' not in wp_str:
                continue
                
            # Parse WP1:lat,lon format
            name_part, coords_part = wp_str.split(':', 1)
            
            # Extract lat, lon
            coords = coords_part.split(',')
            if len(coords) != 2:
                continue
            
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
            
            waypoint = {
                'name': name_part.strip(),
                'lat': lat,
                'lon': lon,
                'saved_at': datetime.now().isoformat()
            }
            
            waypoints.append(waypoint)
        
        return waypoints
    
    except Exception as e:
        print(f"[ERROR] Failed to parse waypoint data: {e}")
        return None

def save_waypoints(waypoints):
    """Save waypoints to waypoints.json file."""
    try:
        data = {
            'waypoints': waypoints,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('waypoints.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[✓] Saved {len(waypoints)} waypoints to waypoints.json")
        
        # Also update current_location.json with the first waypoint (source/current position)
        if waypoints:
            current_location = {
                'lat': waypoints[0]['lat'],
                'lon': waypoints[0]['lon'],
                'last_updated': datetime.now().isoformat()
            }
            
            with open('current_location.json', 'w') as f:
                json.dump(current_location, f, indent=2)
            
            print(f"[✓] Updated current_location.json: {waypoints[0]['name']} ({waypoints[0]['lat']}, {waypoints[0]['lon']})")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to save waypoints: {e}")
        return False

def listen_for_waypoints_serial(port='/dev/ttyUSB0', baudrate=115200):
    """
    Listen for waypoint data from serial port (ESP32 via USB).
    Use this if your ESP32 is connected via USB to the Pi.
    """
    try:
        import serial
        
        print(f"[Listening] Waiting for waypoint data on {port}...")
        
        ser = serial.Serial(port, baudrate, timeout=1)
        
        while True:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8').strip()
                
                if raw_data:
                    print(f"\n[Received] {raw_data}")
                    
                    waypoints = parse_waypoint_data(raw_data)
                    
                    if waypoints:
                        print(f"[Parsed] {len(waypoints)} waypoints:")
                        for wp in waypoints:
                            print(f"  - {wp['name']}: {wp['lat']}, {wp['lon']}")
                        
                        if save_waypoints(waypoints):
                            print("[✓] Voice assistant can now speak these waypoints!\n")
    
    except ImportError:
        print("[ERROR] pyserial not installed. Install with: pip install pyserial")
        return False
    except Exception as e:
        print(f"[ERROR] Serial connection failed: {e}")
        return False

def test_with_sample_data():
    """Test the receiver with sample data."""
    print("[TEST MODE] Testing with sample waypoint data...\n")
    
    # Sample data in the format the React Native app sends
    sample_data = "WP1:37.788250,-122.432400;WP2:37.789000,-122.433000;WP3:37.790500,-122.434500"
    
    print(f"[Sample Data] {sample_data}")
    
    waypoints = parse_waypoint_data(sample_data)
    
    if waypoints:
        print(f"\n[Parsed] {len(waypoints)} waypoints:")
        for wp in waypoints:
            print(f"  - {wp['name']}: {wp['lat']}, {wp['lon']}")
        
        if save_waypoints(waypoints):
            print("\n[✓] Files updated! Now try asking the voice assistant 'where am I?'")
            return True
    
    return False

def manual_input():
    """Manually input waypoint data for testing."""
    print("\n[MANUAL INPUT MODE]")
    print("Paste waypoint data from the React Native app")
    print("Format: WP1:lat,lon;WP2:lat,lon;WP3:lat,lon")
    print("(Press Ctrl+D or Ctrl+Z when done)\n")
    
    try:
        raw_data = input("Waypoint data: ").strip()
        
        if not raw_data:
            print("[ERROR] No data provided")
            return False
        
        print(f"\n[Received] {raw_data}")
        
        waypoints = parse_waypoint_data(raw_data)
        
        if waypoints:
            print(f"\n[Parsed] {len(waypoints)} waypoints:")
            for wp in waypoints:
                print(f"  - {wp['name']}: {wp['lat']}, {wp['lon']}")
            
            if save_waypoints(waypoints):
                print("\n[✓] Files updated! Now ask the voice assistant 'where am I?'")
                return True
        else:
            print("[ERROR] Failed to parse waypoint data")
            return False
    
    except KeyboardInterrupt:
        print("\n[Cancelled]")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Main function - choose mode."""
    print("=" * 70)
    print("📍 WAYPOINT RECEIVER - React Native App → Raspberry Pi")
    print("=" * 70)
    print("\nThis script receives waypoint data from your friend's React Native app")
    print("and updates the files so the voice assistant can speak your location.\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_with_sample_data()
        elif sys.argv[1] == 'serial':
            port = sys.argv[2] if len(sys.argv) > 2 else '/dev/ttyUSB0'
            listen_for_waypoints_serial(port)
        elif sys.argv[1] == 'manual':
            manual_input()
        else:
            print(f"Unknown mode: {sys.argv[1]}")
            print("Usage: python waypoint_receiver.py [test|serial|manual]")
    else:
        print("Choose mode:")
        print("  1. Test with sample data")
        print("  2. Manual input")
        print("  3. Listen on serial port (ESP32)")
        print("  4. Exit\n")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            test_with_sample_data()
        elif choice == '2':
            manual_input()
        elif choice == '3':
            port = input("Serial port [/dev/ttyUSB0]: ").strip() or '/dev/ttyUSB0'
            listen_for_waypoints_serial(port)
        elif choice == '4':
            print("Goodbye!")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
