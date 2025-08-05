# importing all the necessary libraries

import os
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"
import streamlit as st
import pandas as pd
import time
import datetime
import cv2
import sqlite3
import winsound
from keras.models import load_model  
import cv2  
import numpy as np
import tensorflow.python
import tensorflow as tf
import altair as alt
from datetime import datetime, timedelta




# Loading  the labels
class_names = open("labels.txt", "r").readlines()
 




today = datetime.now()
today_string = today.strftime("%Y-%m-%d")
day = today - timedelta(days=today.weekday())
day_string = day.strftime("%Y-%m-%d")


# makes the database management consistent, reusable, and less error-prone
def execute_db_query(query, params=None, fetch=False):
    conn = sqlite3.connect('project.db')
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch:
            result = cur.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
    except sqlite3.Error as e:
        conn.close()
        raise e

execute_db_query("""CREATE TABLE IF NOT EXISTS project(
    username text,
    total_sesh_day integer,
    total_focus_time_day real,
    times_phone_stopped_day integer,
    total_sesh_week integer,
    total_focus_time_week real,
    times_phone_stopped_week integer,
    last_day_reset text,
    last_week_reset text
)""")

execute_db_query("""CREATE TABLE IF NOT EXISTS daily_stats (
    username TEXT,
    date TEXT,
    focus_time INTEGER,
    phone_detections INTEGER,
    PRIMARY KEY (username, date)
)""")


data = execute_db_query("SELECT * FROM project WHERE username = ?", ("Student",), fetch=True)

if len(data) == 0:
    execute_db_query("INSERT INTO project VALUES ('Student', 0, 0, 0, 0, 0, 0, '0-0-0', '0-0-0')")
    data = execute_db_query("SELECT * FROM project WHERE username = ?", ("Student",), fetch=True)

username = data[0][0]
last_day_reset = data[0][7]
last_week_reset = data[0][8]

if today_string != last_day_reset:
    execute_db_query("""UPDATE project SET
                 total_sesh_day = ?,
                 total_focus_time_day = ?,
                 times_phone_stopped_day = ?, 
                 last_day_reset = ?
                 WHERE username = ?""", (0, 0, 0, today_string, username))
    
    data = execute_db_query("SELECT * FROM project WHERE username = ?", ("Student",), fetch=True)


if day_string != last_week_reset:
    execute_db_query("""UPDATE project SET
                 total_sesh_week = ?,
                 total_focus_time_week = ?,
                 times_phone_stopped_week = ?,
                 last_week_reset = ?
                 WHERE username = ?""", (0, 0, 0, day_string, username))
    
    data = execute_db_query("SELECT * FROM project WHERE username = ?", ("Student",), fetch=True)


username = data[0][0]
total_sesh_day = data[0][1]
total_focus_time_day = data[0][2]
times_phone_stopped_day = data[0][3]
total_sesh_week = data[0][4]
total_focus_time_week = data[0][5]
times_phone_stopped_week = data[0][6]
last_day_reset = data[0][7]
last_week_reset = data[0][8]



