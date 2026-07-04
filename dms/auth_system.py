import time


class AuthSystem:
    """
    Simple placeholder auth gate.
    Press 'a' in the main window to simulate successful authentication.
    """
    def __init__(self, timeout_sec=60):
        self.timeout_sec = timeout_sec
        self.authenticated_at = None

    def is_authenticated(self, now_ts=None):
        if now_ts is None:
            now_ts = time.time()
        if self.authenticated_at is None:
            return False
        return (now_ts - self.authenticated_at) <= self.timeout_sec

    def process(self, frame, now_ts=None):
        """
        Placeholder process hook.
        Returns:
          (auth_ok: bool, auth_msg: str)
        """
        if now_ts is None:
            now_ts = time.time()

        # Keep unauthenticated until external trigger.
        # You can later replace this with face recognition / PIN / RFID.
        if self.is_authenticated(now_ts):
            return True, "Verified"
        return False, "Not verified"

    def mark_authenticated(self, now_ts=None):
        if now_ts is None:
            now_ts = time.time()
        self.authenticated_at = now_ts