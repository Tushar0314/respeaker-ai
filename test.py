import json, queue, sys, os, tempfile, wave, re
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3

# ===================== USER CONFIG (adjust if needed) =====================
PREFERRED_MIC_INDEX = 12                        # we'll try this first; falls back if needed
MIC_NAME_REGEX = r"(Microphone Array|Headset Microphone).*Realtek"  # fallback scan pattern
PREFERRED_OUT_INDEX = 14                        # your wired earphones (try 14, else 5 or 12 or 15)
OUT_NAME_REGEX = r"(Headphone|Speaker).*Realtek" # fallback scan for outputs
MODEL_DIR = "models/en"                         # Vosk model folder
IN_RATES = [48000, 44100, 32000, 16000]         # input rates to try
OUT_RATES = [48000, 44100, 32000, 22050, 16000] # output rates to try (include 22050 for pyttsx3)
DTYPE = 'int16'
BLOCKSIZE = 1024
# ==========================================================================

# -------------------------- Small utilities --------------------------------
def list_devices():
    devices = sd.query_devices()
    print("\n=== Audio devices (abbrev) ===")
    for i, d in enumerate(devices):
        io = []
        if d['max_input_channels'] > 0: io.append("IN")
        if d['max_output_channels'] > 0: io.append("OUT")
        print(f"{i:>2}: {d['name']} [{', '.join(io)}], "
              f"max_in={d['max_input_channels']}, max_out={d['max_output_channels']}, "
              f"default SR={d.get('default_samplerate')}")
    print("================================\n")
    return devices

def resample_audio(audio_np, sr_in, sr_out):
    """Linear resample audio_np (shape [N, C]) from sr_in to sr_out."""
    if sr_in == sr_out:
        return audio_np
    n_in = audio_np.shape[0]
    n_out = int(round(n_in * (sr_out / sr_in)))
    x_old = np.linspace(0.0, 1.0, num=n_in, endpoint=False)
    x_new = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
    if audio_np.ndim == 1:
        out = np.interp(x_new, x_old, audio_np).astype(np.int16)
    else:
        out = np.vstack([
            np.interp(x_new, x_old, audio_np[:, ch])
            for ch in range(audio_np.shape[1])
        ]).T.astype(np.int16)
    return out

# -------------------------- Input probing ----------------------------------
def try_input_config(dev_idx, rates):
    """Return (rate, channels) that passes check_input_settings, trying 1..max_input_channels."""
    info = sd.query_devices(dev_idx, 'input')
    max_ch = max(1, info['max_input_channels'])
    for r in rates:
        for ch in range(1, max_ch + 1):
            try:
                sd.check_input_settings(device=dev_idx, samplerate=r, channels=ch, dtype=DTYPE)
                print(f"[ok IN] dev={dev_idx} ({info['name']}) -> {r} Hz, ch={ch}")
                return r, ch
            except Exception as e:
                print(f"[test IN] dev={dev_idx} {r} Hz, ch={ch} not accepted: {e}")
    return None

def find_working_input(preferred_idx, name_regex):
    # 1) try preferred
    try:
        cfg = try_input_config(preferred_idx, IN_RATES)
        if cfg: return preferred_idx, cfg[0], cfg[1]
    except Exception as e:
        print(f"[warn] preferred input dev {preferred_idx} query failed: {e}")

    # 2) try by name
    devices = sd.query_devices()
    pat = re.compile(name_regex, re.IGNORECASE)
    candidates = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0 and pat.search(d['name'])]
    for idx in candidates:
        cfg = try_input_config(idx, IN_RATES)
        if cfg: return idx, cfg[0], cfg[1]

    # 3) any input
    for idx, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            cfg = try_input_config(idx, IN_RATES)
            if cfg: return idx, cfg[0], cfg[1]

    raise RuntimeError("No acceptable input configuration found on any device.")

# -------------------------- Output probing ---------------------------------
def try_output_config(dev_idx, rates):
    """Return (rate, channels) that passes check_output_settings, preferring stereo then mono."""
    info = sd.query_devices(dev_idx, 'output')
    max_ch = max(1, info['max_output_channels'])
    # Try stereo if available, then mono
    for ch in ([2,1] if max_ch >= 2 else [1]):
        for r in rates:
            try:
                sd.check_output_settings(device=dev_idx, samplerate=r, channels=ch, dtype=DTYPE)
                print(f"[ok OUT] dev={dev_idx} ({info['name']}) -> {r} Hz, ch={ch}")
                return r, ch
            except Exception as e:
                print(f"[test OUT] dev={dev_idx} {r} Hz, ch={ch} not accepted: {e}")
    return None

def find_working_output(preferred_idx, name_regex):
    # 1) try preferred
    try:
        cfg = try_output_config(preferred_idx, OUT_RATES)
        if cfg: return preferred_idx, cfg[0], cfg[1]
    except Exception as e:
        print(f"[warn] preferred output dev {preferred_idx} query failed: {e}")

    # 2) try by name
    devices = sd.query_devices()
    pat = re.compile(name_regex, re.IGNORECASE)
    candidates = [i for i, d in enumerate(devices) if d['max_output_channels'] > 0 and pat.search(d['name'])]
    for idx in candidates:
        cfg = try_output_config(idx, OUT_RATES)
        if cfg: return idx, cfg[0], cfg[1]

    # 3) any output
    for idx, d in enumerate(devices):
        if d['max_output_channels'] > 0:
            cfg = try_output_config(idx, OUT_RATES)
            if cfg: return idx, cfg[0], cfg[1]

    raise RuntimeError("No acceptable output configuration found on any device.")

