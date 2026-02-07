#!/usr/bin/env python3
"""Test the waypoint speaking functionality on Mac"""

import json

# Simulate the updated functions
def get_waypoint_location():
    """Read waypoints from file sent by friend's app."""
    try:
        waypoints_file = 'waypoints.json'
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
    """Handle location-based queries like 'where am I'."""
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
print("Testing Waypoint Speech")
print("=" * 60)

test_questions = [
    "where am I?",
    "what is my location?",
    "where are we?"
]

for question in test_questions:
    print(f"\nQuestion: '{question}'")
    response = handle_location_query(question)
    print(f"Pi would say: '{response}'")
    print()

print("=" * 60)
