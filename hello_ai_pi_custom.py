#!/usr/bin/env python3
"""
Voice Assistant for Raspberry Pi with ReSpeaker 4-Mic Array
Optimized for best performance with external JBL speaker
Works with Gemini AI for intelligent responses
Location-aware with Google Maps integration
"""

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import os
import subprocess
import google.generativeai as genai
import time
import math
from datetime import datetime

# ====== CONFIGURATION ======
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'
GOOGLE_MAPS_API_KEY = 'AIzaSyD0ewRk6lzFRYkts_mcy6UFAF6lfdazvd8'
MODEL_DIR = "models/en"

# ReSpeaker 4-Mic Array Settings (OPTIMIZED)
RESPEAKER_RATE = 16000  # 16kHz optimal for ReSpeaker and speech recognition
RESPEAKER_CHANNELS = 1  # Mono (use first channel of ReSpeaker)
RESPEAKER_CHUNK = 1024  # Audio chunk size

print("=" * 60)
print("🎤 Voice Assistant - Raspberry Pi + ReSpeaker 4-Mic Array")
print("🔊 Output: JBL Speaker")
print("=" * 60)

# ====== STEP 1: AUTO-DETECT RESPEAKER ======
def find_respeaker_device():
    """Auto-detect ReSpeaker 4-Mic Array device (USB or GPIO-connected)."""
    print("\n[STEP 1] Detecting ReSpeaker 4-Mic Array...")
    devices = sd.query_devices()
    
    print(f"\nAvailable audio devices ({len(devices)} total):")
    for idx, device in enumerate(devices):
        channels = device.get('max_input_channels', 0)
        if channels > 0:
            print(f"  [{idx}] {device['name']} - Input: {channels} channels, SR: {device.get('default_samplerate', 'N/A')} Hz")
    
    # Check for GPIO-connected ReSpeaker via ALSA
    print("\n[Checking for GPIO-connected ReSpeaker via ALSA...]")
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True, timeout=5)
        alsa_output = result.stdout.lower()
        
        if 'seeed' in alsa_output or 'ac10x' in alsa_output or 'respeaker' in alsa_output:
            print("✓ GPIO-connected ReSpeaker detected via ALSA!")
            print("  Using ALSA device for audio input")
            return 'hw:0,0'  # Default ALSA device for ReSpeaker
    except Exception as e:
        print(f"[ALSA check info] {e}")
    
    # Look for ReSpeaker via sounddevice (USB connection)
    for idx, device in enumerate(devices):
        name = device['name'].lower()
        if device['max_input_channels'] >= 1:
            # Check for ReSpeaker patterns
            if any(pattern in name for pattern in ['respeaker', 'seeed', 'usb audio', 'usb device']):
                print(f"\n✓ Found ReSpeaker at device index: {idx}")
                print(f"  Name: {device['name']}")
                print(f"  Input channels: {device['max_input_channels']}")
                return idx
    
    # If not auto-detected, ask user to select
    print("\n⚠ ReSpeaker not auto-detected via sounddevice. Please select the ReSpeaker device:")
    try:
        idx = int(input("Enter device index number (or 'hw:0,0' for GPIO): "))
        if isinstance(idx, int) and 0 <= idx < len(devices):
            print(f"✓ Selected device {idx}: {devices[idx]['name']}")
            return idx
    except:
        pass
    
    # Default to pulse/default if available
    print("\n⚠ Using default audio device (pulse)")
    return 10  # Default device index from test output

# ====== STEP 2: SETUP TEXT-TO-SPEECH ======
def say(text):
    """Speak text using espeak (optimized for Raspberry Pi)."""
    if not text or text.strip() == "":
        return
    
    print(f"\n[SPEAKING] {text[:100]}{'...' if len(text) > 100 else ''}")
    
    # Try espeak first (fastest on Pi)
    try:
        subprocess.run(
            ['espeak', '-s', '150', '-a', '200', text],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60
        )
        print("[✓ Speech completed]")
        return
    except Exception as e:
        print(f"[espeak error] {e}")
    
    # Fallback to pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        print("[✓ Speech completed via pyttsx3]")
    except Exception as e:
        print(f"[pyttsx3 error] {e}")

