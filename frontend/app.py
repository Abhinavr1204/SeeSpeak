import streamlit as st
import cv2
import requests
import pyttsx3
import threading
import time
import pandas as pd

st.set_page_config(layout="wide", page_title="SeeSpeak Navigation", page_icon="🧭")

# ─── Custom CSS ───
st.markdown("""
<style>
    /* Global */
    .main { background-color: #f8f9fa; }
    h1 { color: #1f2937; font-weight: 700; }
    h2, h3 { color: #374151; }

    /* Cards */
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }

    /* Status Pills */
    .pill {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        color: white;
    }
    .pill-live { background-color: #10b981; }
    .pill-stopped { background-color: #6b7280; }
    .pill-error { background-color: #ef4444; }

    /* Navigation Box */
    .nav-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e40af;
    }

    /* Empty State */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 360px;
        color: #9ca3af;
        font-size: 1.1rem;
    }

    /* Sidebar */
    .sidebar-section {
        font-size: 0.85rem;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── TTS Engine ───
engine = pyttsx3.init()

def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

# ─── Session State ───
if "run" not in st.session_state:
    st.session_state.run = False
if "objects" not in st.session_state:
    st.session_state.objects = []
if "last_nav" not in st.session_state:
    st.session_state.last_nav = "Waiting to start..."
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# ─── Header ───
st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1> SeeSpeak Intelligent Navigation</h1>
        <p style="color: #6b7280; font-size: 1.05rem; margin-top: -0.5rem;">
            Real-time object detection, depth estimation, and voice-guided navigation
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("<div class='sidebar-section'>Controls</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start = st.button("▶ Start", use_container_width=True, type="primary")
    with col_btn2:
        stop = st.button("⏹ Stop", use_container_width=True, type="secondary")

    talk = st.button("🔊 Announce", use_container_width=True)

    st.markdown("<div class='sidebar-section'>System Status</div>", unsafe_allow_html=True)

    if st.session_state.run:
        st.markdown("<span class='pill pill-live'>● LIVE</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='pill pill-stopped'>● STOPPED</span>", unsafe_allow_html=True)

    if st.session_state.last_error:
        st.markdown(f"<span class='pill pill-error'>⚠ {st.session_state.last_error}</span>", unsafe_allow_html=True)

    st.caption("Ensure the backend is running on http://127.0.0.1:5000")

# ─── Button Logic ───
if start:
    st.session_state.run = True
    st.session_state.last_error = None
if stop:
    st.session_state.run = False

if talk:
    if st.session_state.objects:
        speak("I see " + ", ".join(st.session_state.objects[:3]))
    else:
        speak("Path is clear")

# ─── Main Layout ───
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("<div class='card'><div class='card-title'>📷 Live Camera Feed</div>", unsafe_allow_html=True)
    frame_placeholder = st.empty()
    if not st.session_state.run:
        frame_placeholder.markdown("""
            <div class='empty-state'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📷</div>
                <div>Camera is off. Press <b>▶ Start</b> to begin.</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Navigation Card
    st.markdown("<div class='card'><div class='card-title'>🧭 Navigation</div>", unsafe_allow_html=True)
    nav_box = st.empty()
    if st.session_state.run:
        nav_box.markdown(f"<div class='nav-box'>{st.session_state.last_nav}</div>", unsafe_allow_html=True)
    else:
        nav_box.markdown("<div style='color:#9ca3af; padding: 0.5rem 0;'>No active navigation data.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Detected Objects Card
    st.markdown("<div class='card'><div class='card-title'> Detected Objects</div>", unsafe_allow_html=True)
    table_box = st.empty()
    if st.session_state.objects:
        df = pd.DataFrame({
            "Object": st.session_state.objects,
            "Distance": st.session_state.get("distances", []),
            "Meters": st.session_state.get("meters", [])
        })
        table_box.dataframe(df, use_container_width=True, hide_index=True)
    else:
        table_box.markdown("<div style='color:#9ca3af; padding: 0.5rem 0;'>No objects detected yet.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Main Loop ───
if st.session_state.run:
    cap = cv2.VideoCapture(0)
    st.session_state.last_error = None

    for _ in range(300):
        ret, frame = cap.read()
        if not ret:
            st.session_state.last_error = "Camera disconnected"
            st.session_state.run = False
            st.rerun()
            break

        frame = cv2.resize(frame, (640, 480))
        _, img = cv2.imencode('.jpg', frame)

        try:
            res = requests.post(
                "http://127.0.0.1:5000/analyze",
                files={"image": img.tobytes()},
                timeout=5
            )
            res.raise_for_status()
            data = res.json()

            objects = data.get("objects", [])
            boxes = data.get("boxes", [])
            distances = data.get("distances", [])
            meters = data.get("meters", [])
            navigation = data.get("navigation", "No navigation")

        except requests.exceptions.ConnectionError:
            st.session_state.last_error = "Backend Offline"
            objects, boxes, distances, meters, navigation = [], [], [], [], "Backend Offline"
        except requests.exceptions.Timeout:
            st.session_state.last_error = "Request Timeout"
            objects, boxes, distances, meters, navigation = [], [], [], [], "Timeout"
        except Exception as e:
            st.session_state.last_error = "Analysis Error"
            objects, boxes, distances, meters, navigation = [], [], [], [], f"Error: {str(e)}"

        st.session_state.objects = objects
        st.session_state.distances = distances
        st.session_state.meters = meters
        st.session_state.last_nav = navigation

        for i, obj in enumerate(objects):
            if i < len(boxes):
                x1, y1, x2, y2 = boxes[i]
                label = f"{obj} ({meters[i]}m)" if i < len(meters) else obj
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, navigation,
                    (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 255), 2)

        frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

        # Update sidebar status dynamically inside loop
        # (Streamlit reruns the whole script, so we update placeholders)
        nav_box.markdown(f"<div class='nav-box'>{navigation}</div>", unsafe_allow_html=True)

        if objects:
            df = pd.DataFrame({
                "Object": objects,
                "Distance": distances,
                "Meters": meters
            })
            table_box.dataframe(df, use_container_width=True, hide_index=True)
        else:
            table_box.markdown("<div style='color:#9ca3af; padding: 0.5rem 0;'>No objects in frame.</div>", unsafe_allow_html=True)

        time.sleep(0.03)

    cap.release()
    st.session_state.run = False
    st.rerun()

