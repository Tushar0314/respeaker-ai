#!/usr/bin/env python3
"""
DEMO: Voice-to-Waypoint Test on Mac
Simulates the complete Raspberry Pi experience
"""

import json
import subprocess
import os

def say(text):
    """Mac speech (Pi will use espeak)."""
    print(f"\n🔊 Pi speaks: '{text}'")
    subprocess.run(['say', text])

def simulate_voice_input():
    """Simulate microphone input (on Pi, this is Vosk)."""
    print("\n🎤 SIMULATING YOUR VOICE INPUT")
    print("   (On Pi, you'd actually speak to ReSpeaker)")
    print("\nWhat question do you want to ask?")
    print("1. where am I?")
    print("2. where am i")
    print("3. what is my location")
    
    choice = input("\nEnter 1, 2, or 3 (or type your own): ").strip()
    
    if choice == '1':
        return "where am I?"
    elif choice == '2':
        return "where am i"
    elif choice == '3':
        return "what is my location"
    else:
        return choice

def get_waypoint_location():
    """Read waypoints from file (sent by friend's app)."""
    try:
        waypoints_file = 'waypoints.json'
        if not os.path.exists(waypoints_file):
            return None
        
        with open(waypoints_file, 'r') as f:
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
        print(f"[Error reading waypoints: {e}]")
        return None

def handle_location_query(user_text):
    """Check if asking about location and respond."""
    location_keywords = ['where', 'location', 'place', 'here']
    
    if any(keyword in user_text.lower() for keyword in location_keywords):
        location = get_waypoint_location()
        
        if location and location.get('is_waypoint'):
            wp_name = location.get('waypoint_name', 'Unknown')
            lat = location.get('lat')
            lon = location.get('lon')
            wp_count = location.get('waypoint_count', 0)
            
            response = f"You are at {wp_name}. "
            response += f"Coordinates: latitude {lat:.4f}, longitude {lon:.4f}. "
            
            if wp_count > 1:
                response += f"You have {wp_count} waypoints saved. "
                all_wps = location.get('all_waypoints', [])
                wp_list = ", ".join([wp['name'] for wp in all_wps])
                response += f"Your waypoints are: {wp_list}."
            
            return response
        else:
            return "No waypoints found. Friend hasn't sent location yet."
    
    return "I didn't understand that question."

def main():
    print("=" * 70)
    print("🎙️  VOICE ASSISTANT DEMO (Mac Simulation)")
    print("=" * 70)
    print("\nThis simulates what happens on Raspberry Pi:")
    print("  1. You speak to ReSpeaker microphone")
    print("  2. Vosk converts speech to text")
    print("  3. Pi reads waypoints.json (from friend's app)")
    print("  4. Pi speaks the answer through JBL speaker")
    print("=" * 70)
    
    # Check if waypoints exist
    if os.path.exists('waypoints.json'):
        with open('waypoints.json', 'r') as f:
            data = json.load(f)
        print(f"\n✅ Found {len(data.get('waypoints', []))} waypoints from friend's app")
    else:
        print("\n❌ No waypoints.json found!")
        print("   Run the Flask server and send waypoints from iPhone first")
        return
    
    print("\n" + "=" * 70)
    print("🚀 STARTING VOICE ASSISTANT")
    print("=" * 70)
    
    try:
        while True:
            print("\n" + "-" * 70)
            
            # Simulate listening
            user_text = simulate_voice_input()
            
            print(f"\n📝 Recognized text: '{user_text}'")
            
            # Process the question
            print("\n🤖 Processing...")
            response = handle_location_query(user_text)
            
            print(f"\n💬 Response: '{response}'")
            
            # Speak the answer
            say(response)
            
            # Ask if want to continue
            print("\n" + "-" * 70)
            cont = input("\nAsk another question? (y/n): ").strip().lower()
            if cont != 'y':
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    say("Goodbye!")

if __name__ == "__main__":
    main()
