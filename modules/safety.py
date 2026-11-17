import re
from typing import Tuple

# Dangerous patterns that require intelligent voice confirmation
DESTRUCTIVE_PATTERNS = [
    r"\brm\s+(-[rf]+\s+)?",
    r"\bdelete\b",
    r"\bformat\b",
    r"\bkill\b",
    r"\bpkill\b",
    r"\bsudo\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bdd\b",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
]

class SafetyGuard:
    @staticmethod
    def assess_risk(command_intent: str, details: str = "") -> Tuple[bool, str]:
        """
        Returns (is_risky, warning_message)
        - is_risky = False: Safe to execute immediately without nagging.
        - is_risky = True: Requires clear explanation & user confirmation.
        """
        combined = f"{command_intent} {details}".lower()

        # Check for file deletion
        if any(w in combined for w in ["delete", "remove", "rm ", "trash"]):
            return True, f"This will permanently delete {details or 'files'}. Should I proceed?"

        # Check for killing processes
        if any(w in combined for w in ["kill", "force close", "terminate"]):
            return True, f"This will force-kill {details or 'the application'}. Any unsaved work might be lost. Proceed?"

        # Check for system restarts / shutdowns
        if any(w in combined for w in ["shutdown", "power off", "reboot", "restart"]):
            return True, f"This will turn off or restart your laptop. Are you sure?"

        # Check for shell execution patterns
        for pattern in DESTRUCTIVE_PATTERNS:
            if re.search(pattern, combined):
                return True, f"This action could modify or remove system files. Do you want me to run it?"

        return False, ""

    @staticmethod
    def is_confirmation(response_text: str) -> bool:
        """Check if user confirmed with English or natural Hindi."""
        text = response_text.lower().strip()
        positive = ["yes", "yeah", "yup", "sure", "proceed", "confirm", "haan", "ha", "kar de", "do it"]
        return any(p in text for p in positive)

    @staticmethod
    def is_cancellation(response_text: str) -> bool:
        text = response_text.lower().strip()
        negative = ["no", "nah", "cancel", "stop", "abort", "ruk", "mat kar", "rahne de", "dont"]
        return any(n in text for n in negative)
