import os
import re
import aiohttp
from modules.system_control import SystemControl
from modules.chrome_control import ChromeControl
from modules.tv_control import TVControl
from modules.safety import SafetyGuard

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

NEEL_SYSTEM_PROMPT = (
    "You are Neel, Sagar's personal AI companion living natively inside his Linux laptop. "
    "Sagar's name means ocean, and you are Neel (the blue ocean). "
    "Speak naturally in grounded, intelligent English with subtle Hindi touches where fitting. "
    "Be concise, sharp, and voice-friendly. Never sound like a corporate robot. "
    "Avoid repetitive 'bro' and 'bhai' clichés. Use crisp status phrases like 'On it', 'Sorted', 'Done', 'You can check screen'. "
    "Keep answers under 2-3 sentences unless asked for an in-depth explanation."
)

class Brain:
    @staticmethod
    async def process_intent(text: str) -> str:
        """
        Dual-Engine Intent Processor:
        1. Fast local regex/pattern matching for instant desktop & hardware actions (0ms latency).
        2. Cloud LLM fallback for conversational questions, code logic, and open-ended thoughts.
        """
        cmd = text.lower().strip()
        if not cmd:
            return ""

        # --- 1. Audio & Volume Control ---
        if "volume" in cmd or "mute" in cmd or "unmute" in cmd:
            if "up" in cmd or "increase" in cmd or "raise" in cmd:
                return SystemControl.adjust_volume("up")
            elif "down" in cmd or "decrease" in cmd or "lower" in cmd:
                return SystemControl.adjust_volume("down")
            elif "mute" in cmd or "unmute" in cmd:
                return SystemControl.adjust_volume("mute")
            else:
                digits = re.findall(r"\d+", cmd)
                if digits:
                    return SystemControl.adjust_volume(digits[0])
                return SystemControl.adjust_volume("up")

        # --- 2. Display Brightness ---
        if "brightness" in cmd or "dim" in cmd:
            if "up" in cmd or "increase" in cmd or "max" in cmd:
                return SystemControl.adjust_brightness("up")
            elif "down" in cmd or "dim" in cmd or "low" in cmd:
                return SystemControl.adjust_brightness("down")
            else:
                digits = re.findall(r"\d+", cmd)
                if digits:
                    return SystemControl.adjust_brightness(digits[0])
                return SystemControl.adjust_brightness("up")

        # --- 3. YouTube Autopilot ---
        yt_match = re.search(r"(?:play|search)\s+(.*?)\s+(?:on|in)\s+youtube", cmd)
        if yt_match:
            query = yt_match.group(1).strip()
            return ChromeControl.search_youtube(query)

        if cmd.startswith("play ") and ("song" in cmd or "video" in cmd or "music" in cmd or "on youtube" in cmd):
            query = re.sub(r"^play\s+", "", cmd)
            query = re.sub(r"\s+on\s+youtube.*", "", query).strip()
            return ChromeControl.search_youtube(query)

        # --- 4. Web Search ---
        search_match = re.search(r"^(?:search|google|look up|search for)\s+(.*)", cmd)
        if search_match:
            query = search_match.group(1).strip()
            return ChromeControl.search_google(query)

        # --- 5. Media Playback Controls ---
        if cmd in ["pause", "play", "pause video", "resume", "toggle play", "toggle playback"]:
            return ChromeControl.play_pause_media()

        if "fullscreen" in cmd:
            return ChromeControl.toggle_fullscreen()

        if "close tab" in cmd or "close this tab" in cmd:
            return ChromeControl.close_tab()

        if "new tab" in cmd or "open tab" in cmd:
            return ChromeControl.new_tab()

        # --- 6. Application Launching ---
        launch_match = re.search(r"^(?:open|launch|start)\s+(.*)", cmd)
        if launch_match:
            target = launch_match.group(1).strip()
            # If target has "chrome and search ..."
            if "chrome and search" in target:
                q = target.split("search")[-1].strip()
                return ChromeControl.search_google(q)
            return SystemControl.launch_app(target)

        # --- 7. System Diagnostics & Screenshot ---
        if any(w in cmd for w in ["screenshot", "screen shot", "capture screen"]):
            return SystemControl.take_screenshot()

        if any(w in cmd for w in ["battery", "ram", "cpu", "system status", "specs", "how is laptop", "stats"]):
            return SystemControl.get_system_status()

        if "lock screen" in cmd or "lock laptop" in cmd:
            return SystemControl.lock_screen()

        # --- 8. TV Interaction ---
        if "tv" in cmd:
            return TVControl.get_status()

        # --- 9. Cloud Conversational Fallback ---
        return await Brain._ask_cloud_llm(text)

    @staticmethod
    async def _ask_cloud_llm(prompt: str) -> str:
        """Call Gemini API for free-form thinking, or fallback to local knowledge."""
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return "I'm offline from cloud intelligence right now, but your desktop commands are running at full speed."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": NEEL_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text.strip()
        except Exception:
            pass

        return "Got it. You can check your screen."
