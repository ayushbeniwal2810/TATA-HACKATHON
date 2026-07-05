# Smart In-Cabin Driver Monitoring System (DMS)

AI-powered **Driver Monitoring + Gesture Control** project built in Python using **OpenCV**, **MediaPipe Tasks API**, and a **Streamlit frontend dashboard**.

## What it does

- Monitors driver state from webcam feed
- Detects:
  - prolonged eye closure (drowsiness)
  - yawning events
- Computes a live **Fatigue Meter (%)**
- Supports demo authentication flow
- Supports hand-gesture based volume control
- Triggers alerts/alarms based on risk level
- Displays live telemetry in frontend dashboard

---

## Project Structure

```text
TATA-HACKATHON/
├── main.py                  # Backend-only app runner (OpenCV window)
├── frontend.py              # Streamlit UI
├── dms_service.py           # Background DMS loop for frontend
├── app_state.py             # Shared state between backend loop and UI
├── config.py
├── requirements.txt
├── dms/
│   ├── __init__.py
│   ├── alarm_manager.py
│   ├── auth_system.py
│   ├── driver_monitor.py
│   ├── fatigue_meter.py
│   ├── gesture_controller.py
│   └── utils.py
└── models/
    ├── face_landmarker.task
    └── hand_landmarker.task
```

---

## Prerequisites

- Python **3.10+** (tested on 3.13)
- Webcam access enabled
- MediaPipe task models downloaded into `models/`

Required model files:
- `models/face_landmarker.task`
- `models/hand_landmarker.task`

---

## Setup

```bash
git clone https://github.com/ayushbeniwal2810/TATA-HACKATHON.git
cd TATA-HACKATHON
python3.13 -m venv .venv313
source .venv313/bin/activate      # macOS/Linux
# .venv313\Scripts\activate       # Windows
pip install --upgrade pip
pip install -r requirements.txt
```
---

## Run Options

## 1) Run backend-only mode (OpenCV window)

```bash
python main.py
```

Controls:
- `A` → demo authenticate
- `Z` → manual alarm test
- `Q` → quit

---

## 2) Run full frontend dashboard (recommended)

```bash
streamlit run frontend.py
```

Frontend provides:
- Live camera feed
- Fatigue % and risk band
- Confidence / EAR / MAR / volume
- Start / Stop / Authenticate controls
- Trend graph + recent event log

---

## Fatigue Meter (high level)

Fatigue score (0–100) is derived from:
- eye-closure persistence
- PERCLOS-like eye closure ratio over time window
- yawn ratio over time window

Risk bands:
- `0–29` NORMAL
- `30–59` MILD
- `60–79` HIGH
- `80–100` CRITICAL

---

## Troubleshooting

- If Streamlit cannot import local files:
  - run command from repo root
  - ensure `dms/__init__.py` exists
- If camera fails:
  - close other apps using webcam
  - check camera permissions
- If no landmarks detected:
  - verify model files exist in `models/`
  - improve lighting / face position
- If alarm not audible:
  - verify system output device
  - test using OS sound command directly

---

## Current Status

- ✅ Backend detection pipeline integrated
- ✅ Fatigue meter integrated
- ✅ Frontend dashboard integrated
- 🔧 Ongoing threshold calibration for varied environments

---

## Author

Ayush Beniwal  
GitHub: [@ayushbeniwal2810](https://github.com/ayushbeniwal2810)