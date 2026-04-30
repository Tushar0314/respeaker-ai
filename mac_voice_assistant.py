#!/usr/bin/env python3
"""
Mac Voice Assistant with Gemini AI
- Uses Mac microphone for voice input
- Uses Mac speaker (say command) for output
- Powered by Gemini AI
"""

import json
import os
import subprocess
import speech_recognition as sr
import google.generativeai as genai

# Configuration
GEMINI_API_KEY = 'AIzaSyCkPP0DvADrykHZ9tc6q1Bmv3rkqXEGCmw'

def say(text):
    """Use Mac's text-to-speech."""
    print(f"\n🔊 Speaking: {text}")
    subprocess.run(['say', text])

def listen():
    """Listen using Mac microphone."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n🎤 Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🤔 Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Couldn't understand")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def get_location():
    """Get location from current_location.json."""
    try:
        location_file = 'current_location.json'
        if os.path.exists(location_file):
            with open(location_file, 'r') as f:
                data = json.load(f)
                return data.get('latitude'), data.get('longitude')
    except:
        pass
    return None, None

def get_waypoints():
    """Get waypoints from waypoints.json."""
    try:
        waypoints_file = 'waypoints.json'
        if os.path.exists(waypoints_file):
            with open(waypoints_file, 'r') as f:
                data = json.load(f)
                return data.get('waypoints', [])
    except:
        pass
    return []

def ask_gemini(question):
    """Ask Gemini AI a question."""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Add location context
        lat, lon = get_location()
        waypoints = get_waypoints()
        
        context = f"\nUser question: {question}"
        if lat and lon:
            context += f"\nUser's current location: {lat}, {lon}"
        if waypoints:
            context += f"\nSaved waypoints: {json.dumps(waypoints)}"
        
        response = model.generate_content(context)
        return response.text
        
    except Exception as e:
        return f"Sorry, I had an error: {str(e)}"

def main():
    """Main voice assistant loop."""
    say("Hello! I'm your Mac voice assistant powered by Gemini AI. How can I help you?")
    
    while True:
        # Listen for user input
        user_input = listen()
        
        if not user_input:
            continue
        
        # Check for exit commands
        if any(word in user_input.lower() for word in ['exit', 'quit', 'bye', 'goodbye']):
            say("Goodbye! Have a great day!")
            break
        
        # Get response from Gemini
        print("\n🤖 Asking Gemini AI...")
        response = ask_gemini(user_input)
        print(f"\n💬 Gemini says: {response}")
        
        # Speak the response
        say(response)

if __name__ == '__main__':
    print("="*50)
    print("🎙️  MAC VOICE ASSISTANT WITH GEMINI AI")
    print("="*50)
    print("\nMake sure you have installed:")
    print("  pip install SpeechRecognition google-generativeai pyaudio")
    print("\nPress Ctrl+C to stop anytime")
    print("="*50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