# -------------------------- TTS (synth->resample->play) --------------------
_tts = pyttsx3.init('sapi5')
_tts.setProperty('rate', 180)
_tts.setProperty('volume', 1.0)

def _synthesize_to_wav(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    path = tmp.name
    tmp.close()
    _tts.save_to_file(text, path)
    _tts.runAndWait()
    return path

def _play_wav_on_device(wav_path: str, out_idx: int, out_sr: int, out_ch: int):
    with wave.open(wav_path, 'rb') as wf:
        wav_ch = wf.getnchannels()
        wav_sr = wf.getframerate()
        sw = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    # bytes -> numpy int16
    audio = np.frombuffer(frames, dtype=np.int16 if sw == 2 else np.int16).reshape(-1, wav_ch)

    # upmix mono->stereo if output expects 2ch
    if audio.shape[1] == 1 and out_ch == 2:
        audio = np.repeat(audio, 2, axis=1)
    # downmix stereo->mono if output expects 1ch
    if audio.shape[1] == 2 and out_ch == 1:
        audio = audio.mean(axis=1, dtype=np.int16).reshape(-1, 1)

    # resample to out_sr if needed
    if wav_sr != out_sr:
        audio = resample_audio(audio, wav_sr, out_sr)

    sd.play(audio, out_sr, device=out_idx, blocking=True)
    sd.stop()

def say(text: str, out_idx: int, out_sr: int, out_ch: int):
    print(f"[TTS] -> {text}")
    path = _synthesize_to_wav(text)
    try:
        _play_wav_on_device(path, out_idx, out_sr, out_ch)
    finally:
        try: os.remove(path)
        except: pass

# ----------------------------- ASR / Vosk ----------------------------------
def make_recognizer(rate_hz):
    model = Model(MODEL_DIR)
    return KaldiRecognizer(model, rate_hz)

def listen_once(dev_idx, samplerate, stream_channels, seconds=3.0):
    """
    Capture from device/rate/channels. If channels>1, downmix to mono int16
    before feeding Vosk.
    """
    q = queue.Queue()

    def cb(indata, frames, time, status):
        if status:
            # print(status)  # uncomment to debug
            pass
        if stream_channels == 1:
            q.put(bytes(indata))
        else:
            # downmix to mono for Vosk
            arr = np.frombuffer(indata, dtype=np.int16).reshape(-1, stream_channels)
            mono = arr.mean(axis=1).astype(np.int16)
            q.put(mono.tobytes())

    rec = make_recognizer(samplerate)
    target_samples = int(samplerate * seconds)
    got_samples = 0
    text_final = ""

    try:
        with sd.RawInputStream(device=dev_idx,
                               samplerate=samplerate,
                               blocksize=BLOCKSIZE,
                               dtype=DTYPE,
                               channels=stream_channels,
                               callback=cb):
            while got_samples < target_samples:
                buf = q.get()
                got_samples += len(buf) // 2  # 2 bytes/int16 (mono now)
                if rec.AcceptWaveform(buf):
                    res = json.loads(rec.Result())
                    text_final = (res.get("text") or "").strip()
            res = json.loads(rec.FinalResult())
            tail = (res.get("text") or "").strip()
            if tail:
                text_final = tail or text_final
    except Exception as e:
        print(f"[ERR] listen_once failed: {e}")
        return ""
    return (text_final or "").lower().strip()

# -------------------------------- Main -------------------------------------
def main():
    list_devices()

    # Pick input
    try:
        mic_idx, in_sr, in_ch = find_working_input(PREFERRED_MIC_INDEX, MIC_NAME_REGEX)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)

    # Pick output
    try:
        out_idx, out_sr, out_ch = find_working_output(PREFERRED_OUT_INDEX, OUT_NAME_REGEX)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)

    print(f"Using MIC_INDEX={mic_idx} at {in_sr} Hz, ch={in_ch}  |  "
          f"OUTPUT_INDEX={out_idx} at {out_sr} Hz, ch={out_ch}")

    say("Ready. Say hello!", out_idx, out_sr, out_ch)

    while True:
        text = listen_once(mic_idx, in_sr, in_ch, 3.0)
        print(f"[ASR] \"{text}\"")
        if not text:
            continue

        if "hello" in text:
            say("Hello", out_idx, out_sr, out_ch)
        elif "how are you" in text:
            say("I'm doing well. How are you?", out_idx, out_sr, out_ch)
        elif "goodbye" in text or "bye" in text:
            say("Goodbye", out_idx, out_sr, out_ch)
            sys.exit(0)
        elif "your name" in text:
            say("I'm your local voice assistant.", out_idx, out_sr, out_ch)
        elif "time" in text:
            say("I don't have a clock wired in yet, but we can add that.", out_idx, out_sr, out_ch)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
