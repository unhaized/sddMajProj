import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from firebase_config import auth, db  # Custom module for Firebase configuration
import matplotlib.pyplot as plt
import time
from plyer import notification
from PIL import Image
import base64

# Setting up the page configuration for the Streamlit app
st.set_page_config(page_title="SavvyStudy", layout="wide")

# Load the image and convert it to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_base64(file_path):
    img_format = "data:image/png;base64,"
    img_data = get_base64_of_bin_file(file_path)
    return img_format + img_data

logo_base64 = get_img_with_base64(\img\ssImg.png")

# CSS to position the image in the top right corner
st.markdown(
    f"""
    <style>
    .logo-container {{
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
    }}
    </style>
    <div class="logo-container">
        <img src="{logo_base64}" alt="logo" width="100">
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'reminders' not in st.session_state:
    st.session_state.reminders = []

# Homepage overview
def homepage():
    st.title("Welcome to Study Planner")
    st.markdown("""
        ## Your Personal Study Management Tool
        - **Add and manage tasks**: Keep track of your assignments, study sessions, and exams.
        - **Set reminders**: Never miss a deadline with timely reminders.
        - **Track progress**: Monitor your completed and pending tasks.
        - **Customize study plans**: Set your study session duration and break intervals.
        - **Visualize schedule**: View your tasks in a calendar format.
    """)
    st.markdown("Please log in or sign up to get started.")
    
    # Add user guide download link
    with open("userGuide.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()
        st.download_button(label="Download User Guide", data=PDFbyte, file_name="userGuide.pdf", mime='application/octet-stream')

if not st.session_state.logged_in:
    homepage()


# Initializing session state variables to store user data and app states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'reminders' not in st.session_state:
    st.session_state.reminders = []


# Function to handle user login
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)  # Authenticate with Firebase
        st.session_state.logged_in = True
        st.session_state.user = user
        load_user_data()  # Load user data from Firebase
        st.experimental_rerun()  # Re-run the app after login
    except Exception as e:
        st.error(f"Login failed: {e}")  # Display error message if login fails

# Function to handle user sign-up
def sign_up(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)  # Create a new user in Firebase
        st.session_state.logged_in = True
        st.session_state.user = user
        db.child("users").child(user['localId']).set({"tasks": [], "reminders": []})  # Initialize user data in Firebase
        load_user_data()  # Load user data
        st.experimental_rerun()  # Re-run the app after sign-up
    except Exception as e:
        st.error(f"Sign-up failed: {e}")  # Display error message if sign-up fails

# Function to load user data from Firebase
def load_user_data():
    if st.session_state.logged_in and st.session_state.user:
        user_id = st.session_state.user['localId']
        tasks = db.child("users").child(user_id).child("tasks").get().val()  # Fetch tasks from Firebase
        reminders = db.child("users").child(user_id).child("reminders").get().val()  # Fetch reminders from Firebase

        # Convert strings back to date and time objects
        st.session_state.tasks = [
            {
                "name": task["name"],
                "type": task["type"],
                "due_date": datetime.strptime(task["due_date"], '%Y-%m-%d').date(),
                "due_time": datetime.strptime(task["due_time"], '%H:%M:%S').time(),
                "completed": task["completed"]
            }
            for task in tasks
        ] if tasks else []

        st.session_state.reminders = [
            {
                "task": reminder["task"],
                "reminder_date": datetime.strptime(reminder["reminder_date"], '%Y-%m-%d').date(),
                "reminder_time": datetime.strptime(reminder["reminder_time"], '%H:%M:%S').time()
            }
            for reminder in reminders
        ] if reminders else []
    else:
        st.error("You must be logged in to load user data.")



# Function to send notification
def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds
    )



# Function to handle countdown timer for study sessions
def countdown_timer(duration_hours, break_interval_minutes):
    total_seconds = duration_hours * 3600 + break_interval_minutes * 60

    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
        st.session_state.remaining_seconds = total_seconds
        st.session_state.timer_running = False

    if st.button("Start"):
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()

    if st.button("Stop"):
        st.session_state.timer_running = False

    if st.session_state.timer_running:
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.remaining_seconds = max(total_seconds - elapsed_time, 0)

    return st.session_state.remaining_seconds, st.session_state.timer_running



# Function to save user data to Firebase
def save_user_data():
    if st.session_state.logged_in and st.session_state.user:
        user_id = st.session_state.user['localId']
        
        # Convert date and time objects to strings
        tasks = [
            {
                "name": task["name"],
                "type": task["type"],
                "due_date": task["due_date"].strftime('%Y-%m-%d'),
                "due_time": task["due_time"].strftime('%H:%M:%S'),
                "completed": task["completed"]
            }
            for task in st.session_state.tasks
        ]
        
        reminders = [
            {
                "task": reminder["task"],
                "reminder_date": reminder["reminder_date"].strftime('%Y-%m-%d'),
                "reminder_time": reminder["reminder_time"].strftime('%H:%M:%S')
            }
            for reminder in st.session_state.reminders
        ]
        
        db.child("users").child(user_id).child("tasks").set(tasks)
        db.child("users").child(user_id).child("reminders").set(reminders)
    else:
        st.error("You must be logged in to save user data.")



# Check for reminders and send notifications
def check_reminders():
    current_time = datetime.now()
    for reminder in st.session_state.reminders:
        reminder_datetime = datetime.combine(reminder["reminder_date"], reminder["reminder_time"])
        if current_time >= reminder_datetime:
            send_notification("Reminder", f"Time to work on: {reminder['task']}")
            st.session_state.reminders.remove(reminder)
            save_user_data()
            st.experimental_rerun()

if st.session_state.logged_in:
    check_reminders()



# Authentication form for login and signup
if not st.session_state.logged_in:
    st.title("Study Planner")

    option = st.selectbox("Login or Signup", ["Login", "Signup"])

    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Submit")

        if submit:
            if option == "Login":
                login(email, password)
            elif option == "Signup":
                sign_up(email, password)
else:
    st.title(f"Welcome, {st.session_state.user['email']}")



    # Tabbed navigation for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add Task", "Your Tasks", "Set Reminders", "Progress Tracker", "Customize Plans"])

    with tab1:
        st.header("Add New Task")
        with st.form("task_form"):
            task_name = st.text_input("Task Name")
            task_type = st.selectbox("Task Type", ["Assignment", "Study Session", "Exam"])
            due_date = st.date_input("Due Date")
            due_time = st.time_input("Due Time")
            submit = st.form_submit_button("Add Task")

            if submit:
                st.session_state.tasks.append({
                    "name": task_name,
                    "type": task_type,
                    "due_date": due_date,
                    "due_time": due_time,
                    "completed": False
                })
                save_user_data()
                st.experimental_rerun()  # Re-run the app after adding a task
                st.success(f"Task '{task_name}' added successfully!")

    with tab2:
        st.header("Your Tasks")
        tasks_df = pd.DataFrame(st.session_state.tasks)

        for index, task in tasks_df.iterrows():
            task_col, actions_col = st.columns([4, 1])  # Divide the row into a 4:1 ratio

            with task_col:
                st.write(f"**{task['name']}** - {task['type']} on {task['due_date']} at {task['due_time']}")

            with actions_col:
                if not task["completed"]:
                    if st.button(f"Mark as Complete##{index}", key=f"complete_{index}"):
                        st.session_state.tasks[index]["completed"] = True
                        save_user_data()
                        st.experimental_rerun()  # Re-run the app after marking a task as complete

                # Add a spacer between buttons if the 'Mark as Complete' button is displayed
                if not task["completed"]:
                    st.write("")  # Blank space for alignment

                if st.button(f"Delete##{index}", key=f"delete_{index}"):
                    st.session_state.tasks.pop(index)
                    save_user_data()
                    st.experimental_rerun()  # Re-run the app after deleting a task

                st.write("")  # Blank space for alignment

    if all(task["completed"] for task in st.session_state.tasks):
        st.info("All tasks are completed!")

    with tab3:
        st.header("Set Reminders")
        with st.form("reminder_form"):
            reminder_task = st.selectbox("Task", [task['name'] for task in st.session_state.tasks])
            reminder_date = st.date_input("Reminder Date")
            reminder_time = st.time_input("Reminder Time")
            set_reminder = st.form_submit_button("Set Reminder")

            if set_reminder:
                st.session_state.reminders.append({
                    "task": reminder_task,
                    "reminder_date": reminder_date,
                    "reminder_time": reminder_time
                })
                save_user_data()
                st.experimental_rerun()  # Re-run the app after setting a reminder
                st.success(f"Reminder for '{reminder_task}' set successfully!")

    with tab4:
        st.header("Progress Tracker")

        completed_tasks = [task for task in st.session_state.tasks if task["completed"]]
        pending_tasks = [task for task in st.session_state.tasks if not task["completed"]]

        # Custom HTML for better visibility
        st.markdown(f"""
            <p style='color:green; font-size:24px; font-weight:bold;'>
                Completed Tasks: {len(completed_tasks)}
            </p>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <p style='color:red; font-size:24px; font-weight:bold;'>
                Pending Tasks: {len(pending_tasks)}
            </p>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            if completed_tasks:
                st.subheader("Completed Tasks")
                for task in completed_tasks:
                    st.write(f"**{task['name']}** - {task['type']} on {task['due_date']} at {task['due_time']}")
            else:
                st.subheader("Completed Tasks")
                st.write("No complete tasks")
        
        with col2:
            if pending_tasks:
                st.subheader("Pending Tasks")
                for task in pending_tasks:
                    st.write(f"**{task['name']}** - {task['type']} on {task['due_date']} at {task['due_time']}")
            else:
                st.subheader("Pending Tasks")
                st.write("No pending tasks")
        
        # Convert task data to DataFrame for table display
        task_data = {
            "Task Name": [task['name'] for task in st.session_state.tasks],
            "Task Type": [task['type'] for task in st.session_state.tasks],
            "Due Date": [task['due_date'] for task in st.session_state.tasks],
            "Due Time": [task['due_time'] for task in st.session_state.tasks],
            "Completed": [task['completed'] for task in st.session_state.tasks]
        }
        tasks_df = pd.DataFrame(task_data)
        
        # Display task data in a table with color coding for completion
        st.subheader("Tasks Table")

        # Apply background color to the 'Completed' column
        def apply_style(row):
            return ['background-color: lightgreen' if row['Completed'] else '' for _ in row]

        styled_df = tasks_df.style.apply(apply_style, axis=1)
        st.dataframe(styled_df)

    with tab5:
        st.header("Customize Study Plans")
        default_study_duration = st.slider("Default Study Session Duration (hours)", 1, 4, 2)
        study_break_interval = st.slider("Study Break Interval (minutes)", 30, 120, 60)

        st.write(f"Your default study session duration is {default_study_duration} hours.")
        st.write(f"You will take a break every {study_break_interval} minutes during study sessions.")

        st.header("Countdown Timer")
        remaining_seconds, timer_running = countdown_timer(default_study_duration, study_break_interval)

        if timer_running:
            st.write("Time remaining:", remaining_seconds)
        else:
            st.write("Timer stopped.")
