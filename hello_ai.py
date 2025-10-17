import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

RATE = 16000
MODEL_DIR = "models/en"
GRAMMAR = '["hello"]'   # only listen for "hello"

model = Model(MODEL_DIR)
rec = KaldiRecognizer(model, RATE, GRAMMAR)
engine = pyttsx3.init()  # Windows SAPI

def say(text: str):
    engine.say(text)
    engine.runAndWait()

def heard_hello() -> bool:
    q = queue.Queue()
    def cb(indata, frames, time, status):
        q.put(bytes(indata))

    rec.Reset()
    with sd.RawInputStream(
    device=12,              # << use the WASAPI Realtek mic
    samplerate=RATE,
    blocksize=1024,
    dtype='int16',
    channels=1,
    callback=cb
):


 # add device=<index> if needed
        data = b""
        while len(data) < RATE * 2:
            data += q.get()
            if rec.AcceptWaveform(data):
                break

    result = json.loads(rec.FinalResult())
    text = (result.get("text") or "").strip()
    return text == "hello"

def main():
    print("Say 'hello' to get a reply.  Press Ctrl+C to stop.")
    say("Ready")
    while True:
        if heard_hello():
            print("You said hello → replying…")
            say("Hello")

if __name__ == "__main__":
    main()
