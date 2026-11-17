import asyncio
import os
import subprocess
import edge_tts

# Audio feedback lock to prevent Neel from hearing himself
IS_SPEAKING = False

# Default natural voice: en-IN-PrabhatNeural (warm Indian English, natural, non-robotic)
# Alternative options: en-US-ChristopherNeural, en-GB-RyanNeural
VOICE = os.environ.get("NEEL_VOICE", "en-IN-PrabhatNeural")

SOUNDS_DIR = os.path.expanduser("~/neel/sounds")

def play_sound(sound_name: str):
    """Play a low-latency UI sound cue (wake, success, error)."""
    sound_path = os.path.join(SOUNDS_DIR, f"{sound_name}.wav")
    if os.path.exists(sound_path):
        subprocess.Popen(
            ["mpv", "--no-video", "--really-quiet", "--volume=80", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

async def speak(text: str, voice: str = VOICE):
    """
    Stream voice directly to audio output using edge-tts and mpv.
    Consumes ~0MB persistent RAM and releases memory instantly.
    """
    global IS_SPEAKING
    if not text or not text.strip():
        return

    IS_SPEAKING = True
    try:
        # Stream TTS audio directly through pipe into mpv
        communicate = edge_tts.Communicate(text.strip(), voice)
        mpv_proc = subprocess.Popen(
            ["mpv", "--no-video", "--really-quiet", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio" and mpv_proc.stdin:
                try:
                    mpv_proc.stdin.write(chunk["data"])
                    mpv_proc.stdin.flush()
                except (BrokenPipeError, OSError):
                    break

        if mpv_proc.stdin:
            try:
                mpv_proc.stdin.close()
            except OSError:
                pass
        mpv_proc.wait()
    except Exception as e:
        print(f"[Neel Speaker Error]: {e}")
        # Fallback to local espeak-ng if offline or network error
        subprocess.run(["espeak-ng", "-s", "165", text], check=False)
    finally:
        # Give a small 100ms grace period for room reverberation to settle
        await asyncio.sleep(0.15)
        IS_SPEAKING = False

def speak_sync(text: str, voice: str = VOICE):
    """Synchronous wrapper for speak."""
    asyncio.run(speak(text, voice))

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "Yo Sagar, Neel is online. Everything is running smooth."
    print(f"Testing speaker: '{msg}'")
    speak_sync(msg)
