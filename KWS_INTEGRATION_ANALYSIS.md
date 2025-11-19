# KWS-DS-CNN Integration Analysis for ReSpeaker AI

## 📋 Project Overview

Your Current Project (`respeaker-ai`):
- **Speech Recognition**: Vosk (offline, lightweight)
- **Text-to-Speech**: Pyttsx3
- **AI Processing**: Google Gemini API
- **Hardware**: ReSpeaker 2/4-Mic Array (optional)

External Project (`KWS-DS-CNN-for-embedded`):
- **Technology**: TensorFlow-based Depthwise Separable CNN
- **Purpose**: Keyword Spotting (KWS) for embedded systems
- **Languages**: C++, Python, C
- **License**: Apache-2.0

---

## ✅ CAN YOU USE IT? YES!

### Why It's Compatible:

1. **Complementary Technology**
   - Your Vosk: Full speech-to-text recognition
   - KWS-DS-CNN: Lightweight keyword detection (like a gate)
   - **Together**: KWS detects keywords → Vosk processes full command

2. **Embedded-Friendly**
   - Both designed for embedded systems (Raspberry Pi, ARM)
   - KWS-DS-CNN specifically optimized for low power
   - Your project targets ReSpeaker (embedded device)

3. **Python Integration**
   - KWS-DS-CNN has Python scripts for inference
   - Easy to integrate into your `hello_ai.py`

---

## 🎯 Your Use Case: "WHERE" → "SPEED" Keywords

### Implementation Strategy:

```
Audio Stream (Mic)
    ↓
KWS Model 1: Detect "where"
    ↓ (if detected)
KWS Model 2: Detect "speed"
    ↓ (if detected)
Full Speech Recognition (Vosk)
    ↓
Gemini AI Processing
    ↓
TTS Response
```

### Step-by-Step Implementation:

#### Step 1: Train/Get KWS Models for Your Keywords
```python
# Option A: Use pre-trained models from KWS-DS-CNN (limited keywords)
# Option B: Train custom models for "where" and "speed"

from models import DS_CNN  # From KWS-DS-CNN repo
model_where = load_model('models/kws_where.tflite')
model_speed = load_model('models/kws_speed.tflite')
```

#### Step 2: Add Keyword Detection to Your Pipeline
```python
import tensorflow as tf
import numpy as np

class KeywordSpotter:
    def __init__(self, model_path, threshold=0.9):
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.threshold = threshold
    
    def detect(self, audio_chunk):
        """Returns True if keyword detected"""
        # Process audio chunk → MFCC features → Model inference
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        
        # Prepare features from audio
        # ... implementation
        
        self.interpreter.set_tensor(input_details[0]['index'], features)
        self.interpreter.invoke()
        confidence = self.interpreter.get_tensor(output_details[0]['index'])
        
        return confidence > self.threshold
```

#### Step 3: Integrate into Your Main Loop
```python
# In hello_ai.py, after Vosk setup:

kws_where = KeywordSpotter('models/kws_where.tflite')
kws_speed = KeywordSpotter('models/kws_speed.tflite')

# In audio stream loop:
if kws_where.detect(audio_chunk):
    print("WHERE keyword detected!")
    # Proceed with Vosk recognition

if kws_speed.detect(audio_chunk):
    print("SPEED keyword detected!")
    # Proceed with Vosk recognition
```

---

## 📊 Comparison Table

| Feature | Your Vosk | KWS-DS-CNN | Combined Approach |
|---------|-----------|-----------|-------------------|
| **Full Speech Recognition** | ✅ Yes | ❌ No | ✅ Yes |
| **Keyword Detection** | ❌ Limited | ✅ Excellent | ✅ Yes |
| **Latency** | ~500ms | ~50ms | ~550ms total |
| **Memory** | ~50MB | ~1-5MB | ~55MB |
| **Online Required** | ❌ No | ❌ No | ❌ No |
| **Custom Keywords** | ⚠️ Hard | ✅ Easy (train) | ✅ Yes |
| **Raspberry Pi** | ✅ Works | ✅ Optimized | ✅ Perfect |

---

## 🔧 Integration Challenges & Solutions

