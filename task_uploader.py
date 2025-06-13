# task_uploader.py

import streamlit as st
import json
import os
import subprocess
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

TASKS_FILE = "tasks_queue/tasks.json"


# --- Functions ---

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    else:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def is_duplicate_task(tasks, new_task):
    for task in tasks:
        if (
            task.get("agent") == new_task.get("agent") and
            task.get("description") == new_task.get("description") and
            task.get("output_file") == new_task.get("output_file") and
            task.get("input_file") == new_task.get("input_file")
        ):
            return True
    return False

def mark_all_incomplete(tasks):
    for task in tasks:
        task["completed"] = False
    save_tasks(tasks)

def clear_all_tasks():
    save_tasks([])

def delete_task(tasks, index):
    tasks.pop(index)
    save_tasks(tasks)

# --- UI ---

st.set_page_config(page_title="AI Agent Pipeline Task Manager", layout="wide")

count = st_autorefresh(interval = 3000, limit = None, key = "refreshcounter")
st.title("🤖 AI Agent Pipeline - Task Manager UI")

# Load tasks
tasks = load_tasks()

# --- View Existing Tasks ---
st.header("📋 Existing Tasks")

if tasks:
    for idx, task in enumerate(tasks):
        col1, col2 = st.columns([6,1])
        with col1:
            st.markdown(f"**Task {idx+1}:** `{task['agent']}` - _{task['description']}_ - Completed: `{task['completed']}`")
        with col2:
            if st.button("❌ Delete", key=f"delete_{idx}"):
                delete_task(tasks, idx)
                st.experimental_rerun()
else:
    st.info("No tasks found in tasks.json.")

# --- Add New Task ---
st.header("➕ Add New Task")

with st.form("add_task_form"):
    agent = st.selectbox("Agent", ["Code Architect Agent", "Coding Agent", "Testing Agent", "Refactoring Agent", "Documentation Agent"])
    description = st.text_area("Description", height=100)
    output_file = st.text_input("Output file (optional)")
    input_file = st.text_input("Input file (optional)")
    completed = st.checkbox("Completed", value=False)

    prevent_duplicates = st.checkbox("Prevent duplicate tasks", value=True)

    submitted = st.form_submit_button("Add Task")

    if submitted:
        new_task = {
            "agent": agent,
            "description": description,
            "completed": completed
        }
        if output_file:
            new_task["output_file"] = output_file
        if input_file:
            new_task["input_file"] = input_file

        if prevent_duplicates and is_duplicate_task(tasks, new_task):
            st.warning("⚠️ Duplicate task detected. Task was not added.")
        else:
            tasks.append(new_task)
            save_tasks(tasks)
            st.success("✅ Task added successfully!")

# --- Pipeline Controls ---
st.header("🚀 Pipeline Control")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Run Pipeline"):
        st.info("Running pipeline... (check terminal output)")
        subprocess.Popen(["python", "-m", "src.main"])
        st.success(f"Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    if st.button("📝 Mark All Incomplete"):
        mark_all_incomplete(tasks)
        st.success("✅ All tasks marked as incomplete.")

with col3:
    if st.button("🗑️ Clear All Tasks"):
        clear_all_tasks()
        st.success("✅ All tasks cleared.")

# --- Footer ---
st.markdown("---")
st.caption("AI Agent Pipeline Task Manager UI - Powered by Streamlit 🚀")
