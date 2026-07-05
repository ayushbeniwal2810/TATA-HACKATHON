import time
import cv2
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
import sys
from app_state import shared_state


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app_state import shared_state
from dms_service import start_dms, stop_dms, authenticate_demo
from dms_service import start_dms, stop_dms, authenticate_demo

st.set_page_config(page_title="DMS Dashboard", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #0f172a;
    color: #e2e8f0;
}
.block-container {padding-top: 1rem;}
.card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 14px;
}
.badge {
    display:inline-block;padding:6px 10px;border-radius:999px;font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 Smart In-Cabin Driver Monitoring System")

# ---------- Header controls ----------
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("▶ Start", use_container_width=True):
        start_dms()
with c2:
    if st.button("■ Stop", use_container_width=True):
        stop_dms()
with c3:
    if st.button("✅ Authenticate", use_container_width=True):
        authenticate_demo()
with c4:
    with shared_state.lock:
        running = shared_state.running
    st.markdown(f"**Status:** {'🟢 Running' if running else '⚪ Stopped'}")

left, right = st.columns([1.8, 1])

video_slot = left.empty()
panel_slot = right.empty()
trend_slot = st.empty()
events_slot = st.empty()


def risk_color(risk: str):
    return {
        "NORMAL": "#22c55e",
        "MILD": "#eab308",
        "HIGH": "#f97316",
        "CRITICAL": "#ef4444",
    }.get(risk, "#94a3b8")


while True:
    with shared_state.lock:
        frame = shared_state.frame_bgr.copy() if shared_state.frame_bgr is not None else None
        m = dict(shared_state.metrics)
        hist = list(shared_state.history)
        events = list(shared_state.events)
        running = shared_state.running

    # Video panel
    if frame is not None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_slot.image(rgb, channels="RGB", use_container_width=True)
    else:
        video_slot.info("Camera feed not available. Click Start.")

    # Right metrics panel
    rc = risk_color(m["risk"])
    panel_slot.markdown(f"""
    <div class="card">
      <h3 style="margin-top:0;">Fatigue Meter</h3>
      <h1 style="margin:0;color:{rc};">{m['fatigue_score']}%</h1>
      <span class="badge" style="background:{rc}22;color:{rc};border:1px solid {rc};">
        {m['risk']}
      </span>
      <hr style="border-color:#1f2937;">
      <p>Confidence: <b>{int(m['confidence']*100)}%</b></p>
      <p>Face: <b>{"Detected" if m["face_found"] else "Not detected"}</b></p>
      <p>EAR: <b>{m["ear"]}</b> &nbsp;&nbsp; MAR: <b>{m["mar"]}</b></p>
      <p>Volume: <b>{m["volume"]}%</b></p>
      <p style="color:#94a3b8;">Last event: {m["last_event"]}</p>
    </div>
    """, unsafe_allow_html=True)

    # Trend chart
    if hist:
        df = pd.DataFrame(hist)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["fatigue_score"], mode="lines",
            name="Fatigue %", line=dict(color="#38bdf8", width=3)
        ))
        fig.update_layout(
            template="plotly_dark",
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Time",
            yaxis_title="Fatigue %",
            yaxis_range=[0, 100],
            paper_bgcolor="#0f172a",
            plot_bgcolor="#111827",
        )
        trend_slot.plotly_chart(fig, use_container_width=True)

    # Event log
    if events:
        edf = pd.DataFrame(events[::-1][:12])  # latest 12
        events_slot.dataframe(edf, use_container_width=True, hide_index=True)

    time.sleep(0.08 if running else 0.2)