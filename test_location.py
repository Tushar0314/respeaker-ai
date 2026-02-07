#!/usr/bin/env python3
"""
Test Google Maps Location API
Run this to test if the location detection works
"""

import requests
import json

# API Keys
GOOGLE_MAPS_API_KEY = 'AIzaSyD0ewRk6lzFRYkts_mcy6UFAF6lfdazvd8'

def test_google_geolocation():
    """Test Google Maps Geolocation API."""
    print("=" * 60)
    print("Testing Google Maps Geolocation API...")
    print("=" * 60)
    
    try:
        # Step 1: Get coordinates from WiFi/IP
        print("\n[STEP 1] Requesting location from Google Geolocation API...")
        geolocation_url = 'https://www.googleapis.com/geolocation/v1/geolocate'
        geolocation_params = {'key': GOOGLE_MAPS_API_KEY}
        
        geo_response = requests.post(
            geolocation_url,
            params=geolocation_params,
            json={},
            timeout=5
        )
        
        print(f"Status Code: {geo_response.status_code}")
        
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            print(f"\n✓ Geolocation Response:")
            print(json.dumps(geo_data, indent=2))
            
            lat = geo_data.get('location', {}).get('lat')
            lon = geo_data.get('location', {}).get('lng')
            accuracy = geo_data.get('accuracy')
            
            print(f"\n✓ Coordinates Found:")
            print(f"  Latitude: {lat}")
            print(f"  Longitude: {lon}")
            print(f"  Accuracy: {accuracy} meters")
            
            # Step 2: Reverse geocode to get address
            print(f"\n[STEP 2] Converting coordinates to address...")
            geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
            geocode_params = {
                'latlng': f'{lat},{lon}',
                'key': GOOGLE_MAPS_API_KEY
            }
            
            geocode_response = requests.get(geocode_url, params=geocode_params, timeout=5)
            
            print(f"Status Code: {geocode_response.status_code}")
            
            if geocode_response.status_code == 200:
                geocode_data = geocode_response.json()
                
                if geocode_data.get('results'):
                    result = geocode_data['results'][0]
                    
                    print(f"\n✓ Reverse Geocoding Response:")
                    print(f"  Formatted Address: {result.get('formatted_address')}")
                    
                    # Extract components
                    city = None
                    region = None
                    country = None
                    
                    print(f"\n✓ Address Components:")
                    for component in result.get('address_components', []):
                        types = component.get('types', [])
                        if 'locality' in types:
                            city = component.get('long_name')
                            print(f"  City: {city}")
                        elif 'administrative_area_level_1' in types:
                            region = component.get('long_name')
                            print(f"  Region/State: {region}")
                        elif 'country' in types:
                            country = component.get('long_name')
                            print(f"  Country: {country}")
                    
                    # Final spoken response
                    print(f"\n" + "=" * 60)
                    print("VOICE ASSISTANT WOULD SAY:")
                    print("=" * 60)
                    if city and region and city != region:
                        print(f"\"You are in {city}, {region}, {country}.\"")
                    elif city:
                        print(f"\"You are in {city}, {country}.\"")
                    else:
                        print(f"\"You are near {result.get('formatted_address')}.\"")
                    print("=" * 60)
                else:
                    print("✗ No results from geocoding")
            else:
                print(f"✗ Geocoding failed: {geocode_response.text}")
        else:
            print(f"✗ Geolocation failed: {geo_response.text}")
            
            # Try fallback
            print("\n[FALLBACK] Trying IP-based location...")
            test_ip_location()
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n[FALLBACK] Trying IP-based location...")
        test_ip_location()

def test_ip_location():
    """Test IP-based location as fallback."""
    try:
        print("\nUsing ipapi.co for IP-based location...")
        response = requests.get('https://ipapi.co/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ IP Location Response:")
            print(json.dumps(data, indent=2))
            
            city = data.get('city')
            region = data.get('region')
            country = data.get('country_name')
            
            print(f"\n" + "=" * 60)
            print("VOICE ASSISTANT WOULD SAY:")
            print("=" * 60)
            if region and region != city:
                print(f"\"You are in {city}, {region}, {country}.\"")
            else:
                print(f"\"You are in {city}, {country}.\"")
            print("=" * 60)
        else:
            print(f"✗ IP location failed: {response.text}")
    except Exception as e:
        print(f"✗ Fallback error: {e}")

if __name__ == "__main__":
    test_google_geolocation()
    