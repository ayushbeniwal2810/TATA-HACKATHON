from collections import deque


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


class FatigueMeter:
    """
    Fatigue score (0-100) from:
      - eye closure persistence (EAR proxy input)
      - PERCLOS-like ratio (eyes_closed_flag over last 60s)
      - yawn ratio (yawn_flag over last 60s)

    update(...) expects booleans from driver_monitor:
      eyes_closed_flag: True when prolonged eye closure condition is active
      yawn_flag: True when yawn warning condition is active
    """

    def __init__(
        self,
        long_window_sec=60.0,
        ema_alpha=0.2,
        w_eye=0.45,
        w_perclos=0.35,
        w_yawn=0.20,
    ):
        self.long_window_sec = long_window_sec
        self.ema_alpha = ema_alpha

        self.w_eye = w_eye
        self.w_perclos = w_perclos
        self.w_yawn = w_yawn

        # events as (timestamp, flag_int)
        self.eye_events = deque()
        self.yawn_events = deque()
        self.face_events = deque()

        self.prev_ts = None
        self.eye_closed_run_sec = 0.0
        self.smoothed_score = 0.0

    def _prune(self, dq, now_ts):
        cut = now_ts - self.long_window_sec
        while dq and dq[0][0] < cut:
            dq.popleft()

    @staticmethod
    def _ratio(dq):
        if not dq:
            return 0.0
        s = sum(v for _, v in dq)
        return s / float(len(dq))

    def update(self, now_ts, face_found, eyes_closed_flag, yawn_flag):
        # dt for run-length logic
        if self.prev_ts is None:
            dt = 0.0
        else:
            dt = max(0.0, now_ts - self.prev_ts)
        self.prev_ts = now_ts

        # Store frame-level flags
        self.eye_events.append((now_ts, 1 if eyes_closed_flag else 0))
        self.yawn_events.append((now_ts, 1 if yawn_flag else 0))
        self.face_events.append((now_ts, 1 if face_found else 0))

        self._prune(self.eye_events, now_ts)
        self._prune(self.yawn_events, now_ts)
        self._prune(self.face_events, now_ts)

        # eye closure persistence
        if eyes_closed_flag:
            self.eye_closed_run_sec += dt
        else:
            self.eye_closed_run_sec = 0.0

        # Component 1: eye persistence score
        # 0 sec -> 0, 3+ sec -> 100
        eye_score = _clamp((self.eye_closed_run_sec / 3.0) * 100.0)

        # Component 2: PERCLOS-like ratio in 60s window
        perclos_ratio = self._ratio(self.eye_events)       # 0..1
        perclos_score = _clamp((perclos_ratio / 0.40) * 100.0)  # 40% closure -> high risk

        # Component 3: yawn ratio in 60s window
        yawn_ratio = self._ratio(self.yawn_events)         # 0..1
        yawn_score = _clamp((yawn_ratio / 0.20) * 100.0)   # 20% yawn-warning frames -> high risk

        raw_score = (
            self.w_eye * eye_score
            + self.w_perclos * perclos_score
            + self.w_yawn * yawn_score
        )

        # Confidence from face visibility
        face_ratio = self._ratio(self.face_events)  # 0..1
        confidence = face_ratio

        # Penalize score if face missing too often
        if face_ratio < 0.5:
            raw_score *= (0.5 + face_ratio)  # reduce up to half when very low visibility

        raw_score = _clamp(raw_score)

        # EMA smoothing
        self.smoothed_score = (
            self.ema_alpha * raw_score + (1.0 - self.ema_alpha) * self.smoothed_score
        )

        fatigue = int(round(_clamp(self.smoothed_score)))

        if fatigue < 30:
            risk = "NORMAL"
        elif fatigue < 60:
            risk = "MILD"
        elif fatigue < 80:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        return {
            "fatigue_score": fatigue,
            "risk": risk,
            "confidence": round(float(confidence), 2),
            "components": {
                "eye": int(round(eye_score)),
                "perclos": int(round(perclos_score)),
                "yawn": int(round(yawn_score)),
            },
            "debug": {
                "eye_closed_run_sec": round(self.eye_closed_run_sec, 2),
                "perclos_ratio": round(perclos_ratio, 3),
                "yawn_ratio": round(yawn_ratio, 3),
            },
        }