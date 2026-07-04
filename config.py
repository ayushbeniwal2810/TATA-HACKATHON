class DMSConfig:
    camera_index = 0

    ear_threshold = 0.21
    mar_threshold = 0.45          # was 0.60, too high for many faces
    eyes_closed_duration_sec = 2.0
    yawn_duration_sec = 1.0        # was 1.5, reduce for easier trigger

    auth_timeout_sec = 60
    alarm_cooldown_sec = 2.0

    pinch_min_dist = 20
    pinch_max_dist = 140
    volume_smoothing = 0.25

    face_model_path = "models/face_landmarker.task"
    hand_model_path = "models/hand_landmarker.task"