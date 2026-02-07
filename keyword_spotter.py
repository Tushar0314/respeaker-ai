r#!/usr/bin/env python3
"""
Simple Keyword Spotter for Voice Assistant
Listens for wake words like "hey assistant", "jarvis", "alexa" etc.
Only activates full voice assistant when wake word is detected
"""

import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import queue

# Configuration
WAKE_WORDS = ['hey', 'jarvis', 'alexa', 'assistant', 'computer', 'pi']
MODEL_DIR = "models/en"
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

print("=" * 60)
print("🎧 Keyword Spotter - Listening for Wake Words")
print("=" * 60)
print(f"Wake words: {', '.join(WAKE_WORDS)}")
print("=" * 60)

class KeywordSpotter:
    def __init__(self, model_dir, sample_rate=16000):
        """Initialize the keyword spotter."""
        self.model = Model(model_dir)
        self.rec = KaldiRecognizer(self.model, sample_rate)
        self.rec.SetWords(True)
        self.sample_rate = sample_rate
        self.q = queue.Queue()
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            print(f"[Audio Status] {status}")
        self.q.put(bytes(indata))
    
    def listen_for_keyword(self, keywords, device=None, timeout=None):
        """
        Listen continuously for wake words.
        
        Args:
            keywords: List of wake words to detect
            device: Audio input device index (None for default)
            timeout: Stop after timeout seconds (None for infinite)
            
        Returns:
            detected_keyword: The keyword that was detected
        """
        print(f"\n[LISTENING] Say one of: {', '.join(keywords)}")
        
        try:
            with sd.RawInputStream(
                device=device,
                samplerate=self.sample_rate,
                blocksize=BLOCK_SIZE,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            ):
                start_time = None
                if timeout:
                    import time
                    start_time = time.time()
                
                while True:
                    # Check timeout
                    if timeout and start_time:
                        import time
                        if time.time() - start_time > timeout:
                            print("\n[TIMEOUT] No wake word detected")
                            return None
                    
                    # Get audio data
                    try:
                        data = self.q.get(timeout=1)
                    except queue.Empty:
                        continue
                    
                    # Process audio
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").lower()
                        
                        if text:
                            print(f"[HEARD] {text}")
                            
                            # Check if any keyword is in the text
                            for keyword in keywords:
                                if keyword.lower() in text:
                                    print(f"\n✓ [WAKE WORD DETECTED] '{keyword}'")
                                    return keyword
                    else:
                        # Partial result
                        partial = json.loads(self.rec.PartialResult())
                        partial_text = partial.get("partial", "").lower()
                        
                        if partial_text:
                            # Check partial results too (faster response)
                            for keyword in keywords:
                                if keyword.lower() in partial_text:
                                    print(f"\n✓ [WAKE WORD DETECTED] '{keyword}'")
                                    return keyword
        
        except KeyboardInterrupt:
            print("\n\n[STOPPED]")
            return None
        except Exception as e:
            print(f"\n[ERROR] {e}")
            return None

def main():
    """Test the keyword spotter."""
    # Initialize
    spotter = KeywordSpotter(MODEL_DIR, SAMPLE_RATE)
    
    print("\n[READY] Listening for wake words...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Listen for wake word
            detected = spotter.listen_for_keyword(WAKE_WORDS)
            
            if detected:
                print(f"\n🎯 Wake word '{detected}' activated!")
                print(">>> Now you can activate your full voice assistant <<<")
                print("\nWaiting 2 seconds before listening again...\n")
                
                import time
                time.sleep(2)
                
                print("\n" + "=" * 60)
                print("[LISTENING AGAIN]")
                print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\nGoodbye!")

if __name__ == "__main__":
    main()
