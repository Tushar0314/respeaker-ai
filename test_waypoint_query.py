#!/usr/bin/env python3
"""
Test the waypoint location query functionality without running the full voice assistant.
This simulates asking "Where am I?" and shows what the voice assistant would respond.
"""

import json
import os
import math
from datetime import datetime

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

def format_location_response(location):
    """Format the location data into a natural language response."""
    if not location:
        return "I cannot find the location right now."
    
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
        
        response += f"Coordinates: latitude {lat:.4f}, longitude {lon:.4f}. "
        
        if wp_count > 1:
            response += f"You have {wp_count} waypoints in your route. "
            
            # List all waypoints
            all_wps = location.get('all_waypoints', [])
            wp_list = ", ".join([wp['name'] for wp in all_wps])
            response += f"Your waypoints are: {wp_list}."
        
        return response
    
    return "No waypoint data available."

def main():
    """Test the location query system."""
    print("=" * 70)
    print("🧪 WAYPOINT LOCATION QUERY TEST")
    print("=" * 70)
    print()
    
    # Check if waypoints.json exists
    if not os.path.exists('waypoints.json'):
        print("❌ Error: waypoints.json not found!")
        print()
        print("Run this first to create sample data:")
        print("  python3 waypoint_receiver.py test")
        return
    
    print("📂 Reading waypoint data...")
    location = get_waypoint_location()
    
    if not location:
        print("❌ No waypoint data found in waypoints.json")
        return
    
    print("✅ Waypoint data loaded successfully!")
    print()
    
    # Display raw data
    print("📊 RAW DATA:")
    print("-" * 70)
    print(f"  Waypoint Name: {location.get('waypoint_name')}")
    print(f"  Latitude: {location.get('lat')}")
    print(f"  Longitude: {location.get('lon')}")
    print(f"  Total Waypoints: {location.get('waypoint_count')}")
    
    if location.get('distance_to_waypoint') is not None:
        print(f"  Distance to Waypoint: {location.get('distance_to_waypoint'):.2f} meters")
    
    if location.get('all_waypoints'):
        print(f"  All Waypoints:")
        for wp in location.get('all_waypoints'):
            print(f"    - {wp['name']}: {wp['lat']}, {wp['lon']}")
    
    print()
    
    # Display formatted response
    print("🗣️  VOICE ASSISTANT RESPONSE:")
    print("-" * 70)
    response = format_location_response(location)
    print(f"  \"{response}\"")
    print()
    
    # Simulate different queries
    print("💬 SIMULATED VOICE QUERIES:")
    print("-" * 70)
    
    queries = [
        "Where am I?",
        "What's my location?",
        "GPS coordinates",
        "Show all waypoints",
    ]
    
    for query in queries:
        print(f"  You: \"{query}\"")
        print(f"  Pi:  \"{response}\"")
        print()
    
    print("=" * 70)
    print("✅ Test completed successfully!")
    print()
    print("💡 To test with the full voice assistant:")
    print("   python3 hello_ai_pi_custom.py")
    print()

if __name__ == "__main__":
    main()