st.set_page_config(
    page_title="Focus Timer",
    page_icon="⏳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #0a0b14;
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(102, 125, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 85% 80%, rgba(102, 125, 255, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(102, 125, 255, 0.05) 0%, transparent 50%);
        min-height: 100vh;
        overflow: hidden;
    }
    
    /* Animated particles background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(1px 1px at 20px 30px, rgba(255, 255, 255, 0.05), transparent),
            radial-gradient(1px 1px at 40px 70px, rgba(102, 125, 255, 0.1), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(102, 125, 255, 0.08), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255, 255, 255, 0.03), transparent);
        background-size: 150px 80px;
        animation: particle-float 25s infinite linear;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes particle-float {
        0% { transform: translateY(0px) translateX(0px); }
        33% { transform: translateY(-15px) translateX(8px); }
        66% { transform: translateY(-8px) translateX(-8px); }
        100% { transform: translateY(0px) translateX(0px); }
    }
            
    /* Hide only specific Streamlit elements - PRESERVE NAVIGATION */
    .stDeployButton {
        display: none !important;
    }
    
    /* Keep navigation visible but style the main content area */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Style the header but don't hide it completely */
    header[data-testid="stHeader"] {
        background: rgba(10, 11, 20, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Style navigation elements */
    .st-emotion-cache-1wmy9hl, .st-emotion-cache-1wmy9hl a {
        color: #ffffff !important;
    }
    
    /* Style sidebar navigation */
    .css-1d391kg, .css-1d391kg a {
        color: #ffffff !important;
    }
    
    
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667dff, #8fa4ff, #b3c6ff);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 3rem 0 4rem 0;
        letter-spacing: -0.03em;
        animation: gradient-shift 4s ease-in-out infinite alternate;
        filter: drop-shadow(0 0 20px rgba(102, 125, 255, 0.2));
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    
    .timer-container {
        display: flex;
        justify-content: center;
        margin: 3rem 0;
    }
    
    .timer-display {
        font-size: 5rem;
        font-weight: 700;
        text-align: center;
        color: #ffffff;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(25px);
        padding: 3rem 4rem;
        border-radius: 24px;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
    }
    
    .timer-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 125, 255, 0.1), transparent);
        animation: shine 4s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .status-text {
        font-size: 1.4rem;
        text-align: center;
        margin: 2rem 0;
        font-weight: 500;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.8);
        text-shadow: 0 0 15px rgba(102, 125, 255, 0.3);
    }
    
    .glassmorphism-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glassmorphism-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(102, 125, 255, 0.2);
    }
    
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        border: none !important;
        background: linear-gradient(135deg, #667dff, #8fa4ff) !important;
        color: white !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 1rem 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 8px 25px rgba(102, 125, 255, 0.25) !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 35px rgba(102, 125, 255, 0.35) !important;
        background: linear-gradient(135deg, #7a8eff, #a3b6ff) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    .phone-warning {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.8), rgba(255, 107, 122, 0.7));
        backdrop-filter: blur(25px);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 600;
        margin: 1.5rem 0;
        font-size: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 30px rgba(255, 71, 87, 0.25);
        animation: pulse-warning 2.5s infinite;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    
    @keyframes pulse-warning {
        0%, 100% { transform: scale(1); box-shadow: 0 12px 30px rgba(255, 71, 87, 0.25); }
        50% { transform: scale(1.01); box-shadow: 0 15px 35px rgba(255, 71, 87, 0.35); }
    }
    
    .stats-text {
        color: rgba(255, 255, 255, 0.9);
        text-align: left;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    
    .stats-text h3 {
        background: linear-gradient(135deg, #667dff, #8fa4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.4rem;
        font-weight:700;
        margin-bottom: 1.5rem;
        text-align: center;
        letter-spacing: -0.01em;
    }
    
    .stats-text p {
        margin: 0.8rem 0;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stats-text strong {
        color: #8fa4ff;
        font-weight: 600;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.015);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        background: rgba(255, 255, 255, 0.03);
        transform: translateY(-1px);
        border: 1px solid rgba(102, 125, 255, 0.15);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667dff, #8fa4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        margin: 3rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(25px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.015) !important;
        backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667dff, #8fa4ff);
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7a8eff, #a3b6ff);
    }
</style>
""", unsafe_allow_html=True)


if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'total_seconds' not in st.session_state:
    st.session_state.total_seconds = 0
if 'total_sesh_day' not in st.session_state:
    st.session_state.total_sesh_day = total_sesh_day
if 'total_focus_time_day' not in st.session_state:
    st.session_state.total_focus_time_day = total_focus_time_day
if 'times_phone_stopped_day' not in st.session_state:
    st.session_state.times_phone_stopped_day = times_phone_stopped_day
if 'total_sesh_week' not in st.session_state:
    st.session_state.total_sesh_week = total_sesh_week
if 'total_focus_time_week' not in st.session_state:
    st.session_state.total_focus_time_week = total_focus_time_week
if 'times_phone_stopped_week' not in st.session_state:
    st.session_state.times_phone_stopped_week = times_phone_stopped_week
if 'false_detection_window' not in st.session_state:
    st.session_state.false_detection_window = False
if 'false_detection_start_time' not in st.session_state:
    st.session_state.false_detection_start_time = None
if 'false_detected' not in st.session_state:
    st.session_state.false_detected = False
if 'paused_time' not in st.session_state:
    st.session_state.paused_time = 0
if 'pause_start_time' not in st.session_state:
    st.session_state.pause_start_time = None

if "model" not in st.session_state:
    try:
        st.session_state.model = load_model("keras_model.h5", compile=False)
    except Exception as e:
        print(f"‼️‼️‼️Could not load model: {e}‼️‼️‼️")


if 'video' not in st.session_state:
    try:
        st.session_state.video = cv2.VideoCapture(0)
    except Exception as e:
        print(f"Could not capture video: {e}")

if 'recent_confidences' not in st.session_state:
    st.session_state.recent_confidences = []



if 'phone_detected' not in st.session_state:
    st.session_state.phone_detected = False

if 'stopped_by_phone' not in st.session_state:
    st.session_state.stopped_by_phone = False

if 'phone_confidence_counter' not in st.session_state:
    st.session_state.phone_confidence_counter = 0

if 'phone_detection_threshold' not in st.session_state:
    st.session_state.phone_detection_threshold = 5


def preprocess_frame(frame):

    frame = cv2.resize(frame, (224, 224)) # standardizes the input size to 224 x 224 pixels
    

    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV) # Y (luminance), U (blue projection), and V (red projection)
    
    
    yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0]) # extracts the y channel and redistributes the brightness across the image

    frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    frame = np.asarray(frame, dtype=np.float32).reshape(1, 224, 224, 3) # 1 image, 224 pixels high, 224 pixels wide, 3 channels
    frame = (frame / 127.5) - 1

    return frame




st.markdown('<h1 class="main-title">🎯FocusAI</h1>', unsafe_allow_html=True)


if st.session_state.timer_running and st.session_state.start_time:
    if st.session_state.false_detection_window and st.session_state.pause_start_time:
       
        elapsed_seconds = int(st.session_state.pause_start_time - st.session_state.start_time - st.session_state.paused_time)
    else:
      
        current_time = time.time()
        elapsed_seconds = int(current_time - st.session_state.start_time - st.session_state.paused_time)
    st.session_state.total_seconds = elapsed_seconds
else:
    elapsed_seconds = st.session_state.total_seconds

minutes = elapsed_seconds // 60
seconds = elapsed_seconds % 60
time_display = f"{minutes:02d}:{seconds:02d}"


if st.session_state.timer_running and not st.session_state.false_detection_window:
 

    ret, frame = st.session_state.video.read()
    if not ret:
        print("Could not get the ret!")
        quit()


    frame = preprocess_frame(frame)



    prediction = st.session_state.model.predict(frame)

    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]


    st.session_state.phone_detected = False
    phone_confidence = prediction[0][0]
    nonphone_confidence = prediction[0][1]

   


    st.session_state.recent_confidences.append(phone_confidence)
    if len(st.session_state.recent_confidences) > 5: 
       st.session_state.recent_confidences.pop(0)



    avg_conf = np.mean(st.session_state.recent_confidences)
    high_conf_count = sum(conf > 0.7 for conf in st.session_state.recent_confidences)

    with st.expander("📊 Phone Detection Metrics", expanded=True):
       metric_col1, metric_col2 = st.columns(2)
       with metric_col1:
           st.markdown(f"""
           <div class="metric-container">
               <div class="metric-label">Avg Confidence</div>
               <div class="metric-value">{avg_conf:.2f}</div>
           </div>
           """, unsafe_allow_html=True)
       with metric_col2:
           st.markdown(f"""
           <div class="metric-container">
               <div class="metric-label">High Confidence</div>
               <div class="metric-value">{high_conf_count:.0f}</div>
           </div>
           """, unsafe_allow_html=True)
 
    if avg_conf > 0.4 and high_conf_count >= 2: # thresholds
           st.session_state.phone_detected = True

        



    if st.session_state.phone_detected:
        st.markdown('<div class="phone-warning">📱 FocusAI: Phone Detected!</div>', unsafe_allow_html=True)
        winsound.Beep(1000, 500)
        st.session_state.recent_confidences = []
        avg_conf = 0
        high_conf_count = 0
        st.session_state.false_detection_window = True
        st.session_state.false_detection_start_time = time.time()

        st.session_state.pause_start_time = time.time()
        st.rerun()



if st.session_state.false_detection_window:
    st.markdown('<div class="phone-warning">FALSE DETECTION? Click within 5 seconds!</div>', unsafe_allow_html=True)


    if st.button("Falsely Detected?", key="false_pos"):

        if st.session_state.pause_start_time:
            pause_duration = time.time() - st.session_state.pause_start_time
            st.session_state.paused_time += pause_duration
            st.session_state.pause_start_time = None
        
        st.session_state.false_detected = True
        st.session_state.recent_confidences = []
        st.session_state.false_detection_window = False
        st.session_state.phone_detected = False
        st.rerun()

    elapsed = time.time() - st.session_state.false_detection_start_time
    if elapsed > 5:
        if not st.session_state.false_detected:
          
            current_session_time = st.session_state.total_seconds
            st.session_state.timer_running = False
            st.session_state.total_sesh_day += 1
            st.session_state.total_sesh_week += 1
            st.session_state.times_phone_stopped_day += 1
            st.session_state.times_phone_stopped_week += 1
            st.session_state.total_focus_time_day += current_session_time
            st.session_state.total_focus_time_week += current_session_time
            st.session_state.total_seconds = 0
            st.session_state.start_time = None
            st.session_state.stopped_by_phone = True
            st.session_state.phone_confidence_counter = 0
            
        
            st.session_state.paused_time = 0
            st.session_state.pause_start_time = None

        
            st.session_state.false_detection_window = False
            st.session_state.false_detected = False
            st.session_state.phone_detected = False

            execute_db_query("""UPDATE project SET
                total_sesh_day = ?, total_focus_time_day = ?, times_phone_stopped_day = ?,
                total_sesh_week = ?, total_focus_time_week = ?, times_phone_stopped_week = ?
                WHERE username = ?""", 
                (st.session_state.total_sesh_day, st.session_state.total_focus_time_day,
                st.session_state.times_phone_stopped_day, st.session_state.total_sesh_week,
                st.session_state.total_focus_time_week, st.session_state.times_phone_stopped_week,
                username))

            today_string = datetime.now().strftime("%Y-%m-%d")
            execute_db_query("""
                INSERT INTO daily_stats (username, date, focus_time, phone_detections)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, date) DO UPDATE SET 
                    focus_time = focus_time + ?, 
                    phone_detections = phone_detections + ?
            """, (
                username, today_string,
                current_session_time, 1,
                current_session_time, 1
            ))

            st.rerun()
        else:
           
            st.session_state.false_detected = False

    
  
          

if st.session_state.stopped_by_phone:
    st.markdown('<div class="phone-warning">📱 SESSION STOPPED!</div>', unsafe_allow_html=True)
    st.session_state.stopped_by_phone = False




st.markdown(f"""
<div class="timer-container">
    <div class="timer-display">{time_display}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.timer_running:
    if st.session_state.false_detection_window:
        status = "Focus Mode Paused - Detection Active"
        status_color = "#ff6b7a"
    else:
        status = "Focus Mode Active"
        status_color = "#ff77c6"
else:
    status = "Focus Mode Inactive"
    status_color = "#7877c6"

st.markdown(f'<div class="status-text" style="color: {status_color};">{status}</div>', 
           unsafe_allow_html=True)



col1, col2, col3 = st.columns([1, 2, 1])

with col2:
  
    if not st.session_state.timer_running:
        if st.button("READY TO FOCUS?", key="start_btn"):
            st.session_state.recent_confidences = []
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
           
            st.session_state.paused_time = 0
            st.session_state.pause_start_time = None
            st.rerun()
    elif not st.session_state.false_detection_window:  
        if st.button("DONE FOR THE SESSION?", key="stop_btn"):
            current_session_time = st.session_state.total_seconds
            st.session_state.timer_running = False
            st.session_state.total_sesh_day += 1
            avg_phone = 0
            avg_nonphone = 0
            st.session_state.total_sesh_week += 1
            st.session_state.total_focus_time_day += st.session_state.total_seconds
            st.session_state.total_focus_time_week += st.session_state.total_seconds
            st.session_state.total_seconds = 0
            st.session_state.start_time = None
            # FIXED: Reset pause-related variables
            st.session_state.paused_time = 0
            st.session_state.pause_start_time = None
            st.success(f"Great job! You focused for {minutes} minutes and {seconds} seconds! ")
            execute_db_query("""UPDATE project SET
             total_sesh_day = ?,
             total_focus_time_day = ?,
             total_sesh_week = ?,
             total_focus_time_week = ?
             WHERE username = ?""", 
             (st.session_state.total_sesh_day,
              st.session_state.total_focus_time_day,
              st.session_state.total_sesh_week,
              st.session_state.total_focus_time_week,
              username))
            execute_db_query("""
    INSERT INTO daily_stats (username, date, focus_time, phone_detections)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(username, date) DO UPDATE SET 
        focus_time = focus_time + ?, 
        phone_detections = phone_detections + ?
    """, (
        username, today_string,
        current_session_time, 
        0,                     
        current_session_time,  
        0                      
    ))

            time.sleep(2)
            st.rerun()
          

            

st.markdown("---")


if st.session_state.timer_running and not st.session_state.false_detection_window:
    time.sleep(0.1)
    st.rerun()
elif st.session_state.false_detection_window:
    time.sleep(0.1)
    st.rerun()

stats_col1, stats_col2 = st.columns(2)

with stats_col1:
   if st.session_state.total_sesh_day > 0:
    avg_session = st.session_state.total_focus_time_day // st.session_state.total_sesh_day
    avg_minutes = avg_session // 60
    total_minutes = st.session_state.total_focus_time_day // 60

    st.markdown(f"""
        <div class="glassmorphism-card">
            <div class="stats-text">
                <h3 style="color: #ff4757; text-align: center;">📊 {username}'s Daily Focus Stats</h3>
                <p><strong>Total Sessions:</strong> {st.session_state.total_sesh_day}</p>
                <p><strong>Total Focus Time:</strong> {total_minutes} minutes</p>
                <p><strong>Average Session:</strong> {avg_minutes} minutes</p>
                <p><strong>Times your phone has been detected in total:</strong> {st.session_state.times_phone_stopped_day}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
   else:
        st.markdown(f"""
        <div class="glassmorphism-card">
            <div class="stats-text">
                <h3 style="color: #ff4757; text-align: center;">📊 {username}'s Daily Focus Stats</h3>
                <p>No data for today yet. Start a session!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


with stats_col2:
    if st.session_state.total_sesh_week > 0:
        avg_session_week = st.session_state.total_focus_time_week // st.session_state.total_sesh_week
        avg_minutes_week = avg_session_week // 60
        total_minutes_week = st.session_state.total_focus_time_week // 60
        
        st.markdown(f"""
        <div class="glassmorphism-card">
            <div class="stats-text">
                <h3 style="color: #ff4757; text-align: center;">📊 {username}'s Weekly Focus Stats</h3>
                <p><strong>Total Sessions:</strong> {st.session_state.total_sesh_week}</p>
                <p><strong>Total Focus Time:</strong> {total_minutes_week} minutes</p>
                <p><strong>Average Session:</strong> {avg_minutes_week} minutes</p>
                <p><strong>Times your phone has been detected in total:</strong> {st.session_state.times_phone_stopped_week}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="glassmorphism-card">
            <div class="stats-text">
                <h3 style="color: #ff4757; text-align: center;">📊 {username}'s Weekly Focus Stats</h3>
                <p>No data for this week yet. Keep focusing!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
