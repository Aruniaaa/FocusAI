import os
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"
import streamlit as st
import time
import datetime
import cv2
import sqlite3
import winsound
from keras.models import load_model  
import cv2  
import numpy as np
import tensorflow.python

# keras_model1 seems to work, try it in a different environment and if it is accurate even there, lower the threshold


np.set_printoptions(suppress=True)



# Load the labels
class_names = open("labels.txt", "r").readlines()
 




today = datetime.datetime.now()
today_string = today.strftime("%Y-%m-%d")
day = today - datetime.timedelta(days=today.weekday())
day_string = day.strftime("%Y-%m-%d")

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
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #ff4757;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(255, 71, 87, 0.3);
    }
    
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        color: #ffffff;
        background: linear-gradient(145deg, #2c2c2c, #3a3a3a);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 2px solid #ff4757;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .status-text {
        font-size: 1.5rem;
        text-align: center;
        color: #ff6b7a;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }
            
    .phone-warning {
    background: linear-gradient(145deg, #ff4757, #ff3742);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    margin: 1rem 0;
    font-size: 1.2rem;
    }
    
    .start-button {
        background: linear-gradient(145deg, #ff4757, #ff3742);
        color: white;
    }
    
    .stop-button {
        background: linear-gradient(145deg, #747d8c, #57606f);
        color: white;
    }
    
    .stats-container {
        background: linear-gradient(145deg, #2c2c2c, #3a3a3a);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 1px solid #ff4757;
    }
    
    .stats-text {
        color: #ffffff;
        text-align: center;
        font-size: 1.1rem;
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

if 'model' not in st.session_state:
    try:
        st.session_state.model = load_model("keras_model.h5", compile=False)
    except Exception as e:
        print(f"Could not load model: {e}")


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

    frame = cv2.resize(frame, (224, 224))
    

    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    
    
    yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])

    frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    frame = np.asarray(frame, dtype=np.float32).reshape(1, 224, 224, 3)
    frame = (frame / 127.5) - 1

    return frame




st.markdown('<h1 class="main-title">🎯 Focus Timer</h1>', unsafe_allow_html=True)


if st.session_state.timer_running and st.session_state.start_time:
    if st.session_state.false_detection_window and st.session_state.pause_start_time:
       
        elapsed_seconds = int(st.session_state.pause_start_time - st.session_state.start_time - st.session_state.paused_time)
    else:
      
        current_time = time.time()
        elapsed_seconds = int(current_time - st.session_state.start_time - st.session_state.paused_time)
    st.session_state.total_seconds = elapsed_seconds
else:
    elapsed_seconds = st.session_state.total_seconds


if st.session_state.timer_running and not st.session_state.false_detection_window and st.session_state.model is not None and st.session_state.video is not None:
 

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


        
    st.session_state.recent_confidences.append(phone_confidence)
    if len(st.session_state.recent_confidences) > 5:
        st.session_state.recent_confidences.pop(0)

    avg_conf = np.mean(st.session_state.recent_confidences)
    high_conf_count = sum(conf > 0.7 for conf in st.session_state.recent_confidences)
    with st.expander("📊 Phone Detection Metrics", expanded=True):
       metric_col1, metric_col2 = st.columns(2)
       with metric_col1:
           st.metric("Avg Confidence", f"{avg_conf:.2f}")
       with metric_col2:
           st.metric("High Confidence", f"{high_conf_count:.0f}")
 
       if avg_conf > 0.7 and high_conf_count >= 2: # thresholds
           st.session_state.phone_detected = True



    if st.session_state.phone_detected:
        st.markdown('<div class="phone-warning">📱 Phone detected!</div>', unsafe_allow_html=True)
        winsound.Beep(1000, 500)
        st.session_state.recent_confidences = []
        avg_conf = 0
        high_conf_count = 0
        st.session_state.false_detection_window = True
        st.session_state.false_detection_start_time = time.time()

        st.session_state.pause_start_time = time.time()
        st.rerun()


if st.session_state.false_detection_window:
    st.markdown('<div class="phone-warning">⏳ False Detection? Click within 5 seconds!</div>', unsafe_allow_html=True)

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

            today_string = datetime.datetime.now().strftime("%Y-%m-%d")
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
    st.markdown('<div class="phone-warning">📱 Timer stopped - Phone detected!</div>', unsafe_allow_html=True)
    st.session_state.stopped_by_phone = False



minutes = elapsed_seconds // 60
seconds = elapsed_seconds % 60
time_display = f"{minutes:02d}:{seconds:02d}"

st.markdown(f'<div class="timer-display">{time_display}</div>', unsafe_allow_html=True)


if st.session_state.timer_running:
    if st.session_state.false_detection_window:
        status = "Focus Mode Paused - Phone Detection"
        status_color = "#ff6b7a"
    else:
        status = "Focus Mode Active"
        status_color = "#ff4757"
else:
    status = "Focus Mode Inactive"
    status_color = "#747d8c"

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
    time.sleep(0.2)
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
    
    st.markdown("""
    <div class="stats-container">
        <div class="stats-text">
            <h3 style="color: #ff4757; text-align: center;">📊 {}'s Daily Focus Stats</h3>
            <p><strong>Total Sessions:</strong> {}</p>
            <p><strong>Total Focus Time:</strong> {} minutes</p>
            <p><strong>Average Session:</strong> {} minutes</p>
            <p><strong>Times your phone has been detected in total:</strong> {}</p>
        </div>
    </div>
    """.format(username, st.session_state.total_sesh_day, total_minutes, avg_minutes, st.session_state.times_phone_stopped_day), 
    unsafe_allow_html=True)


with stats_col2:
   if st.session_state.total_sesh_week > 0:
    avg_session = st.session_state.total_focus_time_week // st.session_state.total_sesh_week
    avg_minutes = avg_session // 60
    total_minutes = st.session_state.total_focus_time_week // 60
    
    st.markdown("""
    <div class="stats-container">
        <div class="stats-text">
            <h3 style="color: #ff4757; text-align: center;">📊 {}'s Weekly Focus Stats</h3>
            <p><strong>Total Sessions:</strong> {}</p>
            <p><strong>Total Focus Time:</strong> {} minutes</p>
            <p><strong>Average Session:</strong> {} minutes</p>
            <p><strong>Times your phone has been detected in total:</strong> {}</p>
        </div>
    </div>
    """.format(username, st.session_state.total_sesh_week, total_minutes, avg_minutes, st.session_state.times_phone_stopped_week), 
    unsafe_allow_html=True)