from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, Any, List
import time


@dataclass
class SharedState:
    lock: Lock = field(default_factory=Lock)
    running: bool = False
    authenticated: bool = False
    frame_bgr: Any = None

    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "fatigue_score": 0,
        "risk": "NORMAL",
        "confidence": 0.0,
        "ear": 0.0,
        "mar": 0.0,
        "face_found": False,
        "volume": 0,
        "last_event": "Idle",
        "updated_at": time.time(),
    })

    history: List[Dict[str, Any]] = field(default_factory=list)   # trend points
    events: List[Dict[str, Any]] = field(default_factory=list)    # timeline logs

    def update_metrics(self, payload: Dict[str, Any]):
        with self.lock:
            self.metrics.update(payload)
            self.metrics["updated_at"] = time.time()

            self.history.append({
                "ts": self.metrics["updated_at"],
                "fatigue_score": self.metrics.get("fatigue_score", 0),
                "confidence": self.metrics.get("confidence", 0.0),
            })
            if len(self.history) > 1200:
                self.history.pop(0)

    def add_event(self, level: str, message: str):
        with self.lock:
            self.events.append({
                "ts": time.strftime("%H:%M:%S"),
                "level": level,
                "message": message
            })
            if len(self.events) > 200:
                self.events.pop(0)


shared_state = SharedState()