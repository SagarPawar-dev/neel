import json
import os
import sys
import time
import pyaudio
from vosk import Model, KaldiRecognizer
from modules.speaker import play_sound, IS_SPEAKING

MODEL_PATH = os.path.expanduser("~/neel/data/vosk-model")

# Phonetic variants of "Hey Neel" / "Neel" in English acoustic models
WAKE_WORDS = ["hey neel", "neel", "hey kneel", "kneel", "hey nil", "nil", "hey meal", "hey deal"]

SAMPLE_RATE = 16000
CHUNK_SIZE = 4096

class Listener:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.recognizer.SetWords(True)

        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_stream(self):
        """Open microphone input stream."""
        if self.stream is None:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )

    def stop_stream(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def listen_for_wake_word(self) -> bool:
        """
        Continuously listen in background with minimum CPU/RAM.
        Returns True immediately when 'Hey Neel' is detected.
        """
        self.start_stream()
        self.recognizer.Reset()

        while True:
            # Echo guard: if Neel is speaking, skip audio frames
            if IS_SPEAKING:
                time.sleep(0.1)
                continue

            try:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            except OSError:
                time.sleep(0.02)
                continue

            if self.recognizer.AcceptWaveform(data):
                res = json.loads(self.recognizer.Result())
                text = res.get("text", "").lower()
                for wake in WAKE_WORDS:
                    if wake in text:
                        return True
            else:
                partial = json.loads(self.recognizer.PartialResult())
                part_text = partial.get("partial", "").lower()
                for wake in WAKE_WORDS:
                    if wake in part_text:
                        self.recognizer.Reset()
                        return True
            
            # Tiny sleep to yield CPU cycle
            time.sleep(0.005)

    def record_command(self, thinking_timeout: float = 2.8, silence_cutoff: float = 0.8) -> str:
        """
        Dynamic VAD Command Recorder:
        - 2.8s thinking buffer: gives Sagar time to formulate thought without being cut off.
        - 0.8s silence cutoff: once words are detected and silence follows, triggers execution.
        """
        self.start_stream()
        self.recognizer.Reset()
        
        # Audio feedback that Neel is awake and listening
        play_sound("wake")

        start_time = time.time()
        has_spoken = False
        last_speech_time = start_time
        collected_text = ""

        while True:
            if IS_SPEAKING:
                time.sleep(0.05)
                continue

            try:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            except OSError:
                time.sleep(0.01)
                continue

            now = time.time()

            # Kaldi internal VAD
            if self.recognizer.AcceptWaveform(data):
                res = json.loads(self.recognizer.Result())
                text = res.get("text", "").strip()
                if text:
                    collected_text += " " + text
                    has_spoken = True
                    # End of utterance detected by Kaldi
                    break
            else:
                partial = json.loads(self.recognizer.PartialResult())
                part_text = partial.get("partial", "").strip()
                if part_text:
                    has_spoken = True
                    last_speech_time = now

            if not has_spoken:
                if now - start_time > thinking_timeout:
                    return ""
            else:
                if now - last_speech_time > silence_cutoff:
                    final_res = json.loads(self.recognizer.FinalResult())
                    final_text = final_res.get("text", "")
                    collected_text += " " + final_text
                    break

            time.sleep(0.005)

        total_cmd = collected_text.strip()
        for wake in WAKE_WORDS:
            if total_cmd.startswith(wake):
                total_cmd = total_cmd[len(wake):].strip()
        return total_cmd
