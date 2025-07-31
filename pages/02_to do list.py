import streamlit as st
import sqlite3 



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



# --- Page Configuration ---
st.set_page_config(page_title="To Do List", page_icon="✅", layout="centered")



st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        /* General Body and Font */
        html, body, .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0f;
            background-image:
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
            min-height: 100vh;
            overflow-x: hidden; /* Prevent horizontal scroll */
            color: #ffffff; /* Default text color for the app */
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
                radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.1), transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255, 119, 198, 0.2), transparent),
                radial-gradient(1px 1px at 90px 40px, rgba(120, 119, 198, 0.3), transparent),
                radial-gradient(1px 1px at 130px 80px, rgba(255, 255, 255, 0.1), transparent);
            background-size: 200px 100px;
            animation: particle-float 20s infinite linear;
            pointer-events: none;
            z-index: -1;
        }

        @keyframes particle-float {
            0% { transform: translateY(0px) translateX(0px); }
            33% { transform: translateY(-20px) translateX(10px); }
            66% { transform: translateY(-10px) translateX(-10px); }
            100% { transform: translateY(0px) translateX(0px); }
        }

        /* Hide specific Streamlit elements, preserve navigation */
        .stDeployButton {
            display: none !important;
        }

        /* Style the main content area */
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 800px !important; /* Adjusted for better centering */
        }

        /* Style the header */
        header[data-testid="stHeader"] {
            background: rgba(10, 10, 15, 0.8) !important;
            backdrop-filter: blur(20px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Style navigation elements (if any) */
        .st-emotion-cache-1wmy9hl, .st-emotion-cache-1wmy9hl a {
            color: #ffffff !important;
        }

        /* Style sidebar navigation (if any) */
        .css-1d391kg, .css-1d391kg a {
            color: #ffffff !important;
        }

        /* Main Title Styling */
        .main-title {
            font-size: clamp(2.5rem, 8vw, 4rem); /* Responsive font size */
            font-weight: 900;
            text-align: center;
            background: linear-gradient(135deg, #ff77c6, #7877c6, #00d4ff);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 3rem 0 2rem 0;
            letter-spacing: -0.02em;
            animation: gradient-shift 3s ease-in-out infinite alternate;
            filter: drop-shadow(0 0 30px rgba(255, 119, 198, 0.3));
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }
        .clear-button {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 12px;
    background: linear-gradient(90deg, #7877c6, #ff77c6);
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(255, 119, 198, 0.3);
}

.clear-button:hover {
    background: linear-gradient(90deg, #ff77c6, #7877c6);
    box-shadow: 0 6px 18px rgba(255, 119, 198, 0.5);
    transform: translateY(-2px);
}

.clear-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(255, 119, 198, 0.2);
}


        /* Glassmorphism Card Style */
        .glassmorphism-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            margin-bottom: 1.5rem; /* Space between cards */
            box-shadow:
                0 20px 40px rgba(0, 0, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glassmorphism-card:hover {
            transform: translateY(-5px);
            box-shadow:
                0 30px 60px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        /* Streamlit Text Area Styling (target specific internal classes) */
        /* This targets the container div around the textarea */
        .stTextArea > label {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }

        .stTextArea textarea {
            width: 100%;
            min-height: 100px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05);
            color: #ffffff;
            font-size: 1rem;
            resize: vertical; /* Allow vertical resizing */
            outline: none;
            transition: border-color 0.3s ease, background-color 0.3s ease;
        }

        .stTextArea textarea::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .stTextArea textarea:focus {
            border-color: #7877c6;
            background: rgba(255, 255, 255, 0.1);
        }

        /* Streamlit Button Styling */
        .stButton > button {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 15px;
            background: linear-gradient(90deg, #ff77c6, #7877c6);
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(255, 119, 198, 0.3);
            width: auto; /* Allow button to size naturally */
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #7877c6, #ff77c6);
            box-shadow: 0 8px 20px rgba(255, 119, 198, 0.5);
            transform: translateY(-2px);
        }

        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 2px 5px rgba(255, 119, 198, 0.2);
        }

        /* To-Do Item Styling (for dynamic rendering) */
        .todo-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 0.8rem; /* Space between items */
            transition: all 0.2s ease;
        }

        .todo-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: scale(1.01);
        }

        .todo-text {
            flex-grow: 1;
            font-size: 1.1rem;
            color: #ffffff;
            word-break: break-word; /* Ensure long text wraps */
        }

        .todo-actions {
            display: flex;
            gap: 0.5rem;
            margin-left: 1rem;
        }

        .action-button {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: rgba(255, 255, 255, 0.7);
            transition: color 0.2s ease, transform 0.2s ease;
        }

        .action-button:hover {
            color: #ff77c6;
            transform: scale(1.1);
        }

        .action-button.delete:hover {
            color: #ff4d4d; /* Red for delete */
        }

        .action-button.complete:hover {
            color: #4CAF50; /* Green for complete */
        }

        .todo-item.completed .todo-text {
            text-decoration: line-through;
            color: rgba(255, 255, 255, 0.6);
        }

        /* Responsive adjustments */
        @media (max-width: 600px) {
            .main .block-container {
                padding: 1rem !important;
            }

            .main-title {
                font-size: clamp(2rem, 10vw, 3rem);
                margin-top: 2rem;
            }

            .stTextArea textarea {
                min-height: 80px;
            }

            .stButton > button {
                width: 100%; /* Full width button on small screens */
            }

            .todo-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.8rem;
                padding: 0.8rem 1rem;
            }

            .todo-actions {
                width: 100%;
                justify-content: flex-end;
                margin-left: 0;
            }
        }
        
    </style>
""", unsafe_allow_html=True)



st.markdown('<h1 class="main-title">Your Daily To-Do List</h1>', unsafe_allow_html=True)

# Input Section
with st.container():
    st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)
    user_input = st.text_area(
        "Enter a task here:",
        height=150,
        placeholder="Enter the text you want to get done today...\n\nExample: 'Complete chapter 7 maths one shot' or 'Solve NCERT exercises'",
        key="task_input_area"
    )

    # Use a column to right-align the button
    col1, col2 = st.columns([0.7, 0.3])
    with col2:
        enter_button = st.button("Add Task", key="add_task_button")
    st.markdown('</div>', unsafe_allow_html=True)



if "db_task" not in st.session_state:
    st.session_state.db_task = sqlite3.connect('todo.db')
    execute_db_query("""
CREATE TABLE IF NOT EXISTS tasks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
task TEXT,
completed INTEGER DEFAULT 0)

""")


if enter_button and user_input:
    execute_db_query("INSERT INTO tasks (task) VALUES (?)", (user_input,))
    st.rerun() # Rerun to clear input and update list

# To-Do List Display Section
with st.container():
    st.markdown('<div class="glassmorphism-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.4rem; font-weight: 600; color: #ffffff; margin-bottom: 1rem;">Your Tasks</h2>', unsafe_allow_html=True)

    # TO DO: Backend - Fetch tasks from the database
    tasks = execute_db_query("SELECT * FROM tasks", fetch=True)
    

    if len(tasks) == 0:
        st.info("You have no tasks yet! Add one above.")
    else:
        for task in tasks:
            task_class = "completed" if task[2] == 1 else "not_done"
        
            col_text, col_complete, col_delete = st.columns([0.7, 0.15, 0.15]) # Adjusted column ratios

            with col_text:
                st.markdown(f'<div class="todo-item {task_class}"><span class="todo-text">{task[1]}</span></div>', unsafe_allow_html=True)

            with col_complete:
                # TO DO: Backend - Handle task completion/uncompletion
                if st.button("✅", key=f"complete_{task[0]}", help="Mark as Complete"):
                    execute_db_query("UPDATE tasks SET completed = 1 WHERE id = ?", (task[0],))
                    st.rerun()

            with col_delete:

                # TO DO: Backend - Handle task deletion
                if st.button("🗑️", key=f"delete_{task[0]}", help="Delete Task"):
                    execute_db_query("DELETE FROM tasks WHERE id = ?", (task[0],))
            
                    st.rerun()
    clear_completed = st.button("🧹 Clear Completed Tasks", key="clear_completed")
    if clear_completed:
            execute_db_query("DELETE FROM tasks WHERE completed = 1")
         
            st.rerun()



    st.markdown('</div>', unsafe_allow_html=True)





