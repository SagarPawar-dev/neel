import socket

TV_IP = "192.168.0.100"
TV_PORTS = [3000, 7000, 8080]

class TVControl:
    @staticmethod
    def is_tv_online() -> bool:
        """Check if LG webOS TV is awake on the local WiFi network."""
        for port in TV_PORTS:
            try:
                with socket.create_connection((TV_IP, port), timeout=1.5):
                    return True
            except (socket.timeout, OSError):
                continue
        return False

    @staticmethod
    def get_status() -> str:
        if TVControl.is_tv_online():
            return "Your LG webOS TV is currently online and reachable on the network at 192.168.0.100."
        return "The TV appears to be turned off or in deep standby."
