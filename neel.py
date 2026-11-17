#!/usr/bin/env python3
import asyncio
import os
import signal
import subprocess
import sys

from modules.listener import Listener
from modules.speaker import speak, play_sound
from modules.brain import Brain
from modules.safety import SafetyGuard

VERSION = "1.0.0"

def notify_desktop(title: str, message: str):
    """Subtle Linux desktop notification."""
    try:
        subprocess.run(
            ["notify-send", "-a", "Neel", "-i", "dialog-information", title, message],
            check=False
        )
    except Exception:
        pass

async def main_loop():
    print(f"""
    🌊 ====================================== 🌊
             NEEL — AI Companion v{VERSION}
          Born for Sagar | Linux Native System
    🌊 ====================================== 🌊
    [Status]: Ready and listening for 'Hey Neel'...
    [Memory]: Headless lightweight daemon (<190MB)
    """)

    notify_desktop("🌊 Neel is Online", "Say 'Hey Neel' to give a command.")
    listener = Listener()

    # Graceful shutdown handler
    def handle_exit(sig, frame):
        print("\n[Neel]: Signing off. Catch you later!")
        listener.stop_stream()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    while True:
        # Step 1: Wait for wake word with minimal CPU
        wake_detected = listener.listen_for_wake_word()
        if not wake_detected:
            await asyncio.sleep(0.05)
            continue

        print("\n[Neel]: Wake word detected! Listening...")
        notify_desktop("🌊 Neel", "Listening...")

        # Step 2: Record speech with Dynamic VAD (2.5s thinking buffer, 0.8s silence cutoff)
        command = listener.record_command(thinking_timeout=2.5, silence_cutoff=0.8)

        if not command:
            print("[Neel]: No command heard. Returning to standby.")
            continue

        print(f"[Neel]: Heard -> '{command}'")

        # Step 3: Safety Guard Check
        is_risky, warning = SafetyGuard.assess_risk(command)
        if is_risky:
            play_sound("warn")
            await speak(warning)
            confirm_cmd = listener.record_command(thinking_timeout=3.5, silence_cutoff=1.0)
            if not SafetyGuard.is_confirmation(confirm_cmd):
                await speak("Action cancelled.")
                continue

        # Step 4: Intent Processing
        response = await Brain.process_intent(command)

        if response:
            print(f"[Neel]: Responding -> '{response}'")
            notify_desktop("🌊 Neel", response)
            play_sound("success")
            await speak(response)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n[Neel]: Terminated by user.")
