import time
import threading
import platform
import subprocess


class AlarmManager:
    def __init__(self, cooldown_sec=2.0):
        self.cooldown_sec = cooldown_sec
        self.last_trigger_ts = {}

    def can_trigger(self, key, now_ts=None):
        if now_ts is None:
            now_ts = time.time()
        last = self.last_trigger_ts.get(key)
        if last is None:
            return True
        return (now_ts - last) >= self.cooldown_sec

    def _play_alarm(self, key):
        system = platform.system().lower()
        try:
            if "darwin" in system:
                # macOS: guaranteed built-in voice + beep
                msg = "Driver alert" if key == "eyes_closed" else "Drowsiness warning"
                subprocess.Popen(["say", msg])
                subprocess.Popen(["afplay", "/System/Library/Sounds/Sosumi.aiff"])
            elif "windows" in system:
                import winsound
                winsound.Beep(1200, 400)
            else:
                # Linux fallback
                print("\a", end="", flush=True)
        except Exception:
            # final fallback
            print("\a", end="", flush=True)

    def trigger(self, key, now_ts=None):
        if now_ts is None:
            now_ts = time.time()

        if not self.can_trigger(key, now_ts):
            return False

        self.last_trigger_ts[key] = now_ts
        print(f"[ALARM] {key}")
        threading.Thread(target=self._play_alarm, args=(key,), daemon=True).start()
        return True