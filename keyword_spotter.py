"""
Keyword Spotting Module for ReSpeaker AI
Integrates KWS-DS-CNN for custom keyword detection

Usage:
    kws = KeywordSpotter(model_path='models/kws/where.tflite', threshold=0.9)
    if kws.detect(audio_chunk):
        print("Keyword detected!")
"""

import tensorflow as tf
import numpy as np
import threading
from collections import deque
from typing import Callable, Optional


class KeywordSpotter:
    """
    TensorFlow Lite-based keyword spotter for custom keywords.
    Designed to work with KWS-DS-CNN models.
    """
    
    def __init__(self, model_path: str, threshold: float = 0.9, label: str = "keyword"):
        """
        Initialize keyword spotter with a trained model.
        
        Args:
            model_path: Path to .tflite model file
            threshold: Confidence threshold (0-1) for detection
            label: Name of the keyword for logging
        """
        self.model_path = model_path
        self.threshold = threshold
        self.label = label
        
        # Load TensorFlow Lite model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            print(f"✓ Loaded KWS model for '{label}': {model_path}")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise
    
    def detect(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if keyword is present in audio chunk.
        
        Args:
            audio_chunk: Audio data (numpy array, float32, normalized -1 to 1)
        
        Returns:
            True if keyword detected above threshold, False otherwise
        """
        try:
            # Prepare input for model (reshape to expected input shape)
            input_data = audio_chunk.astype(np.float32)
            input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get confidence score
            confidence = float(output_data[0])
            
            detected = confidence > self.threshold
            if detected:
                print(f"🎤 {self.label.upper()} detected! Confidence: {confidence:.2%}")
            
            return detected
            
        except Exception as e:
            print(f"✗ Detection error: {e}")
            return False
    
    def get_confidence(self, audio_chunk: np.ndarray) -> float:
        """
        Get raw confidence score for keyword.
        
        Args:
            audio_chunk: Audio data (numpy array)
        
        Returns:
            Confidence score (0-1)
        """
        try:
            input_data = audio_chunk.astype(np.float32)
            input_data = np.expand_dims(input_data, axis=0)
            
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            return float(output_data[0])
        except:
            return 0.0


class MultiKeywordSpotter:
    """
    Manages multiple keyword spotters for different keywords.
    Useful for detecting "WHERE" and "SPEED" in sequence.
    """
    
    def __init__(self):
        """Initialize empty spotter collection."""
        self.spotters = {}
    
    def add_spotter(self, keyword: str, model_path: str, threshold: float = 0.9):
        """
        Add a new keyword spotter.
        
        Args:
            keyword: Name of keyword (e.g., 'where', 'speed')
            model_path: Path to .tflite model
            threshold: Detection threshold
        """
        self.spotters[keyword.lower()] = KeywordSpotter(
            model_path=model_path,
            threshold=threshold,
            label=keyword
        )
        print(f"✓ Added spotter for '{keyword}'")
    
    def detect_any(self, audio_chunk: np.ndarray) -> Optional[str]:
        """
        Check if ANY keyword is detected.
        
        Args:
            audio_chunk: Audio data
        
        Returns:
            Name of detected keyword, or None if no detection
        """
        for keyword, spotter in self.spotters.items():
            if spotter.detect(audio_chunk):
                return keyword
        return None
    
    def detect_all_confidences(self, audio_chunk: np.ndarray) -> dict:
        """
        Get confidence scores for all keywords.
        
        Args:
            audio_chunk: Audio data
        
        Returns:
            Dictionary {keyword: confidence_score}
        """
        results = {}
        for keyword, spotter in self.spotters.items():
            results[keyword] = spotter.get_confidence(audio_chunk)
        return results


class StreamingKeywordDetector:
    """
    Real-time keyword detection on streaming audio.
    Maintains a buffer of recent audio frames for detection.
    """
    
    def __init__(self, keyword_spotter: KeywordSpotter, 
                 chunk_size: int = 16000, overlap: float = 0.5):
        """
        Initialize streaming detector.
        
        Args:
            keyword_spotter: KeywordSpotter instance
            chunk_size: Samples per chunk (e.g., 1 second at 16kHz)
            overlap: Overlap between chunks (0-1)
        """
        self.spotter = keyword_spotter
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.buffer = deque(maxlen=chunk_size)
        self.detected_callback: Optional[Callable] = None
    
    def set_detection_callback(self, callback: Callable[[str], None]):
        """
        Set callback to invoke when keyword detected.
        
        Args:
            callback: Function to call with detection details
        """
        self.detected_callback = callback
    
    def process_chunk(self, audio_chunk: np.ndarray) -> bool:
        """
        Process new audio chunk and check for keyword.
        
        Args:
            audio_chunk: New audio samples
        
        Returns:
            True if keyword detected
        """
        # Add new samples to buffer
        self.buffer.extend(audio_chunk)
        
        # When buffer is full, run detection
        if len(self.buffer) >= self.chunk_size:
            audio_array = np.array(list(self.buffer), dtype=np.float32)
            detected = self.spotter.detect(audio_array)
            
            if detected and self.detected_callback:
                self.detected_callback(self.spotter.label)
            
            return detected
        
        return False


# Example usage function
def example_integration_with_vosk():
    """
    Example: Integrate KWS with Vosk speech recognition
    
    Typical workflow:
    1. Audio stream comes in
    2. KWS checks for "WHERE" keyword
    3. If detected, start Vosk recognition
    4. Process Vosk result with Gemini AI
    5. Generate TTS response
    """
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  KWS Integration with Vosk - Example Workflow              ║
    ╚════════════════════════════════════════════════════════════╝
    
    # Step 1: Initialize keyword spotters
    kws_detector = MultiKeywordSpotter()
    kws_detector.add_spotter('where', 'models/kws/where.tflite', threshold=0.9)
    kws_detector.add_spotter('speed', 'models/kws/speed.tflite', threshold=0.9)
    
    # Step 2: In audio processing loop
    while audio_stream_open:
        audio_chunk = audio_stream.read()  # Read from mic
        
        # Check for keywords first (low latency)
        keyword = kws_detector.detect_any(audio_chunk)
        
        if keyword:
            print(f"Keyword '{keyword}' detected! Starting Vosk...")
            
            # Step 3: Now run Vosk for full recognition
            vosk_recognizer.process_chunk(audio_chunk)
            if vosk_recognizer.final_result():
                text = vosk_recognizer.result()
                
                # Step 4: Send to Gemini AI
                ai_response = gemini_api.generate(text)
                
                # Step 5: Synthesize speech
                tts_engine.say(ai_response)
    """)


if __name__ == "__main__":
    example_integration_with_vosk()
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  Next Steps for Integration                                ║
    ╚════════════════════════════════════════════════════════════╝
    
    1. CREATE MODELS:
       - Train custom "where" and "speed" models using:
         python train.py --keywords where,speed
         (See KWS-DS-CNN repo for training scripts)
       - Or download pre-trained models from TensorFlow Hub
       - Save as: models/kws/where.tflite, models/kws/speed.tflite
    
    2. INSTALL DEPENDENCIES:
       pip install tensorflow
       OR (for lightweight)
       pip install tflite-runtime
    
    3. MODIFY hello_ai.py:
       - Import this module
       - Create MultiKeywordSpotter instance
       - Call detect_any() in audio processing loop
       - Only run Vosk when keyword detected
    
    4. TEST:
       python keyword_spotter.py  # This file
       # Should show "Next Steps" message
    
    5. BENCHMARK:
       - Test on Raspberry Pi
       - Measure latency and accuracy
       - Adjust thresholds if needed
    """)
