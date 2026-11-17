# 🌊 NEEL — Linux-Native Voice & System AI Companion

> **Neel** — The Blue Ocean AI Companion, built for **Sagar**.  
> A lightweight, always-ready AI friend hardwired directly into Linux Mint / Ubuntu X11.

## ✨ Capabilities

- **🎤 Offline Wake-Word & Dynamic VAD (`modules/listener.py`)**
  - Detects `"Hey Neel"` locally using Vosk small English acoustic model.
  - **Adaptive Timing**: 2.8s thinking buffer (never cuts you off mid-thought) + 0.8s silence cutoff (zero awkward pauses).
  - **Acoustic Echo Guard**: Automatically pauses microphone recognition while speaking.
- **🗣️ Zero-RAM Natural Voice (`modules/speaker.py`)**
  - Natural streamed neural voice (`edge-tts` piped directly to `mpv`), releasing memory immediately after speaking.
  - Subtle generated sound cues (`wake.wav`, `success.wav`, `warn.wav`).
- **💻 Desktop Puppet (`modules/system_control.py`)**
  - App launching (`chrome`, `code`, `terminal`, `files`, `calculator`, `settings`).
  - Volume control via PulseAudio (`pactl`) and brightness via `xrandr`.
  - Screenshots saved automatically to `~/Pictures`.
  - Live CPU, RAM, and battery diagnostics.
- **🌐 Chrome Autopilot (`modules/chrome_control.py`)**
  - Direct YouTube and Google searches.
  - Playback toggling (`playerctl` / `xdotool`), fullscreen, mute, and tab management.
- **📺 Smart TV Interaction (`modules/tv_control.py`)**
  - Local network reachability check for LG webOS TV (`192.168.0.100`).
- **🛡️ Smart Safety Guard (`modules/safety.py`)**
  - Everyday actions execute instantaneously.
  - High-risk operations (deletions, process termination, sudo) explain the risk and ask for voice confirmation.
- **🧠 Hybrid Brain (`modules/brain.py`)**
  - Instant offline regex/intent router for OS & browser commands (<15ms latency).
  - Cloud LLM fallback for free-form questions and reasoning (0 MB local RAM overhead).

## 🕹️ CLI Usage

```bash
neel start                   # Run silently as background daemon (<190MB RAM)
neel stop                    # Stop daemon and release all memory
neel status                  # Check live PID, RAM, and CPU usage
neel run                     # Run interactively in foreground with live logs
neel test "battery status"   # Simulate a command directly through Neel's brain
```

## 🛠️ Setup

1. Install system dependencies:
   ```bash
   sudo apt install -y xdotool xclip portaudio19-dev ffmpeg mpv playerctl brightnessctl python3-venv
   ```
2. Setup Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Download the lightweight Vosk model (`vosk-model-small-en-us-0.15`) into `data/vosk-model/`.
4. Generate sound cues:
   ```bash
   .venv/bin/python sounds/generate_sounds.py
   ```
5. Symlink CLI:
   ```bash
   ln -sf "$(pwd)/bin/neel" ~/.local/bin/neel
   ```
