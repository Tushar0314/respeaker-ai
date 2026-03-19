#!/usr/bin/env python3
"""
LoRa Receiver with Text-to-Speech - Receive commands from LoRa32 and speak them
Listens for commands via LoRa and uses espeak for text-to-speech output

Commands format:
- Simple text: "hold" → speaks "hold"
- JSON: {"command": "hold", "message": "Please hold your position"}
- With speed: "SPEED:slow:Please slow down"
"""

import serial
import json
import subprocess
import time
import os
import sys
from datetime import datetime

class LoRaReceiverTTS:
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200, voice='en'):
        """
        Initialize LoRa receiver with text-to-speech.
        
        Args:
            port: Serial port for LoRa module
            baudrate: Communication speed
            voice: Voice for espeak (en, en-us, en-gb, etc.)
        """
        self.port = port
        self.baudrate = baudrate
        self.voice = voice
        self.ser = None
        self.command_history = []
        
        # Check if espeak is available
        self.check_tts()
        self.connect()
    
    def check_tts(self):
        """Check if espeak is installed."""
        try:
            subprocess.run(['espeak', '--version'], 
                         capture_output=True, 
                         check=True)
            print("[✓] espeak is available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARNING] espeak not found. Install with: sudo apt-get install espeak")
            print("[INFO] Text will be printed but not spoken")
            return False
    
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
            time.sleep(2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to LoRa module: {e}")
            print(f"[HINT] Check if LoRa module is connected to {self.port}")
            return False
    
    def speak(self, text, speed=150, pitch=50, volume=100):
        """
        Convert text to speech using espeak.
        
        Args:
            text: Text to speak
            speed: Words per minute (80-450, default 150)
            pitch: Voice pitch (0-99, default 50)
            volume: Volume level (0-200, default 100)
        """
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] 🔊 SPEAKING: \"{text}\"")
            
            # Build espeak command
            cmd = [
                'espeak',
                '-v', self.voice,
                '-s', str(speed),  # Speed
                '-p', str(pitch),  # Pitch
                '-a', str(volume), # Amplitude/volume
                text
            ]
            
            # Execute espeak
            subprocess.run(cmd, check=True)
            
            # Log to history
            self.command_history.append({
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'speed': speed,
                'pitch': pitch
            })
            
            return True
        
        except FileNotFoundError:
            print(f"[PRINT ONLY] {text}")
            return False
        except Exception as e:
            print(f"[ERROR] TTS failed: {e}")
            return False
    
    def parse_command(self, raw_data):
        """
        Parse incoming command and extract text to speak.
        
        Supports multiple formats:
        1. Simple text: "hold"
        2. JSON: {"command": "hold", "message": "Please hold"}
        3. With parameters: "SPEED:slow:Please slow down"
        4. Alert format: "ALERT:Warning:Low battery"
        """
        try:
            # Try JSON format first
            try:
                data = json.loads(raw_data)
                
                text = data.get('message') or data.get('command') or data.get('text')
                speed = data.get('speed', 150)
                pitch = data.get('pitch', 50)
                volume = data.get('volume', 100)
                
                return {
                    'text': text,
                    'speed': speed,
                    'pitch': pitch,
                    'volume': volume,
                    'format': 'JSON'
                }
            
            except json.JSONDecodeError:
                pass
            
            # Check for SPEED: prefix
            if raw_data.startswith('SPEED:'):
                parts = raw_data.split(':', 2)
                if len(parts) == 3:
                    speed_map = {
                        'slow': 100,
                        'normal': 150,
                        'fast': 200,
                        'very_fast': 250
                    }
                    speed = speed_map.get(parts[1].lower(), 150)
                    
                    return {
                        'text': parts[2],
                        'speed': speed,
                        'pitch': 50,
                        'volume': 100,
                        'format': 'SPEED'
                    }
            
            # Check for ALERT: prefix
            if raw_data.startswith('ALERT:'):
                parts = raw_data.split(':', 2)
                if len(parts) == 3:
                    alert_type = parts[1]
                    message = parts[2]
                    
                    # Alerts use higher pitch and slower speed
                    return {
                        'text': f"{alert_type}! {message}",
                        'speed': 130,
                        'pitch': 70,
                        'volume': 150,
                        'format': 'ALERT'
                    }
            
            # Simple text format
            return {
                'text': raw_data,
                'speed': 150,
                'pitch': 50,
                'volume': 100,
                'format': 'SIMPLE'
            }
        
        except Exception as e:
            print(f"[ERROR] Failed to parse command: {e}")
            return None
    
    def listen(self, callback=None):
        """
        Listen for commands from LoRa32 and speak them.
        
        Args:
            callback: Optional function to call with received data
        """
        if not self.ser or not self.ser.is_open:
            print("[ERROR] Serial port not open")
            return False
        
        print(f"\n[LISTENING] Waiting for commands from LoRa32...")
        print("[Press Ctrl+C to stop]\n")
        
        try:
            message_count = 0
            
            while True:
                if self.ser.in_waiting > 0:
                    # Read incoming data
                    raw_data = self.ser.readline().decode('utf-8').strip()
                    
                    if raw_data:
                        message_count += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        print(f"\n{'='*60}")
                        print(f"[{timestamp}] Message #{message_count}")
                        print(f"[RX] Received: {raw_data}")
                        print(f"{'='*60}")
                        
                        # Parse and speak
                        command = self.parse_command(raw_data)
                        
                        if command:
                            print(f"[Format] {command['format']}")
                            print(f"[Text] {command['text']}")
                            print(f"[Speed] {command['speed']} WPM")
                            print(f"[Pitch] {command['pitch']}")
                            
                            self.speak(
                                command['text'],
                                speed=command['speed'],
                                pitch=command['pitch'],
                                volume=command['volume']
                            )
                            
                            # Call callback if provided
                            if callback:
                                callback(raw_data, command)
                        
                        else:
                            print("[ERROR] Could not parse command")
                
                time.sleep(0.1)  # Small delay to prevent CPU overuse
        
        except KeyboardInterrupt:
            print("\n\n[✓] Stopped listening")
            print(f"[Stats] Total messages received: {message_count}")
            return True
        
        except Exception as e:
            print(f"[ERROR] Listening failed: {e}")
            return False
    
    def test_tts(self):
        """Test text-to-speech with sample phrases."""
        print("\n[TEST MODE] Testing text-to-speech...\n")
        
        test_phrases = [
            ("Hold", 150, 50),
            ("Stop", 150, 50),
            ("Go ahead", 150, 50),
            ("Turn left", 150, 50),
            ("Turn right", 150, 50),
            ("Slow down", 130, 50),
            ("Speed up", 170, 50),
            ("Warning! Low battery", 130, 70),
            ("Mission completed successfully", 150, 40)
        ]
        
        for i, (text, speed, pitch) in enumerate(test_phrases, 1):
            print(f"\n[{i}/{len(test_phrases)}] Testing: \"{text}\"")
            self.speak(text, speed=speed, pitch=pitch)
            time.sleep(1)  # Pause between phrases
        
        print("\n[✓] TTS test completed")
    
    def save_history(self, filename='lora_command_history.json'):
        """Save command history to file."""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'history': self.command_history,
                    'total_commands': len(self.command_history),
                    'saved_at': datetime.now().isoformat()
                }, f, indent=2)
            
            print(f"[✓] Saved {len(self.command_history)} commands to {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save history: {e}")
            return False
    
    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[✓] Serial connection closed")

