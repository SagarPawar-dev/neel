import subprocess
import urllib.parse

class ChromeControl:
    @staticmethod
    def _send_key_to_chrome(key: str) -> bool:
        """Send a keyboard shortcut directly to the active Google Chrome window."""
        try:
            # Find visible chrome windows
            proc = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--class", "google-chrome"],
                capture_output=True,
                text=True,
                check=False
            )
            wids = proc.stdout.strip().split()
            if not wids:
                return False

            # Focus the most recent chrome window and send key
            wid = wids[-1]
            subprocess.run(["xdotool", "windowactivate", "--sync", wid], check=False)
            subprocess.run(["xdotool", "key", "--window", wid, key], check=False)
            return True
        except Exception:
            return False

    @staticmethod
    def search_google(query: str) -> str:
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.google.com/search?q={encoded}"
        subprocess.Popen(
            ["google-chrome", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Searching Google for {query}."

    @staticmethod
    def search_youtube(query: str) -> str:
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        subprocess.Popen(
            ["google-chrome", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Opening YouTube for {query}."

    @staticmethod
    def play_pause_media() -> str:
        # First try standard Linux playerctl MPRIS interface
        try:
            res = subprocess.run(["playerctl", "play-pause"], capture_output=True, check=False)
            if res.returncode == 0:
                return "Playback toggled."
        except Exception:
            pass

        # Fallback to sending Space key to Chrome window
        if ChromeControl._send_key_to_chrome("space"):
            return "Toggled video playback."
        return "Couldn't locate active media."

    @staticmethod
    def toggle_fullscreen() -> str:
        if ChromeControl._send_key_to_chrome("f"):
            return "Toggled fullscreen."
        return "Chrome window not found."

    @staticmethod
    def toggle_video_mute() -> str:
        if ChromeControl._send_key_to_chrome("m"):
            return "Toggled video mute."
        return "Chrome window not found."

    @staticmethod
    def close_tab() -> str:
        if ChromeControl._send_key_to_chrome("ctrl+w"):
            return "Tab closed."
        return "Chrome window not found."

    @staticmethod
    def new_tab(url: str = "") -> str:
        if url:
            subprocess.Popen(
                ["google-chrome", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return f"Opening {url}."
        elif ChromeControl._send_key_to_chrome("ctrl+t"):
            return "New tab opened."
        return "Chrome window not found."