# ====== STEP 3: INITIALIZE GEMINI ======
def init_gemini():
    """Initialize Gemini API with best model."""
    print("\n[STEP 2] Connecting to Gemini AI...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List available models
        available_models = list(genai.list_models())
        print(f"  Available models: {len(available_models)}")
        
        # Prefer faster models for Pi
        preferred_models = [
            'models/gemini-2.0-flash',
            'models/gemini-2.5-flash',
            'models/gemini-flash-latest',
        ]
        
        # Find best model
        for preferred in preferred_models:
            for m in available_models:
                if m.name == preferred:
                    if hasattr(m, 'supported_generation_methods'):
                        if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                            print(f"  ✓ Using model: {m.name}")
                            return m.name
        
        # Fallback
        for m in available_models:
            if hasattr(m, 'supported_generation_methods') and 'generateContent' in getattr(m, 'supported_generation_methods', []):
                print(f"  ✓ Using model: {m.name}")
                return m.name
        
        print("  ✗ No suitable model found")
        return None
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

# ====== STEP 4: SPEECH RECOGNITION ======
def listen_once(mic_index, rate=RESPEAKER_RATE, seconds=3.0):
    """Capture audio from ReSpeaker (USB or GPIO) and recognize speech."""
    q = queue.Queue()
    
    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"[Audio warning] {status}")
        q.put(bytes(indata))
    
    try:
        # Load Vosk model
        model = Model(MODEL_DIR)
        rec = KaldiRecognizer(model, rate)
        rec.Reset()
        
        frames_needed = int(rate * seconds)
        got = 0
        
        # Handle both sounddevice (numeric) and ALSA (string) devices
        if isinstance(mic_index, str):
            # ALSA device (hw:0,0)
            print(f"[Using ALSA device: {mic_index}]")
            try:
                # Use arecord for ALSA devices
                import wave
                import tempfile
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp_path = tmp.name
                
                subprocess.run(
                    ['arecord', '-D', mic_index, '-f', 'S16_LE', '-r', str(rate), '-c', '1', '-d', str(int(seconds)+1), tmp_path],
                    timeout=int(seconds)+5,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Read the recorded audio
                with open(tmp_path, 'rb') as f:
                    f.read(44)  # Skip WAV header
                    while True:
                        buf = f.read(RESPEAKER_CHUNK * 2)
                        if not buf:
                            break
                        if rec.AcceptWaveform(buf):
                            break
                
                os.unlink(tmp_path)
            except Exception as e:
                print(f"[ALSA recording error] {e}")
                return ""
        else:
            # Sounddevice device (numeric index)
            # Capture audio
            with sd.RawInputStream(
                device=mic_index,
                samplerate=rate,
                blocksize=RESPEAKER_CHUNK,
                dtype='int16',
                channels=RESPEAKER_CHANNELS,
                callback=audio_callback
            ):
                while got < frames_needed:
                    try:
                        buf = q.get(timeout=1)
                        got += len(buf) // 2
                        
                        if rec.AcceptWaveform(buf):
                            break
                    except queue.Empty:
                        break
        
        # Get final result
        result = json.loads(rec.FinalResult())
        text = result.get("text", "").strip()
        return text
        
    except Exception as e:
        print(f"[Listen error] {e}")
        return ""

# ====== STEP 5: GET LOCATION ======
def get_current_location():
    """Get current location - first check waypoints, then fall back to Google/IP."""
    # First, check if we have waypoints from the boat
    waypoint_location = get_waypoint_location()
    if waypoint_location:
        return waypoint_location
    
    # Otherwise use Google Maps/IP location
    try:
        import requests
        
        # Method 1: Try Google Maps Geolocation API (WiFi-based)
        geolocation_url = 'https://www.googleapis.com/geolocation/v1/geolocate'
        geolocation_params = {'key': GOOGLE_MAPS_API_KEY}
        
        geo_response = requests.post(
            geolocation_url,
            params=geolocation_params,
            json={},
            timeout=5
        )
        
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            lat = geo_data.get('location', {}).get('lat')
            lon = geo_data.get('location', {}).get('lng')
            
            if lat and lon:
                # Use Reverse Geocoding to get address
                geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
                geocode_params = {
                    'latlng': f'{lat},{lon}',
                    'key': GOOGLE_MAPS_API_KEY
                }
                
                geocode_response = requests.get(geocode_url, params=geocode_params, timeout=5)
                
                if geocode_response.status_code == 200:
                    geocode_data = geocode_response.json()
                    
                    if geocode_data.get('results'):
                        result = geocode_data['results'][0]
                        
                        # Extract city, region, country from address components
                        city = None
                        region = None
                        country = None
                        
                        for component in result.get('address_components', []):
                            types = component.get('types', [])
                            if 'locality' in types:
                                city = component.get('long_name')
                            elif 'administrative_area_level_1' in types:
                                region = component.get('long_name')
                            elif 'country' in types:
                                country = component.get('long_name')
                        
                        return {
                            'lat': lat,
                            'lon': lon,
                            'city': city or 'Unknown',
                            'region': region,
                            'country': country,
                            'formatted_address': result.get('formatted_address', '')
                        }
        
        # Fallback: IP-based location
        print("[Location] Google API failed, using IP-based fallback...")
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'formatted_address': f"{data.get('city')}, {data.get('country_name')}"
            }
    except Exception as e:
        print(f"[Location error] {e}")
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in meters using Haversine formula."""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_waypoint_location():
    """Read waypoints from file sent by friend's app."""
    try:
        waypoints_file = 'waypoints.json'
        current_location_file = 'current_location.json'
        
        if not os.path.exists(waypoints_file):
            return None
        
        with open(waypoints_file, 'r') as f:
            data = json.load(f)
        
        waypoints = data.get('waypoints', [])
        if not waypoints:
            return None
        
        # Try to get current location from file (updated by the app)
        current_lat = None
        current_lon = None
        
        if os.path.exists(current_location_file):
            try:
                with open(current_location_file, 'r') as f:
                    current_data = json.load(f)
                    current_lat = current_data.get('lat')
                    current_lon = current_data.get('lon')
            except:
                pass
        
        # If we have current location, find nearest waypoint
        if current_lat and current_lon:
            nearest_wp = None
            min_distance = float('inf')
            
            for wp in waypoints:
                distance = calculate_distance(current_lat, current_lon, wp['lat'], wp['lon'])
                if distance < min_distance:
                    min_distance = distance
                    nearest_wp = wp
            
            if nearest_wp:
                return {
                    'lat': nearest_wp['lat'],
                    'lon': nearest_wp['lon'],
                    'waypoint_name': nearest_wp['name'],
                    'waypoint_count': len(waypoints),
                    'is_waypoint': True,
                    'all_waypoints': waypoints,
                    'distance_to_waypoint': min_distance,
                    'current_lat': current_lat,
                    'current_lon': current_lon
                }
        
        # Otherwise, return the most recent waypoint
        latest_wp = waypoints[-1]
        
        return {
            'lat': latest_wp['lat'],
            'lon': latest_wp['lon'],
            'waypoint_name': latest_wp['name'],
            'waypoint_count': len(waypoints),
            'is_waypoint': True,
            'all_waypoints': waypoints
        }
    except Exception as e:
        print(f"[Waypoint error] {e}")
        return None

