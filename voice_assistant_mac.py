#!/usr/bin/env python3
"""
Complete Voice Assistant Demo on Mac
- Uses Mac microphone for voice input
- Uses Gemini AI for responses
- Reads waypoints from waypoints.json
- Speaks with Mac 'say' command
"""

import json
import os
import subprocess
import speech_recognition as sr
import google.generativeai as genai

# Configuration
GEMINI_API_KEY = 'AIzaSyAxkVCMAiB0ksjuA9jDvrOgXH3v5wYueVQ'

def say(text):
    """Mac text-to-speech."""
    print(f"\n🔊 Speaking: {text}")
    subprocess.run(['say', text])

def listen_with_mac_mic():
    """Listen using Mac microphone and Google Speech Recognition."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n🎤 Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🤔 Processing speech...")
            
            # Use Google Speech Recognition (free)
            text = recognizer.recognize_google(audio)
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

def get_live_location():
    """Read LIVE GPS location from current_location.json (sent every 5 seconds)."""
    try:
        current_file = '/Users/tusharbhaliya/Desktop/AI/respeaker-ai/current_location.json'
        if not os.path.exists(current_file):
            return None
        
        with open(current_file, 'r') as f:
            data = json.load(f)
        
        return {
            'lat': data['lat'],
            'lon': data['lon'],
            'is_live': True,
            'last_updated': data.get('timestamp', 'unknown')
        }
    except Exception as e:
        print(f"[Live GPS error: {e}]")
        return None

def get_waypoint_location():
    """Read saved waypoints from waypoints.json."""
    try:
        waypoint_file = '/Users/tusharbhaliya/Desktop/AI/respeaker-ai/waypoints.json'
        if not os.path.exists(waypoint_file):
            return None
        
        with open(waypoint_file, 'r') as f:
            data = json.load(f)
        
        waypoints = data.get('waypoints', [])
        if not waypoints:
            return None
        
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
        print(f"[Waypoint error: {e}]")
        return None

def get_current_location():
    """Get current location - prioritize LIVE GPS, fallback to saved waypoints."""
    # First try live GPS (updated every 5 seconds)
    live_location = get_live_location()
    if live_location:
        return live_location
    
    # Fallback to saved waypoints
    waypoint_location = get_waypoint_location()
    if waypoint_location:
        return waypoint_location
    
    return None

def handle_location_query(user_text):
    """Handle location-based queries."""
    location_patterns = [
        'where am i', 'where are we', 'what is my location',
        'what is our location', 'tell me my location',
        'tell me where i am', 'tell me where we are',
        'current location', 'my location', 'our location',
        'where', 'location', 'gps', 'coordinates', 'position',
    ]
    
    user_lower = user_text.lower()
    
    if any(pattern in user_lower for pattern in location_patterns):
        location = get_current_location()
        
        if location and location.get('is_live'):
            # Live GPS location
            lat = location.get('lat')
            lon = location.get('lon')
            
            response = f"Your LIVE location is: latitude {lat:.4f}, longitude {lon:.4f}. "
            response += "This is real-time GPS being sent from your iPhone every 5 seconds."
            
            return response
        
        elif location and location.get('is_waypoint'):
            # Saved waypoint
            wp_name = location.get('waypoint_name')
            lat = location.get('lat')
            lon = location.get('lon')
            wp_count = location.get('waypoint_count', 0)
            
            response = f"You are at saved waypoint {wp_name}. "
            response += f"Coordinates: latitude {lat:.4f}, longitude {lon:.4f}. "
            
            if wp_count > 1:
                response += f"You have {wp_count} waypoints saved. "
                all_wps = location.get('all_waypoints', [])
                wp_list = ", ".join([wp['name'] for wp in all_wps])
                response += f"Your waypoints are: {wp_list}."
            
            return response
        else:
            return "No GPS data found. Make sure live tracking is enabled on your iPhone, or send waypoints."
    
    return None

def get_gemini_response(user_text, model):
    """Get response from Gemini AI."""
    # First check if it's a location query
    location_response = handle_location_query(user_text)
    if location_response:
        return location_response
    
    # Otherwise, ask Gemini
    try:
        prompt = f"""User said: "{user_text}"

Reply with one concise spoken sentence suitable for text-to-speech."""
        
        response = model.generate_content(prompt, stream=False)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            # Quota exceeded - provide helpful fallback
            return "I'm listening, but my AI quota is exceeded. Try asking about your location, or wait a minute and ask again."
        else:
            return f"Sorry, I had a technical issue. {error_str[:100]}"

def main():
    print("\n" + "=" * 70)
    print("🎙️  VOICE ASSISTANT - MAC DEMO")
    print("=" * 70)
    print("\n✨ Features:")
    print("  • Real-time voice recognition (Mac microphone)")
    print("  • Gemini AI for intelligent responses")
    print("  • Waypoint location from iPhone app")
    print("  • Mac text-to-speech output")
    print("\n" + "=" * 70)
    
    # Initialize Gemini
    print("\n🤖 Connecting to Gemini AI...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini connected (using gemini-1.5-flash)!")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return
    
    # Check for waypoints
    if os.path.exists('waypoints.json'):
        with open('waypoints.json', 'r') as f:
            data = json.load(f)
        wp_count = len(data.get('waypoints', []))
        print(f"✅ Found {wp_count} waypoints from iPhone")
    else:
        print("⚠️  No waypoints yet (send from iPhone web app)")
    
    print("\n" + "=" * 70)
    print("🚀 READY! Start speaking...")
    print("   Press Ctrl+C to exit")
    print("=" * 70)
    
    say("Voice assistant ready. How can I help you?")
    
    conversation_count = 0
    
    try:
        while True:
            print(f"\n{'='*70}")
            print(f"Conversation #{conversation_count + 1}")
            print("=" * 70)
            
            # Listen
            user_text = listen_with_mac_mic()
            
            if user_text:
                print(f"\n✅ You said: '{user_text}'")
                
                # Check for exit commands
                exit_commands = ['goodbye', 'good bye', 'bye', 'exit', 'quit', 'stop']
                if any(cmd in user_text.lower() for cmd in exit_commands):
                    print("👋 User said goodbye!")
                    say("Goodbye! Have a great day!")
                    break
                
                # Get response
                print("🤔 Thinking...")
                response = get_gemini_response(user_text, model)
                
                print(f"💬 Response: {response}")
                
                # Speak
                say(response)
                
                conversation_count += 1
            else:
                print("❌ Couldn't hear you. Try again...")
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("👋 Shutting down...")
        print("=" * 70)
        say("Goodbye!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Check dependencies
    try:
        import speech_recognition
        print("✅ speech_recognition installed")
    except ImportError:
        print("❌ Installing speech_recognition...")
        subprocess.run(['pip3', 'install', 'SpeechRecognition', 'pyaudio'])
    
    main()
