import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .utils import euclidean, map_range


class GestureController:
    """
    MediaPipe Tasks-based hand gesture volume controller.
    """
    def __init__(self, pinch_min=20, pinch_max=140, smoothing=0.25,
                 model_path="models/hand_landmarker.task"):
        self.pinch_min = pinch_min
        self.pinch_max = pinch_max
        self.smoothing = smoothing

        self.current_volume = 40.0
        self.prev_volume = self.current_volume

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process(self, frame):
        volume_event = None
        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)

        if result.hand_landmarks:
            hand_lm = result.hand_landmarks[0]  # first hand
            thumb = hand_lm[4]   # thumb tip
            index = hand_lm[8]   # index tip

            tx, ty = int(thumb.x * w), int(thumb.y * h)
            ix, iy = int(index.x * w), int(index.y * h)

            dist = euclidean((tx, ty), (ix, iy))
            target_volume = map_range(dist, self.pinch_min, self.pinch_max, 0, 100)
            self.current_volume = (1 - self.smoothing) * self.current_volume + self.smoothing * target_volume

            if self.current_volume - self.prev_volume > 2:
                volume_event = f"Volume Up [{int(self.current_volume)}%]"
            elif self.prev_volume - self.current_volume > 2:
                volume_event = f"Volume Down [{int(self.current_volume)}%]"

            self.prev_volume = self.current_volume

            cv2.circle(frame, (tx, ty), 6, (0, 255, 0), -1)
            cv2.circle(frame, (ix, iy), 6, (0, 255, 0), -1)
            cv2.line(frame, (tx, ty), (ix, iy), (255, 0, 0), 2)

        return frame, int(self.current_volume), volume_event