def handle_location_query(user_text):
    """Handle location-based queries in many different ways."""
    # All the different ways to ask about location
    location_patterns = [
        'where am i',
        'where are we',
        'what is my location',
        'what is our location',
        'tell me my location',
        'tell me where i am',
        'tell me where we are',
        'current location',
        'my location',
        'our location',
        'where',
        'location',
        'gps',
        'coordinates',
        'position',
        'waypoint',
        'destination',
        'route',
    ]
    
    user_lower = user_text.lower().strip()
    
    # Check if user is asking about location
    if any(pattern in user_lower for pattern in location_patterns) or user_lower == 'where':
        location = get_current_location()
        
        if location:
            # Check if this is waypoint data from friend's app
            if location.get('is_waypoint'):
                wp_name = location.get('waypoint_name', 'Unknown')
                lat = location.get('lat')
                lon = location.get('lon')
                wp_count = location.get('waypoint_count', 0)
                distance = location.get('distance_to_waypoint')
                
                # Create natural response about waypoints
                if distance is not None:
                    # We know the distance to the waypoint
                    if distance < 10:
                        response = f"You are at waypoint {wp_name}. "
                    elif distance < 50:
                        response = f"You are very close to waypoint {wp_name}, about {int(distance)} meters away. "
                    elif distance < 500:
                        response = f"You are near waypoint {wp_name}, approximately {int(distance)} meters away. "
                    else:
                        distance_km = distance / 1000
                        response = f"The nearest waypoint is {wp_name}, about {distance_km:.1f} kilometers away. "
                else:
                    # No current location, just report the waypoint
                    response = f"Your destination waypoint is {wp_name}. "
                
                # Add coordinates if requested
                if 'coordinate' in user_lower or 'gps' in user_lower:
                    response += f"Coordinates: latitude {lat:.4f}, longitude {lon:.4f}. "
                
                # Add waypoint list if multiple waypoints
                if wp_count > 1:
                    response += f"You have {wp_count} waypoints in your route. "
                    
                    # List all waypoints if specifically asked
                    if 'all' in user_lower or 'list' in user_lower or 'show' in user_lower:
                        all_wps = location.get('all_waypoints', [])
                        wp_list = ", ".join([wp['name'] for wp in all_wps])
                        response += f"Your waypoints are: {wp_list}."
                
                return response
            
            # Regular location (Google/IP-based)
            elif location.get('city'):
                city = location.get('city', 'unknown')
                region = location.get('region', '')
                country = location.get('country', '')
                
                # Create natural response
                if region and region != city:
                    return f"You are in {city}, {region}, {country}."
                else:
                    return f"You are in {city}, {country}."
        
        return "I cannot find the location right now."
    
    return None  # Not a location query

