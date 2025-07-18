import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime, timedelta


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


DEBUG_MODE = False


if DEBUG_MODE:
    st.markdown("---")
    st.markdown("### 🔍 DEBUG INFO")
    
    # Show database contents
    debug_data = execute_db_query("SELECT * FROM daily_stats WHERE username = ?", ("Student",), fetch=True)
    if debug_data:
        st.write("**Daily Stats Database Contents:**")
        df_debug = pd.DataFrame(debug_data, columns=['username', 'date', 'focus_time', 'phone_detections']) # change coloumns name to be more user friendly
        st.dataframe(df_debug)
    else:
        st.write("**Daily Stats Database is EMPTY!**")
    
    # Show project table
    project_data = execute_db_query("SELECT * FROM project WHERE username = ?", ("Student",), fetch=True)
    if project_data:
        st.write("**Project Table Contents:**")
        st.write(project_data[0])


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


# Display charts
st.markdown("---")
st.markdown("### 📊 Weekly Statistics")

df = get_week_data("Student")

# Always show charts now since we have a complete week dataframe
if not df.empty:
    # Focus time chart
    focus_chart = alt.Chart(df).mark_bar(color='#ff4757').encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%m/%d')),
        y=alt.Y('focus_time_mins:Q', title='Focus Time (minutes)'),
        tooltip=['date', 'focus_time_mins']
    ).properties(
        title='📈 Focus Time (mins) This Week',
        width=600,
        height=300
    )
    
    # Phone detections chart
    phone_chart = alt.Chart(df).mark_bar(color='#ffa502').encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%m/%d')),
        y=alt.Y('phone_detections:Q', title='Phone Detections'),
        tooltip=['date', 'phone_detections']
    ).properties(
        title='📱 Phone Detections This Week',
        width=600,
        height=300
    )
    
    st.altair_chart(focus_chart, use_container_width=True)
    st.altair_chart(phone_chart, use_container_width=True)
    
    # Show a message if no actual data exists
    if df['focus_time_mins'].sum() == 0 and df['phone_detections'].sum() == 0:
        st.info("📊 No focus session data yet. Complete some focus sessions to see your progress!")
    
    if DEBUG_MODE:
        st.write("**Chart Data:**")
        st.dataframe(df)
        
        st.write("**Week dates being queried:**")
        today = datetime.now()
        week_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        st.write(week_dates)
else:
    st.error("Error creating week dataframe")