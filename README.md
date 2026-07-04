# Smart In-Cabin Driver Monitoring System (DMS)

AI-powered **Driver Monitoring + Gesture Control** project built in Python using **OpenCV** and **MediaPipe Tasks API**.

This system is designed for in-cabin safety and interaction:
- Detects driver drowsiness signs (eyes closed, yawning)
- Supports demo authentication flow
- Includes hand gesture-based volume control
- Triggers alarms for risky conditions

---

## Features

- **Face-based driver monitoring**
  - Eye Aspect Ratio (EAR) based prolonged eye-closure detection
  - Mouth Aspect Ratio (MAR) based yawn detection
- **Alarm manager**
  - Cooldown-based alert triggering
  - Extensible audio warning system
- **Gesture controller**
  - Pinch-distance based volume estimation
- **Authentication gate (demo mode)**
  - Press `A` to authenticate during runtime demo
- **Real-time visual status panel**
  - Auth status, face detection, EAR/MAR values, alerts, volume

---

## Project Structure

```text
TATA-HACKATHON/
├── main.py
├── config.py
├── dms/
│   ├── alarm_manager.py
│   ├── auth_system.py
│   ├── driver_monitor.py
│   ├── gesture_controller.py
│   └── utils.py
├── models/
│   ├── face_landmarker.task
│   └── hand_landmarker.task
└── README.md
```

---

## Tech Stack

- **Python 3.13**
- **OpenCV**
- **MediaPipe Tasks (Vision)**
- NumPy

---

## Setup

### 1) Clone repository
```bash
git clone https://github.com/ayushbeniwal2810/TATA-HACKATHON.git
cd TATA-HACKATHON
```

### 2) Create and activate virtual environment (recommended)
```bash
python3.13 -m venv .venv313
source .venv313/bin/activate
```

### 3) Install dependencies
```bash
pip install --upgrade pip
pip install opencv-python mediapipe numpy
```

### 4) Download required MediaPipe models
Create a `models/` folder and place:
- `face_landmarker.task`
- `hand_landmarker.task`

> The app will exit with an error if these files are missing.

---

## Run

```bash
python main.py
```

Controls:
- Press **A** → authenticate (demo mode)
- Press **Q** → quit

---

## Configuration

Edit `config.py` for thresholds and tuning:

- `ear_threshold`
- `mar_threshold`
- `eyes_closed_duration_sec`
- `yawn_duration_sec`
- `alarm_cooldown_sec`
- gesture pinch parameters

---

## Current Status

✅ Core webcam pipeline running  
✅ Gesture control working  
✅ Face monitoring integrated  
✅ Demo auth flow integrated  

🔧 In refinement:
- Alarm audio reliability across environments
- Yawn detection calibration per lighting/face distance
- Biometric profile support (planned)

---

## Troubleshooting

### 1) `ImportError` for custom modules
Ensure project structure and filenames match imports exactly and run from repo root.

### 2) Camera opens but no face detection
- Improve lighting
- Keep face centered and closer
- Verify `models/face_landmarker.task` exists
- Recheck `driver_monitor.py` running mode (`VIDEO` for stream)

### 3) MediaPipe warning logs in terminal
Most `I0000/W0000` logs are informational and non-fatal unless app crashes.

### 4) Alarm not audible
Depends on OS/audio backend and configured alarm implementation; verify system output device and test alarm manually.

---

## Roadmap

- [ ] Biometric profile module
- [ ] Backend logging/API integration
- [ ] Session analytics dashboard
- [ ] Improved alert policies and personalization
- [ ] Production-grade packaging

---

## Author

**Ayush Beniwal**  
GitHub: [@ayushbeniwal2810](https://github.com/ayushbeniwal2810)

---

## License

This project is currently for hackathon/prototype use.  
Add a license file (`MIT`, `Apache-2.0`, etc.) before production/public reuse.
