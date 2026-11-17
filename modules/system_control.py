import os
import subprocess
import time
import psutil

# App aliases mapping voice words to Linux commands
APP_ALIASES = {
    "chrome": ["google-chrome"],
    "browser": ["google-chrome"],
    "code": ["code"],
    "vscode": ["code"],
    "antigravity": ["antigravity-app"],
    "terminal": ["gnome-terminal"],
    "files": ["nemo"],
    "file manager": ["nemo"],
    "calculator": ["gnome-calculator"],
    "monitor": ["gnome-system-monitor"],
    "system monitor": ["gnome-system-monitor"],
    "settings": ["cinnamon-settings"],
}

class SystemControl:
    @staticmethod
    def launch_app(app_name: str) -> str:
        app_name = app_name.lower().strip()
        cmd = APP_ALIASES.get(app_name)
        if not cmd:
            cmd = [app_name]

        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return f"Opening {app_name}."
        except FileNotFoundError:
            return f"I couldn't find an application named {app_name} on your laptop."
        except Exception as e:
            return f"Failed to launch {app_name}: {e}"

    @staticmethod
    def adjust_volume(action: str) -> str:
        """action can be 'up', 'down', 'mute', or a specific number e.g. '50%'"""
        action = action.lower().strip()
        try:
            if "up" in action:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"], check=True)
                return "Volume increased."
            elif "down" in action:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"], check=True)
                return "Volume decreased."
            elif "mute" in action or "unmute" in action:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=True)
                return "Volume toggled."
            else:
                # If numeric e.g. "50"
                num = ''.join(c for c in action if c.isdigit())
                if num:
                    val = max(0, min(100, int(num)))
                    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{val}%"], check=True)
                    return f"Volume set to {val}%."
        except Exception as e:
            return f"Could not adjust volume: {e}"
        return "Volume adjusted."

    @staticmethod
    def adjust_brightness(action: str) -> str:
        """Adjust display brightness via xrandr or brightnessctl."""
        action = action.lower().strip()
        try:
            if "up" in action:
                subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", "1.0"], check=False)
                return "Brightness set to maximum."
            elif "down" in action or "dim" in action:
                subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", "0.4"], check=False)
                return "Screen dimmed."
            else:
                num = ''.join(c for c in action if c.isdigit())
                if num:
                    val = max(10, min(100, int(num))) / 100.0
                    subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", str(val)], check=False)
                    return f"Brightness set to {int(val*100)}%."
        except Exception as e:
            return f"Brightness adjustment failed: {e}"
        return "Brightness adjusted."

    @staticmethod
    def take_screenshot() -> str:
        pictures_dir = os.path.expanduser("~/Pictures")
        os.makedirs(pictures_dir, exist_ok=True)
        filename = f"Screenshot_{int(time.time())}.png"
        filepath = os.path.join(pictures_dir, filename)

        try:
            subprocess.run(["gnome-screenshot", "-f", filepath], check=True)
            return "Screenshot saved to your Pictures folder."
        except Exception as e:
            return f"Screenshot failed: {e}"

    @staticmethod
    def get_system_status() -> str:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()

        status_parts = [
            f"CPU is at {int(cpu)} percent.",
            f"RAM usage is {int(mem.percent)} percent with {int(mem.available / (1024*1024))} megabytes free."
        ]

        if battery:
            plugged = "plugged in" if battery.power_plugged else "on battery power"
            status_parts.append(f"Battery is at {int(battery.percent)} percent, currently {plugged}.")

        return " ".join(status_parts)

    @staticmethod
    def lock_screen() -> str:
        try:
            subprocess.run(["cinnamon-screensaver-command", "-l"], check=False)
            return "Screen locked."
        except Exception:
            return "Unable to lock screen."

    @staticmethod
    def kill_process(proc_name: str) -> str:
        proc_name = proc_name.lower().strip()
        try:
            subprocess.run(["pkill", "-f", proc_name], check=True)
            return f"Terminated {proc_name}."
        except subprocess.CalledProcessError:
            return f"No running process matching {proc_name} was found."
