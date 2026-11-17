import os
import wave
import numpy as np

SOUNDS_DIR = os.path.expanduser("~/neel/sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)
SAMPLE_RATE = 44100

def create_wave_file(filename: str, samples: np.ndarray):
    filepath = os.path.join(SOUNDS_DIR, filename)
    # Normalize to 16-bit PCM
    samples = samples / np.max(np.abs(samples)) * 0.7  # gentle volume
    int_samples = (samples * 32767).astype(np.int16)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16 bits
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(int_samples.tobytes())
    print(f"Generated {filepath}")

def make_wake_chime():
    # Modern subtle 2-tone upward chime (587Hz D5 -> 880Hz A5) over 120ms
    duration = 0.14
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # First tone (0 to 60ms)
    t1 = t[t < 0.07]
    tone1 = np.sin(2 * np.pi * 587.33 * t1) * (1 - np.linspace(0, 0.4, len(t1)))
    # Second tone (60 to 140ms)
    t2 = t[t >= 0.07] - 0.07
    tone2 = np.sin(2 * np.pi * 880.00 * t2) * (np.exp(-t2 * 15))
    signal = np.concatenate([tone1, tone2])
    create_wave_file("wake.wav", signal)

def make_success_pop():
    # Subtle soft affirmative click/pop (440Hz -> 660Hz rapid drop)
    duration = 0.08
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    signal = np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 40)
    create_wave_file("success.wav", signal)

def make_warn_chime():
    # Soft warm warning double ping (440Hz -> 370Hz)
    duration = 0.20
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    t1 = t[t < 0.10]
    tone1 = np.sin(2 * np.pi * 440.0 * t1) * np.exp(-t1 * 20)
    t2 = t[t >= 0.10] - 0.10
    tone2 = np.sin(2 * np.pi * 370.0 * t2) * np.exp(-t2 * 20)
    signal = np.concatenate([tone1, tone2])
    create_wave_file("warn.wav", signal)

if __name__ == "__main__":
    make_wake_chime()
    make_success_pop()
    make_warn_chime()