# ====== STEP 6: GET GEMINI RESPONSE ======
def get_ai_response(prompt, model_name, user_text=""):
    """Get response from Gemini AI with location awareness."""
    if not model_name:
        return "AI model not available"
    
    # First check if this is a location query
    location_response = handle_location_query(user_text)
    if location_response:
        return location_response
    
    # Get location context for general queries
    location = get_current_location()
    
    # Build enhanced prompt with location context
    if location and location.get('city'):
        enhanced_prompt = f"""User said: "{prompt}"
Current location: {location['city']}, {location.get('region', '')}, {location.get('country', '')}

Reply with one concise spoken sentence suitable for text-to-speech."""
    else:
        enhanced_prompt = f"""User said: "{prompt}"

Reply with one concise spoken sentence suitable for text-to-speech."""
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(enhanced_prompt, stream=False)
        return response.text
    except Exception as e:
        return f"Error getting response: {e}"

# ====== STEP 6: MAIN LOOP ======
def main():
    """Main voice assistant loop."""
    
    # Step 1: Find ReSpeaker
    mic_index = find_respeaker_device()
    if mic_index is None:
        print("\n✗ Cannot find ReSpeaker device. Exiting.")
        return
    
    # Step 2: Initialize Gemini
    model_name = init_gemini()
    if not model_name:
        print("\n✗ Cannot connect to Gemini. Check API key. Exiting.")
        return
    
    # Step 3: Check Vosk model
    if not os.path.exists(MODEL_DIR):
        print(f"\n✗ Vosk model not found at {MODEL_DIR}")
        print("  Download: wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        return
    
    # Step 4: Ready to go!
    print("\n" + "=" * 60)
    print("[✓ SETUP COMPLETE]")
    print(f"  Microphone: ReSpeaker (device {mic_index})")
    print(f"  Sample Rate: {RESPEAKER_RATE} Hz")
    print(f"  AI Model: {model_name}")
    print(f"  Speaker: JBL (via Pi audio output)")
    print("=" * 60)
    
    # Test audio
    print("\n[STARTUP TEST]")
    say("Voice assistant ready. Listening for commands.")
    
    print("\n[READY] Say something to the ReSpeaker microphone...")
    print("       Press Ctrl+C to stop\n")
    
    conversation_count = 0
    
    try:
        while True:
            print("\n" + "=" * 60)
            print(f"[LISTENING #{conversation_count + 1}...]")
            print("=" * 60)
            
            # Listen for speech
            recognized_text = listen_once(mic_index, RESPEAKER_RATE, seconds=5.0)
            
            if recognized_text:
                print(f"\n[YOU SAID] {recognized_text}")
                
                # Get AI response
                print(f"\n[AI THINKING...]")
                response = get_ai_response(recognized_text, model_name, user_text=recognized_text)
                
                print(f"\n[AI RESPONSE] {response}")
                
                # Speak response
                say(response)
                
                conversation_count += 1
            else:
                print("\n[NO SPEECH DETECTED] Listening again...")
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("[SHUTTING DOWN]")
        print("=" * 60)
        say("Voice assistant shutting down. Goodbye!")
        print("Goodbye!")
    
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")

# ====== RUN ======
if __name__ == "__main__":
    main()
