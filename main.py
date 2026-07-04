import cv2
import time
import os
import sys

from config import DMSConfig
from dms.driver_monitor import DriverMonitor
from dms.gesture_controller import GestureController
from dms.auth_system import AuthSystem
from dms.alarm_manager import AlarmManager


def ensure_models():
    required = [
        "models/face_landmarker.task",
        "models/hand_landmarker.task",
    ]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        print("\n[ERROR] Missing MediaPipe model file(s):")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease download and place them in the models/ directory, then run again.")
        sys.exit(1)


def draw_status_panel(frame, status_lines, start_y=30):
    y = start_y
    for line, color in status_lines:
        cv2.putText(
            frame,
            line,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA
        )
        y += 30
    return frame


def main():
    ensure_models()
    cfg = DMSConfig()

    auth = AuthSystem(timeout_sec=cfg.auth_timeout_sec)
    alarm = AlarmManager(cooldown_sec=cfg.alarm_cooldown_sec)

    driver_monitor = DriverMonitor(
        ear_thr=cfg.ear_threshold,
        mar_thr=cfg.mar_threshold,
        eyes_sec=cfg.eyes_closed_duration_sec,
        yawn_sec=cfg.yawn_duration_sec,
        model_path=cfg.face_model_path
    )

    gesture = GestureController(
        pinch_min=cfg.pinch_min_dist,
        pinch_max=cfg.pinch_max_dist,
        smoothing=cfg.volume_smoothing,
        model_path=cfg.hand_model_path
    )

    cap = cv2.VideoCapture(cfg.camera_index)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Press 'a' to authenticate (demo), 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[WARN] Failed to read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        now_ts = time.time()

        status_lines = []

        # 1) Authentication gate
        authenticated = auth.is_authenticated(now_ts)
        if not authenticated:
            auth_ok, auth_msg = auth.process(frame, now_ts)
            color = (0, 255, 0) if auth_ok else (0, 165, 255)
            status_lines.append((f"AUTH: {auth_msg}", color))
            status_lines.append(("Press 'A' to authenticate (demo)", (180, 180, 180)))
        else:
            status_lines.append(("AUTH: Verified", (0, 255, 0)))

            # 2) Driver monitoring
            frame, drowsy = driver_monitor.process(frame, now_ts=now_ts)
            if drowsy["face_found"]:
                status_lines.append(("Face: Detected", (0, 255, 0)))
                status_lines.append((f"EAR: {drowsy['ear']:.2f}", (255, 255, 0)))
                status_lines.append((f"MAR: {drowsy['mar']:.2f}", (255, 255, 0)))
            else:
                status_lines.append(("Face: Not detected", (0, 0, 255)))            

            if drowsy["eyes_closed_alarm"]:
                status_lines.append(("ALERT: Eyes closed!", (0, 0, 255)))
                alarm.trigger("eyes_closed", now_ts)

            if drowsy["yawn_warning"]:
                status_lines.append(("WARNING: Yawning!", (0, 140, 255)))
                alarm.trigger("yawn", now_ts)

            # 3) Gesture volume control
            frame, volume, volume_event = gesture.process(frame)
            status_lines.append((f"Volume: {volume}%", (200, 200, 255)))
            if volume_event:
                status_lines.append((volume_event, (255, 200, 100)))

        frame = draw_status_panel(frame, status_lines, start_y=30)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):
            auth.mark_authenticated(now_ts)
            print("[INFO] Authenticated (demo).")
        elif key == ord('q'):
            break

        cv2.imshow("Smart In-Cabin Driver Monitoring System", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()