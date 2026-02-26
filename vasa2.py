import streamlit as st
import json
import os

st.set_page_config(page_title="Check List", page_icon="✓")

DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

st.title("✓ Check List - מעקב משימות")

col1, col2 = st.columns([4, 1])
with col1:
    new_task = st.text_input("הוסף משימה חדשה:")
with col2:
    if st.button("➕ הוסף"):
        if new_task.strip():
            st.session_state.tasks.append({"text": new_task, "status": 0})
            save_tasks(st.session_state.tasks)
            st.rerun()

st.divider()

if st.session_state.tasks:
    completed = sum(1 for t in st.session_state.tasks if t["status"] == 2)
    progress = int((completed / len(st.session_state.tasks)) * 100) if st.session_state.tasks else 0
    
    st.write(f"### 📊 אחוז ביצוע: {progress}%")
    st.progress(progress / 100)
    
    st.divider()
    st.write("### 📋 המשימות שלך:")
    
    for idx, task in enumerate(st.session_state.tasks):
        col1, col2, col3 = st.columns([0.5, 3, 1])
        
        with col1:
            colors = ["🔴", "🟡", "🟢"]
            if st.button(colors[task["status"]], key=f"btn_{idx}"):
                st.session_state.tasks[idx]["status"] = (task["status"] + 1) % 3
                save_tasks(st.session_state.tasks)
                st.rerun()
        
        with col2:
            status_text = ["❌ לא התחלתי", "⏳ בתהליך", "✅ הושלם"][task["status"]]
            st.write(f"**{task['text']}** - {status_text}")
        
        with col3:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.tasks.pop(idx)
                save_tasks(st.session_state.tasks)
                st.rerun()
        
        st.divider()
else:
    st.info("📭 אין משימות. התחל בהוספת משימה!")