### Challenge 1: Training Custom Models
```
Problem: Need "where" and "speed" models
Solution: 
- Use KWS-DS-CNN's training script (train.py)
- Or use TensorFlow Speech Commands dataset + train
- Or download pre-trained models from TensorFlow Hub
```

### Challenge 2: Audio Feature Extraction
```
Problem: KWS uses MFCC features, need to match Vosk's format
Solution: 
- KWS-DS-CNN includes input_data.py for feature extraction
- Reuse their MFCC implementation
- Ensure sample rate matches (16kHz typical)
```

### Challenge 3: Real-time Processing
```
Problem: Running 2-3 models on streaming audio
Solution:
- Use TensorFlow Lite (already in KWS-DS-CNN)
- Run on separate thread from Vosk
- Use audio buffer to avoid blocking
```

---

## 📦 What to Extract from KWS-DS-CNN Repo

```
KWS-DS-CNN/
├── models.py              ← Model architecture
├── input_data.py          ← Feature extraction (MFCC)
├── auto_test_streaming.py ← Streaming inference example
├── work/                  ← Pre-trained model weights
└── Deployment/            ← TensorFlow Lite models
```

### Key Files to Copy:
1. `models.py` - DS_CNN architecture
2. `input_data.py` - Audio preprocessing (MFCC)
3. TensorFlow Lite models from `Deployment/` folder

---

## 📝 Modified File Structure

```
respeaker-ai/
├── hello_ai.py                    ← Main script (modify)
├── models/
│   ├── en/                        ← Vosk models (existing)
│   ├── kws/                       ← NEW: Keyword spotting models
│   │   ├── where.tflite
│   │   ├── speed.tflite
│   │   └── model.json
├── keyword_spotter.py             ← NEW: KWS module
├── requirements_rpi.txt           ← UPDATE: Add TensorFlow Lite
└── README.md
```

---

## 🚀 Step-by-Step Implementation Plan

### Phase 1: Setup (1-2 hours)
- [ ] Clone KWS-DS-CNN repo
- [ ] Extract `models.py` and `input_data.py`
- [ ] Create `keyword_spotter.py` wrapper module
- [ ] Install TensorFlow Lite: `pip install tflite-runtime`

### Phase 2: Get/Train Models (2-6 hours)
- [ ] Option A: Download pre-trained models (if available)
- [ ] Option B: Train custom models using KWS-DS-CNN training script
  - Need audio samples of "where" and "speed"
  - Run `python train.py --keywords where,speed`

### Phase 3: Integration (2-4 hours)
- [ ] Modify `hello_ai.py` to include KeywordSpotter
- [ ] Test KWS detection on sample audio
- [ ] Integrate with Vosk (only run when keyword detected)
- [ ] Test end-to-end pipeline

### Phase 4: Optimization (1-3 hours)
- [ ] Benchmark performance on Raspberry Pi
- [ ] Adjust confidence thresholds
- [ ] Optimize threading if needed
- [ ] Test with ReSpeaker hardware

---

## ⚠️ Important Considerations

1. **Training Data**: You need audio samples for "where" and "speed" (100+ examples each)
2. **Model Size**: TensorFlow Lite models are ~500KB-2MB (fits on RPi)
3. **Latency**: KWS adds ~50-100ms to total pipeline
4. **Accuracy**: Depends on training data quality
5. **Language**: Current models are for English only

---

## 📚 Additional Resources

- **KWS-DS-CNN GitHub**: https://github.com/PeterMS123/KWS-DS-CNN-for-embedded
- **TensorFlow Speech Commands**: https://github.com/tensorflow/examples/tree/master/tensorflow_examples/lite/model_maker/demo
- **ARM ML-KWS**: https://github.com/ARM-software/ML-KWS-for-MCU
- **TensorFlow Lite Python Guide**: https://www.tensorflow.org/lite/guide/python

---

## ✨ Conclusion

**YES, you can absolutely use KWS-DS-CNN in your project!**

The integration will:
- ✅ Enable custom keyword detection ("where", "speed")
- ✅ Reduce false positives from Vosk
- ✅ Save power by only running Vosk when keywords detected
- ✅ Work perfectly on Raspberry Pi with ReSpeaker
- ✅ Maintain offline operation (no cloud dependencies)

**Recommended Next Step**: Start with Phase 1 (setup) and Phase 2 (training custom models).

