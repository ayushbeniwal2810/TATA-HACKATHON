import cv2
import time
import threading

from config import DMSConfig
from dms.driver_monitor import DriverMonitor
from dms.gesture_controller import GestureController
from dms.auth_system import AuthSystem
from dms.alarm_manager import AlarmManager
from dms.fatigue_meter import FatigueMeter
from app_state import shared_state

_thread = None


def _run_loop():
    cfg = DMSConfig()
    auth = AuthSystem(timeout_sec=cfg.auth_timeout_sec)
    alarm = AlarmManager(cooldown_sec=cfg.alarm_cooldown_sec)
    fatigue_meter = FatigueMeter()

    driver_monitor = DriverMonitor(
        ear_thr=cfg.ear_threshold,
        mar_thr=cfg.mar_threshold,
        eyes_sec=cfg.eyes_closed_duration_sec,
        yawn_sec=cfg.yawn_duration_sec,
        model_path=cfg.face_model_path,
    )

    gesture = GestureController(
        pinch_min=cfg.pinch_min_dist,
        pinch_max=cfg.pinch_max_dist,
        smoothing=cfg.volume_smoothing,
        model_path=cfg.hand_model_path,
    )

    cap = cv2.VideoCapture(cfg.camera_index)
    if not cap.isOpened():
        shared_state.update_metrics({"last_event": "Camera open failed"})
        shared_state.add_event("ERROR", "Camera open failed")
        shared_state.running = False
        return

    shared_state.running = True
    shared_state.update_metrics({"last_event": "DMS started"})
    shared_state.add_event("INFO", "DMS started")

    while shared_state.running:
        ok, frame = cap.read()
        if not ok:
            shared_state.update_metrics({"last_event": "Frame read failed"})
            time.sleep(0.05)
            continue

        frame = cv2.flip(frame, 1)
        now_ts = time.time()

        authenticated = auth.is_authenticated(now_ts) or shared_state.authenticated
        if shared_state.authenticated and not auth.is_authenticated(now_ts):
            auth.mark_authenticated(now_ts)

        if not authenticated:
            _, auth_msg = auth.process(frame, now_ts)
            shared_state.update_metrics({
                "face_found": False,
                "ear": 0.0,
                "mar": 0.0,
                "fatigue_score": 0,
                "risk": "NORMAL",
                "confidence": 0.0,
                "last_event": f"AUTH: {auth_msg}",
            })
        else:
            frame, drowsy = driver_monitor.process(frame, now_ts=now_ts)
            frame, volume, _ = gesture.process(frame)

            if drowsy["eyes_closed_alarm"]:
                alarm.trigger("eyes_closed", now_ts)
                shared_state.add_event("ALERT", "Eyes closed detected")

            if drowsy["yawn_warning"]:
                alarm.trigger("yawn", now_ts)
                shared_state.add_event("WARN", "Yawning detected")

            fat = fatigue_meter.update(
                now_ts=now_ts,
                face_found=drowsy["face_found"],
                eyes_closed_flag=drowsy["eyes_closed_alarm"],
                yawn_flag=drowsy["yawn_warning"],
            )

            if fat["risk"] == "CRITICAL":
                alarm.trigger("fatigue_critical", now_ts)
                shared_state.add_event("CRITICAL", "Fatigue critical")
            elif fat["risk"] == "HIGH":
                alarm.trigger("fatigue_high", now_ts)
                shared_state.add_event("WARN", "Fatigue high")

            shared_state.update_metrics({
                "face_found": drowsy["face_found"],
                "ear": round(drowsy["ear"], 3),
                "mar": round(drowsy["mar"], 3),
                "fatigue_score": fat["fatigue_score"],
                "risk": fat["risk"],
                "confidence": fat["confidence"],
                "volume": volume,
                "last_event": "Monitoring active",
            })

        with shared_state.lock:
            shared_state.frame_bgr = frame

    cap.release()
    shared_state.update_metrics({"last_event": "DMS stopped"})
    shared_state.add_event("INFO", "DMS stopped")


def start_dms():
    global _thread
    if _thread and _thread.is_alive():
        return
    _thread = threading.Thread(target=_run_loop, daemon=True)
    _thread.start()


def stop_dms():
    shared_state.running = False


def authenticate_demo():
    shared_state.authenticated = True
    shared_state.add_event("INFO", "Demo authentication enabled")