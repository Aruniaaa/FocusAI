import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import numpy as np


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



# Apply the common CSS styling
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
        overflow: auto; /* Changed to auto to allow scrolling for charts */
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
        margin: 1.5rem auto; /* Center the card */
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 800px; /* Limit width for better chart appearance */
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

    /* Altair chart styling */
    .st-emotion-cache-1r6dm1x { /* This targets the Altair chart container */
        background: rgba(255, 255, 255, 0.015);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.04);
        box-shadow: none !important; /* Remove default chart shadow */
    }
    .st-emotion-cache-1r6dm1x .st-emotion-cache-1r6dm1x { /* Nested containers */
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)



st.markdown('<h1 class="main-title"> FocusAI Stats</h1>', unsafe_allow_html=True)




def get_week_data(username): 
    today = datetime.now()
    week_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    
    # Create a complete week dataframe with all dates
    complete_week_df = pd.DataFrame({
        'date': week_dates,
        'focus_time': [0] * 7,  # Default to 0
        'phone_detections': [0] * 7,  # Default to 0
        'focus_time_mins': [0.0] * 7  # Default to 0.0
    })

    
    # Fetch actual data from database
    conn = sqlite3.connect('project.db')
    actual_data = pd.read_sql_query("""
        SELECT date, focus_time, phone_detections 
        FROM daily_stats 
        WHERE username = ? AND date IN ({})
        ORDER BY date
    """.format(','.join(['?']*len(week_dates))), conn, params=[username] + week_dates)
    conn.close()

    
    # If we have actual data, merge it with the complete week
    if not actual_data.empty:
        actual_data['focus_time_mins'] = actual_data['focus_time'] / 60  # Convert to minutes
        
        # Update the complete week dataframe with actual data
        for _, row in actual_data.iterrows():
            mask = complete_week_df['date'] == row['date']
            complete_week_df.loc[mask, 'focus_time'] = row['focus_time']
            complete_week_df.loc[mask, 'phone_detections'] = row['phone_detections']
            complete_week_df.loc[mask, 'focus_time_mins'] = row['focus_time_mins']
    
    return complete_week_df


def get_week_data(username): 
    today = datetime.now()
    week_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    
    # Create a complete week dataframe with all dates
    complete_week_df = pd.DataFrame({
        'date': week_dates,
        'phone_detections': [0] * 7,  # Default to 0
        'focus_time_mins': [0.0] * 7  # Default to 0.0
    })



    fake_data = np.array([
    ['2025-08-03', 25.0, 2],
    ['2025-08-04', 120.0, 1],
    ['2025-08-05', 240.0, 2],
    ['2025-08-06', 50.0, 1],
    ['2025-08-07', 45.0, 1],
    ['2025-08-08', 120.0, 3],
    ['2025-08-09', 60.0, 4]
])
    actual_data = pd.DataFrame(fake_data, columns=['date', 'focus_time_mins', 'phone_detections'])
    actual_data['phone_detections'] = actual_data['phone_detections'].astype(int)
    actual_data['focus_time_mins'] = actual_data['focus_time_mins'].astype(float)

    
    # If we have actual data, merge it with the complete week
    if not actual_data.empty:
        # actual_data['focus_time_mins'] = actual_data['focus_time_mins'] * 1.0  # Convert to minutes
        
        # Update the complete week dataframe with actual data
        for _, row in actual_data.iterrows():
            mask = complete_week_df['date'] == row['date']
            complete_week_df.loc[mask, 'phone_detections'] = row['phone_detections']
            complete_week_df.loc[mask, 'focus_time_mins'] = row['focus_time_mins']
    
    return complete_week_df



# Display charts
st.markdown("---")
st.markdown("###  Weekly Statistics")

df = get_week_data("Student")

