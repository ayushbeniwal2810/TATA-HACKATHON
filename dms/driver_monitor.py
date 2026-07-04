import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .utils import eye_aspect_ratio, mouth_aspect_ratio


class DriverMonitor:
    def __init__(
        self,
        ear_thr=0.21,
        mar_thr=0.60,
        eyes_sec=2.0,
        yawn_sec=1.5,
        model_path="models/face_landmarker.task",
    ):
        self.ear_thr = ear_thr
        self.mar_thr = mar_thr
        self.eyes_sec = eyes_sec
        self.yawn_sec = yawn_sec

        self.eyes_closed_start = None
        self.yawn_start = None

        # Face mesh landmark indices
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        self.MOUTH_TOP = 13
        self.MOUTH_BOTTOM = 14

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.3,
            min_face_presence_confidence=0.3,
            min_tracking_confidence=0.3,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    @staticmethod
    def _pt(lm, idx, w, h):
        p = lm[idx]
        return (int(p.x * w), int(p.y * h))

    def process(self, frame, now_ts=None):
        if now_ts is None:
            now_ts = time.time()

        out = {
            "face_found": False,
            "ear": 0.0,
            "mar": 0.0,
            "eyes_closed_alarm": False,
            "yawn_warning": False,
            "status_msgs": [],
        }

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        ts_ms = int(now_ts * 1000)
        result = self.detector.detect_for_video(mp_image, ts_ms)

        if not result.face_landmarks:
            self.eyes_closed_start = None
            self.yawn_start = None
            return frame, out

        lm = result.face_landmarks[0]
        out["face_found"] = True

        # Draw a few key points so you can confirm detection visually
        debug_ids = [1, 33, 263, 13, 14, 61, 291]
        for i in debug_ids:
            x, y = self._pt(lm, i, w, h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        left_eye_pts = [self._pt(lm, i, w, h) for i in self.LEFT_EYE]
        right_eye_pts = [self._pt(lm, i, w, h) for i in self.RIGHT_EYE]
        ear = (eye_aspect_ratio(left_eye_pts) + eye_aspect_ratio(right_eye_pts)) / 2.0
        out["ear"] = ear

        m_left = self._pt(lm, self.MOUTH_LEFT, w, h)
        m_right = self._pt(lm, self.MOUTH_RIGHT, w, h)
        m_top = self._pt(lm, self.MOUTH_TOP, w, h)
        m_bottom = self._pt(lm, self.MOUTH_BOTTOM, w, h)
        mar = mouth_aspect_ratio([m_left, m_right, m_top, m_bottom])
        out["mar"] = mar

        if ear < self.ear_thr:
            if self.eyes_closed_start is None:
                self.eyes_closed_start = now_ts
            elif (now_ts - self.eyes_closed_start) >= self.eyes_sec:
                out["eyes_closed_alarm"] = True
                out["status_msgs"].append("DRIVER ALERT! Eyes closed")
        else:
            self.eyes_closed_start = None

        if mar > self.mar_thr:
            if self.yawn_start is None:
                self.yawn_start = now_ts
            elif (now_ts - self.yawn_start) >= self.yawn_sec:
                out["yawn_warning"] = True
                out["status_msgs"].append("Drowsiness Warning: Yawning")
        else:
            self.yawn_start = None

        return frame, out