#!/usr/bin/env python3
"""
Test waypoint speech on Mac using 'say' command
"""

import json
import subprocess
import os

def say(text):
    """Use Mac's built-in 'say' command for text-to-speech."""
    try:
        subprocess.run(['say', text])
        print(f"[✓ Spoke: {text}]")
    except Exception as e:
        print(f"[Error: {e}]")

def get_waypoint_location():
    """Read waypoints from file."""
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
        print(f"[Waypoint error] {e}")
        return None

def handle_location_query(user_text):
    """Handle location-based queries."""
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
            return "No waypoints found."
    
    return None

# Test it!
print("=" * 60)
print("🔊 Testing Mac Speech with Waypoints")
print("=" * 60)

# Check if waypoints.json exists
if os.path.exists('waypoints.json'):
    print("✅ waypoints.json found!")
    
    # Simulate "where am I?" question
    user_question = "where am I?"
    print(f"\n🎤 You ask: '{user_question}'")
    
    response = handle_location_query(user_question)
    
    if response:
        print(f"\n📝 Mac will say: '{response}'")
        print("\n🔊 Speaking now...")
        say(response)
    else:
        print("❌ No response generated")
else:
    print("❌ waypoints.json not found!")
    print("📍 Creating sample waypoints...")
    
    # Create sample waypoints
    sample_data = {
        "waypoints": [
            {"name": "WP1", "lat": 37.7749, "lon": -122.4194},
            {"name": "WP2", "lat": 37.7749, "lon": -122.4194}
        ],
        "last_updated": "2025-12-05T01:21:00"
    }
    
    with open('waypoints.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Sample waypoints created!")
    print("\n🔊 Speaking waypoint location...")
    
    response = handle_location_query("where am I?")
    say(response)

print("\n" + "=" * 60)