def custom_callback(raw_data, command):
    """Example callback function for custom processing."""
    # You can add custom logic here
    # For example, trigger specific actions based on commands
    
    command_actions = {
        'emergency': lambda: print("[!!!] EMERGENCY MODE ACTIVATED"),
        'stop': lambda: print("[STOP] All operations halted"),
        'home': lambda: print("[HOME] Returning to home position")
    }
    
    text_lower = command['text'].lower()
    
    for keyword, action in command_actions.items():
        if keyword in text_lower:
            action()

def main():
    """Main function."""
    print("=" * 70)
    print("📡 LoRa RECEIVER with TEXT-TO-SPEECH - LoRa32 → Pi5")
    print("=" * 70)
    print("\nReceive commands from LoRa32 and speak them using espeak\n")
    
    # Parse command line arguments
    port = '/dev/ttyAMA0'  # Default GPIO UART on Pi5
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage:")
            print("  python3 lora_receiver_tts.py [mode] [port]")
            print("\nModes:")
            print("  listen  - Listen for commands and speak them")
            print("  test    - Test text-to-speech")
            print("\nExamples:")
            print("  python3 lora_receiver_tts.py listen")
            print("  python3 lora_receiver_tts.py listen /dev/ttyUSB0")
            print("  python3 lora_receiver_tts.py test")
            print("\nCommand Formats from LoRa32:")
            print('  Simple:      "hold"')
            print('  JSON:        {"command": "hold", "message": "Please hold"}')
            print('  With speed:  "SPEED:slow:Please slow down"')
            print('  Alert:       "ALERT:Warning:Low battery"')
            sys.exit(0)
    
    # Get serial port from arguments
    if len(sys.argv) > 2:
        port = sys.argv[2]
    
    # Initialize receiver
    receiver = LoRaReceiverTTS(port)
    
    if not receiver.ser:
        print("\n[FAILED] Could not initialize LoRa receiver")
        print("\nTroubleshooting:")
        print("1. Check LoRa module connection")
        print("2. Verify serial port (ls /dev/tty*)")
        print("3. Enable UART on Pi5 (raspi-config → Interface → Serial)")
        sys.exit(1)
    
    # Determine mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'listen':
            receiver.listen(callback=custom_callback)
        
        elif mode == 'test':
            receiver.test_tts()
        
        else:
            print(f"[ERROR] Unknown mode: {mode}")
            print("Use -h for help")
    
    else:
        # Interactive mode
        print("Choose mode:")
        print("  1. Listen for commands")
        print("  2. Test text-to-speech")
        print("  3. Exit\n")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            receiver.listen(callback=custom_callback)
        
        elif choice == '2':
            receiver.test_tts()
        
        elif choice == '3':
            print("Goodbye!")
        
        else:
            print("Invalid choice")
    
    # Save history and cleanup
    if receiver.command_history:
        receiver.save_history()
    
    receiver.close()

if __name__ == "__main__":
    main()
