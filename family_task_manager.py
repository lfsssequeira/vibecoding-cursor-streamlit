import streamlit as st
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Family Task Manager",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .kanban-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        min-height: 400px;
        border: 2px solid #e9ecef;
    }
    
    .open-container {
        border-left: 5px solid #28a745;
    }
    
    .progress-container {
        border-left: 5px solid #ffc107;
    }
    
    .done-container {
        border-left: 5px solid #6c757d;
    }
    
    .column-header {
        text-align: center;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding: 0.4rem;
        border-radius: 5px;
        color: #2c3e50;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
    
    .task-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid;
    }
    
    .priority-high {
        border-left-color: #dc3545;
    }
    
    .priority-medium {
        border-left-color: #ffc107;
    }
    
    .priority-low {
        border-left-color: #28a745;
    }
    
    .task-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    
    .task-description {
        color: #6c757d;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .task-person {
        color: #2E86AB;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .task-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .footer {
        text-align: center;
        color: #6c757d;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #e9ecef;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .kanban-container {
            margin: 0.25rem;
            min-height: 300px;
        }
        
        .column-header {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Data storage functions
def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists('tasks.json'):
        try:
            with open('tasks.json', 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=2)

def get_next_id(tasks):
    """Get the next available ID for a new task"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

if 'show_form' not in st.session_state:
    st.session_state.show_form = False

if 'editing_task' not in st.session_state:
    st.session_state.editing_task = None

# Main header
st.markdown('<h1 class="main-header">👨‍👩‍👧‍👦 Family Task Manager</h1>', unsafe_allow_html=True)

# Sidebar for task creation and management
with st.sidebar:
    st.header("📋 Task Management")
    
    if st.button("➕ Add New Task", use_container_width=True):
        st.session_state.show_form = True
        st.session_state.editing_task = None
    
    # Task statistics
    if st.session_state.tasks:
        total_tasks = len(st.session_state.tasks)
        open_tasks = len([t for t in st.session_state.tasks if t['status'] == 'Open'])
        progress_tasks = len([t for t in st.session_state.tasks if t['status'] == 'In Progress'])
        done_tasks = len([t for t in st.session_state.tasks if t['status'] == 'Done'])
        
        st.subheader("📊 Task Statistics")
        st.metric("Total Tasks", total_tasks)
        st.metric("Open", open_tasks)
        st.metric("In Progress", progress_tasks)
        st.metric("Done", done_tasks)

# Task form (appears when creating or editing)
if st.session_state.show_form:
    st.subheader("📝 " + ("Edit Task" if st.session_state.editing_task else "Create New Task"))
    
    with st.form("task_form"):
        # Get current task data if editing
        current_task = None
        if st.session_state.editing_task:
            current_task = next((t for t in st.session_state.tasks if t['id'] == st.session_state.editing_task), None)
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title", value=current_task['title'] if current_task else "")
            responsible = st.text_input("Responsible Person", value=current_task['responsible'] if current_task else "")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], 
                                  index=["Low", "Medium", "High"].index(current_task['priority']) if current_task else 0)
        
        with col2:
            description = st.text_area("Description", value=current_task['description'] if current_task else "")
            status = st.selectbox("Status", ["Open", "In Progress", "Done"],
                                index=["Open", "In Progress", "Done"].index(current_task['status']) if current_task else 0)
        
        submitted = st.form_submit_button("💾 Save Task", use_container_width=True)
        
        if submitted:
            if not title.strip():
                st.error("Please enter a task title!")
            elif not responsible.strip():
                st.error("Please enter a responsible person!")
            else:
                if st.session_state.editing_task:
                    # Update existing task
                    for task in st.session_state.tasks:
                        if task['id'] == st.session_state.editing_task:
                            task.update({
                                'title': title.strip(),
                                'description': description.strip(),
                                'responsible': responsible.strip(),
                                'priority': priority,
                                'status': status
                            })
                            break
                    st.success("Task updated successfully!")
                else:
                    # Create new task
                    new_task = {
                        'id': get_next_id(st.session_state.tasks),
                        'title': title.strip(),
                        'description': description.strip(),
                        'responsible': responsible.strip(),
                        'priority': priority,
                        'status': status,
                        'created_at': datetime.now().isoformat()
                    }
                    st.session_state.tasks.append(new_task)
                    st.success("Task created successfully!")
                
                save_tasks(st.session_state.tasks)
                st.session_state.show_form = False
                st.session_state.editing_task = None
                st.rerun()
    
    if st.button("❌ Cancel", use_container_width=True):
        st.session_state.show_form = False
        st.session_state.editing_task = None
        st.rerun()

# Kanban Board
st.subheader("📋 Task Board")

if not st.session_state.tasks:
    st.info("🎉 No tasks yet! Click 'Add New Task' in the sidebar to get started.")
else:
    # Create three columns for the Kanban board using Streamlit's native columns
    col1, col2, col3 = st.columns(3)
    
    # Open Tasks Column
    with col1:
        st.markdown('<div class="kanban-container open-container">', unsafe_allow_html=True)
        st.markdown('<div class="column-header">🟢 Open Tasks</div>', unsafe_allow_html=True)
        
        open_tasks = [task for task in st.session_state.tasks if task['status'] == 'Open']
        for task in open_tasks:
            # Display task information using Streamlit components
            with st.container():
                priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.markdown(f"**{task['title']}** {priority_colors.get(task['priority'], '')}")
                st.markdown(f"*{task['description']}*")
                st.markdown(f"👤 **{task['responsible']}**")
                st.markdown(f"📊 Priority: {task['priority']}")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("➡️", key=f"move_progress_{task['id']}", help="Move to In Progress"):
                        task['status'] = 'In Progress'
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                with btn_col2:
                    if st.button("✏️", key=f"edit_{task['id']}", help="Edit Task"):
                        st.session_state.editing_task = task['id']
                        st.session_state.show_form = True
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️", key=f"delete_{task['id']}", help="Delete Task"):
                        if st.session_state.get(f"confirm_delete_{task['id']}", False):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                            save_tasks(st.session_state.tasks)
                            st.session_state[f"confirm_delete_{task['id']}"] = False
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    st.warning(f"⚠️ Delete '{task['title']}'?")
                    if st.button("✅ Confirm Delete", key=f"confirm_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                
                st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # In Progress Tasks Column
    with col2:
        st.markdown('<div class="kanban-container progress-container">', unsafe_allow_html=True)
        st.markdown('<div class="column-header">🟡 In Progress</div>', unsafe_allow_html=True)
        
        progress_tasks = [task for task in st.session_state.tasks if task['status'] == 'In Progress']
        for task in progress_tasks:
            # Display task information using Streamlit components
            with st.container():
                priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.markdown(f"**{task['title']}** {priority_colors.get(task['priority'], '')}")
                st.markdown(f"*{task['description']}*")
                st.markdown(f"👤 **{task['responsible']}**")
                st.markdown(f"📊 Priority: {task['priority']}")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("✅", key=f"move_done_{task['id']}", help="Move to Done"):
                        task['status'] = 'Done'
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                with btn_col2:
                    if st.button("✏️", key=f"edit_progress_{task['id']}", help="Edit Task"):
                        st.session_state.editing_task = task['id']
                        st.session_state.show_form = True
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️", key=f"delete_progress_{task['id']}", help="Delete Task"):
                        if st.session_state.get(f"confirm_delete_{task['id']}", False):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                            save_tasks(st.session_state.tasks)
                            st.session_state[f"confirm_delete_{task['id']}"] = False
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    st.warning(f"⚠️ Delete '{task['title']}'?")
                    if st.button("✅ Confirm Delete", key=f"confirm_progress_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_progress_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                
                st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Done Tasks Column
    with col3:
        st.markdown('<div class="kanban-container done-container">', unsafe_allow_html=True)
        st.markdown('<div class="column-header">✅ Done</div>', unsafe_allow_html=True)
        
        done_tasks = [task for task in st.session_state.tasks if task['status'] == 'Done']
        for task in done_tasks:
            # Display task information using Streamlit components
            with st.container():
                priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.markdown(f"**{task['title']}** {priority_colors.get(task['priority'], '')}")
                st.markdown(f"*{task['description']}*")
                st.markdown(f"👤 **{task['responsible']}**")
                st.markdown(f"📊 Priority: {task['priority']}")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("⬅️", key=f"move_back_{task['id']}", help="Move back to In Progress"):
                        task['status'] = 'In Progress'
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                with btn_col2:
                    if st.button("✏️", key=f"edit_done_{task['id']}", help="Edit Task"):
                        st.session_state.editing_task = task['id']
                        st.session_state.show_form = True
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️", key=f"delete_done_{task['id']}", help="Delete Task"):
                        if st.session_state.get(f"confirm_delete_{task['id']}", False):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                            save_tasks(st.session_state.tasks)
                            st.session_state[f"confirm_delete_{task['id']}"] = False
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    st.warning(f"⚠️ Delete '{task['title']}'?")
                    if st.button("✅ Confirm Delete", key=f"confirm_done_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_done_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                
                st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>👨‍👩‍👧‍👦 Family Task Manager - Keep your family organized and productive!</p>
    <p>Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