# Always show charts now since we have a complete week dataframe
if not df.empty:
    with st.container(): # Use a container to apply glassmorphism card styling
        st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)
        # Focus time chart
        focus_chart = alt.Chart(df).mark_bar(color='#ff77c6').encode( # Changed color to match theme
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%m/%d', tickCount=8)),
            y=alt.Y('focus_time_mins:Q', title='Focus Time (minutes)'),
            tooltip=['date', 'focus_time_mins']
        ).properties(
            title=' Focus Time (mins) This Week',
            width=600,
            height=300,
            background='transparent'
        ).configure_axis(
            labelColor='#ffffff',
            titleColor='#ffffff'
        ).configure_header(
            titleColor='#ffffff',
            labelColor='#ffffff'
        ).configure_title(
            color='#ffffff'
        )
        
        # Phone detections chart
        phone_chart = alt.Chart(df).mark_bar(color='#7877c6').encode( # Changed color to match theme
            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%m/%d', tickCount=8)),
            y=alt.Y('phone_detections:Q', title='Phone Detections'),
            tooltip=['date', 'phone_detections']
        ).properties(
            title='Phone Detections This Week',
            width=600,
            height=300,
            background='transparent'
        ).configure_axis(
            labelColor='#ffffff',
            titleColor='#ffffff'
        ).configure_header(
            titleColor='#ffffff',
            labelColor='#ffffff'
        ).configure_title(
            color='#ffffff'
        )
        
        st.altair_chart(focus_chart, use_container_width=True)
        st.altair_chart(phone_chart, use_container_width=True)
        
        # Show a message if no actual data exists
        if df['focus_time_mins'].sum() == 0 and df['phone_detections'].sum() == 0:
            st.info("📊 No focus session data yet. Complete some focus sessions to see your progress!")
        

else:
    st.error("Error creating week dataframe")



if not df.empty:
    st.markdown("---")
    st.markdown("### 📈 Best and Worst Days")
    
    st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)

    df['total_engagement'] = df['focus_time_mins'] + df['phone_detections'] * 2  # weighted value

    best_day = df.loc[df['total_engagement'].idxmax()]
    worst_day = df.loc[df['total_engagement'].idxmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="🌟 Best Day",
            value=best_day['date'],
            delta=f"Focus: {int(best_day['focus_time_mins'])} mins | Phone: {int(best_day['phone_detections'])}"
        )
    with col2:
        st.metric(
            label="💤 Worst Day",
            value=worst_day['date'],
            delta=f"Focus: {int(worst_day['focus_time_mins'])} mins | Phone: {int(worst_day['phone_detections'])}"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# Add Overall Stats Summary Card
st.markdown("---")
st.markdown("### 📊 Summary Statistics")

st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)

avg_focus = df['focus_time_mins'].mean()
max_focus = df['focus_time_mins'].max()
total_focus = df['focus_time_mins'].sum()

avg_phone = df['phone_detections'].mean()
max_phone = df['phone_detections'].max()
total_phone = df['phone_detections'].sum()

col3, col4 = st.columns(2)
with col3:
    st.metric("📌 Average Focus Time", f"{avg_focus:.1f} mins")
    st.metric("🔋 Max Focus in a Day", f"{max_focus:.1f} mins")
    st.metric("⏱️ Total Focus This Week", f"{total_focus:.1f} mins")

with col4:
    st.metric("📱 Avg. Phone Detections", f"{avg_phone:.1f}")
    st.metric("🚨 Max Detections in a Day", f"{max_phone}")
    st.metric("📵 Total Phone Detections", f"{total_phone}")

st.markdown('</div>', unsafe_allow_html=True)

# Optional: Add Pie chart for engagement ratio
st.markdown("---")
st.markdown("### Focus vs Distraction Ratio")

st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)

pie_df = pd.DataFrame({
    'Activity': ['Focus Time (mins)', 'Phone Detections (count)'],
    'Amount': [total_focus, total_phone * 2]  # Multiply phone detections for impact weighting
})

pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=50).encode(
    theta=alt.Theta(field="Amount", type="quantitative"),
    color=alt.Color(field="Activity", type="nominal",
                   scale=alt.Scale(range=['#ff77c6', '#7877c6'])),
    tooltip=['Activity', 'Amount']
).properties(
    width=400,
    height=300,
    background='transparent'
).configure_legend(
    labelColor='#ffffff',
    titleColor='#ffffff'
).configure_title(color='#ffffff')

st.altair_chart(pie_chart, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

