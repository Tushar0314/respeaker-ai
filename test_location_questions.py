#!/usr/bin/env python3
"""Test different ways of asking about location"""

import json
import os

def get_waypoint_location():
    """Read waypoints from file."""
    try:
        with open('waypoints.json', 'r') as f:
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
    except:
        return None

def handle_location_query(user_text):
    """Handle location queries."""
    location_patterns = [
        'where am i', 'where are we', 'what is my location',
        'what is our location', 'tell me my location',
        'tell me where i am', 'tell me where we are',
        'current location', 'my location', 'our location',
        'where', 'location', 'gps', 'coordinates', 'position',
    ]
    
    user_lower = user_text.lower()
    
    if any(pattern in user_lower for pattern in location_patterns):
        location = get_waypoint_location()
        
        if location and location.get('is_waypoint'):
            wp_name = location.get('waypoint_name')
            lat = location.get('lat')
            lon = location.get('lon')
            wp_count = location.get('waypoint_count', 0)
            
            response = f"You are at {wp_name}. "
            response += f"Coordinates: latitude {lat:.4f}, longitude {lon:.4f}. "
            
            if wp_count > 1:
                response += f"You have {wp_count} waypoints saved."
            
            return response
        else:
            return "No waypoints found."
    
    return None

# Test different phrasings
print("=" * 70)
print("Testing Different Ways to Ask About Location")
print("=" * 70)

test_questions = [
    "where am I?",
    "where are we?",
    "what is my location?",
    "tell me my location",
    "hey can you tell me location?",
    "current location",
    "GPS",
    "coordinates",
    "what's our position?",
]

for question in test_questions:
    print(f"\n🎤 You ask: '{question}'")
    response = handle_location_query(question)
    if response:
        print(f"🔊 Pi says: '{response}'")
    else:
        print(f"❌ Not recognized as location question")

print("\n" + "=" * 70)
