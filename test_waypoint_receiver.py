#!/usr/bin/env python3
"""
Flask server to receive BOTH live location and saved waypoints
- /current endpoint: Receives live GPS updates (every 5 seconds)
- /waypoint endpoint: Receives saved waypoints (when friend taps "Save")
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Two separate data stores
current_location_data = {
    "lat": None,
    "lon": None,
    "last_updated": None
}

waypoints_data = {
    "waypoints": [],
    "last_updated": None
}

# ===== ENDPOINT 1: LIVE LOCATION (Auto Updates) =====
@app.route('/current', methods=['POST'])
def receive_current_location():
    """Receive live GPS location from friend's app (updates every 5 seconds)"""
    try:
        data = request.json
        lat = data.get('lat')
        lon = data.get('lon')
        
        print(f"\n📍 LIVE LOCATION UPDATE: {lat}, {lon}")
        
        # Update current location
        current_location_data['lat'] = lat
        current_location_data['lon'] = lon
        current_location_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file (overwrites each time)
        with open('current_location.json', 'w') as f:
            json.dump(current_location_data, f, indent=2)
        
        print(f"✅ Current location updated")
        
        return jsonify({'status': 'success', 'type': 'current_location'}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ===== ENDPOINT 2: SAVED WAYPOINTS (Manual Save) =====
@app.route('/waypoint', methods=['POST'])
def receive_waypoint():
    """Receive saved waypoints from friend's app (when they tap 'Save Waypoint')"""
    try:
        data = request.json
        waypoint_string = data.get('waypoints', '')
        
        print(f"\n{'='*50}")
        print(f"💾 SAVED WAYPOINT at {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        print(f"Raw data: {waypoint_string}")
        
        # Parse waypoints: "WP1:37.788,-122.432;WP2:37.789,-122.433"
        waypoints = []
        if waypoint_string:
            for wp in waypoint_string.split(';'):
                if ':' in wp:
                    name, coords = wp.split(':')
                    lat, lon = coords.split(',')
                    waypoints.append({
                        'name': name,
                        'lat': float(lat),
                        'lon': float(lon),
                        'saved_at': datetime.now().isoformat()
                    })
                    print(f"  {name}: {lat}, {lon}")
        
        # Store waypoints
        waypoints_data['waypoints'] = waypoints
        waypoints_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open('waypoints.json', 'w') as f:
            json.dump(waypoints_data, f, indent=2)
        
        print(f"\n✅ Saved {len(waypoints)} waypoints to waypoints.json")
        print(f"{'='*50}\n")
        
        return jsonify({
            'status': 'success',
            'type': 'saved_waypoint',
            'message': f'Received {len(waypoints)} waypoints',
            'waypoints': waypoints
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ===== ENDPOINT 3: GET CURRENT LOCATION =====
@app.route('/current', methods=['GET'])
def get_current_location():
    """Get current live location"""
    if os.path.exists('current_location.json'):
        with open('current_location.json', 'r') as f:
            return jsonify(json.load(f)), 200
    return jsonify({'status': 'no_data', 'message': 'No current location available'}), 404

# ===== ENDPOINT 4: GET SAVED WAYPOINTS =====
@app.route('/waypoints', methods=['GET'])
def get_waypoints():
    """Get all stored waypoints"""
    if os.path.exists('waypoints.json'):
        with open('waypoints.json', 'r') as f:
            return jsonify(json.load(f)), 200
    return jsonify(waypoints_data), 200

@app.route('/', methods=['GET'])
def home():
    """Home page showing status"""
    # Read both files
    current_loc = None
    if os.path.exists('current_location.json'):
        with open('current_location.json', 'r') as f:
            current_loc = json.load(f)
    
    waypoints = []
    if os.path.exists('waypoints.json'):
        with open('waypoints.json', 'r') as f:
            waypoints = json.load(f).get('waypoints', [])
    
    html = f"""
    <html>
    <head>
        <title>Waypoint Receiver - Live + Saved</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: #2196F3;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .section {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .live {{
                background: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .waypoint {{
                padding: 10px;
                border-bottom: 1px solid #eee;
            }}
            code {{
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                color: #333;
            }}
            .live-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #fff;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📍 Waypoint Receiver</h1>
            <p>Live Tracking + Saved Waypoints</p>
        </div>
        
        <div class="live">
            <h2><span class="live-indicator"></span> Live Location</h2>
            {'<p><strong>Current:</strong> ' + str(current_loc['lat']) + ', ' + str(current_loc['lon']) + '</p>' if current_loc and current_loc.get('lat') else '<p>No live location yet</p>'}
            {'<p><small>Last updated: ' + str(current_loc.get('last_updated', 'Never')) + '</small></p>' if current_loc else ''}
        </div>
        
        <div class="section">
            <h2>💾 Saved Waypoints ({len(waypoints)})</h2>
            {''.join([f'<div class="waypoint"><strong>{wp["name"]}</strong>: {wp["lat"]}, {wp["lon"]}<br><small>Saved: {wp.get("saved_at", "Unknown")}</small></div>' for wp in waypoints]) or '<p>No saved waypoints yet</p>'}
        </div>
        
        <div class="section">
            <h2>📡 API Endpoints</h2>
            <p><code>POST /current</code> - Receive live GPS location</p>
            <p><code>POST /waypoint</code> - Receive saved waypoint</p>
            <p><code>GET /current</code> - Get current live location</p>
            <p><code>GET /waypoints</code> - Get all saved waypoints</p>
        </div>
        
        <div class="section">
            <h2>🔗 Connection Info</h2>
            <p>Live tracking: <code>http://10.11.3.221:5001/current</code></p>
            <p>Save waypoint: <code>http://10.11.3.221:5001/waypoint</code></p>
            <p><small>Page auto-refreshes every 5 seconds</small></p>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Waypoint Receiver Server (Live + Saved)")
    print("="*60)
    print(f"📍 Server: http://10.11.3.221:5001")
    print(f"")
    print(f"📡 Endpoints:")
    print(f"  Live GPS:     POST http://10.11.3.221:5001/current")
    print(f"  Save Waypoint: POST http://10.11.3.221:5001/waypoint")
    print(f"  Dashboard:     GET  http://10.11.3.221:5001/")
    print(f"")
    print(f"💡 Two modes:")
    print(f"  1. Live tracking - Friend's app sends GPS every 5 sec")
    print(f"  2. Saved waypoints - Friend taps 'Save' to mark spot")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
