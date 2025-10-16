import streamlit as st
import json
import os
from datetime import datetime
from streamlit_kanban_board_goviceversa import kanban_board

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
        color: white;
        font-size: 3rem;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '👨‍👩‍👧‍👦 🏠 📋';
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 2rem;
        opacity: 0.7;
    }
    
    .main-header::after {
        content: '✨';
        position: absolute;
        top: 10px;
        left: 20px;
        font-size: 2rem;
        opacity: 0.7;
    }
    
    .filter-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
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
            padding: 1.5rem;
        }
        
        .main-header::before,
        .main-header::after {
            font-size: 1.5rem;
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
                tasks = json.load(f)
                if tasks and len(tasks) > 0:  # If file exists and has tasks, return them
                    return tasks
        except:
            pass
    
    # If no file or empty file, return example family tasks
    return get_example_family_tasks()

def get_example_family_tasks():
    """Get example family tasks for demonstration"""
    return [
        {
            "id": 1,
            "title": "Plan weekend family picnic",
            "description": "Research parks, pack snacks, and organize outdoor games",
            "responsible": "Mom",
            "priority": "High",
            "status": "In Progress",
            "created_at": "2025-01-15T10:00:00"
        },
        {
            "id": 2,
            "title": "Organize kids' toy room",
            "description": "Sort toys, donate unused items, and create storage system",
            "responsible": "Dad",
            "priority": "Medium",
            "status": "In Progress",
            "created_at": "2025-01-14T15:30:00"
        },
        {
            "id": 3,
            "title": "Grocery shopping for the week",
            "description": "Buy ingredients for family meals and snacks",
            "responsible": "Mom",
            "priority": "High",
            "status": "Done",
            "created_at": "2025-01-13T09:00:00"
        },
        {
            "id": 4,
            "title": "Family movie night setup",
            "description": "Choose movie, prepare popcorn, and arrange cozy seating",
            "responsible": "Kids",
            "priority": "Low",
            "status": "Done",
            "created_at": "2025-01-12T19:00:00"
        },
        {
            "id": 5,
            "title": "Clean and organize garage",
            "description": "Sort tools, organize storage, and create workspace",
            "responsible": "Dad",
            "priority": "Medium",
            "status": "Done",
            "created_at": "2025-01-11T14:00:00"
        },
        {
            "id": 6,
            "title": "Prepare family photo album",
            "description": "Print photos from last vacation and organize in album",
            "responsible": "Mom",
            "priority": "Low",
            "status": "Done",
            "created_at": "2025-01-10T16:45:00"
        }
    ]

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=2)

def get_next_id(tasks):
    """Get the next available ID for a new task"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

def filter_tasks(tasks, stage_filter, priority_filter, responsible_filter):
    """Filter tasks based on the selected criteria"""
    filtered_tasks = tasks.copy()
    
    if stage_filter != "All":
        filtered_tasks = [task for task in filtered_tasks if task['status'] == stage_filter]
    
    if priority_filter != "All":
        filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority_filter]
    
    if responsible_filter != "All":
        filtered_tasks = [task for task in filtered_tasks if task['responsible'] == responsible_filter]
    
    return filtered_tasks

def convert_tasks_to_kanban_format(tasks):
    """Convert tasks to the format required by streamlit-kanban-board-goviceversa"""
    kanban_deals = []
    
    for task in tasks:
        # Create a rich title with priority indicator
        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        title_with_priority = f"{task['title']} {priority_emoji.get(task['priority'], '')}"
        
        # Map status to stage names
        status_to_stage = {
            "Open": "To Do",
            "In Progress": "In Progress", 
            "Done": "Done"
        }
        
        # Create custom HTML content for rich task display
        custom_html = f"""
        <div style="padding: 10px; background: white; border-radius: 8px; margin: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{task['title']} {priority_emoji.get(task['priority'], '')}</h4>
            <p style="margin: 0 0 8px 0; color: #6c757d; font-style: italic;">{task['description']}</p>
            <p style="margin: 0; color: #2E86AB; font-weight: 500;">👤 {task['responsible']}</p>
            <small style="color: #6c757d;">Priority: {task['priority']}</small>
        </div>
        """
        
        kanban_deals.append({
            "id": str(task['id']),
            "stage": status_to_stage.get(task['status'], "To Do"),
            "deal_id": f"TASK-{task['id']}",  # Required: Display ID for the task
            "company_name": task['responsible'],  # Required: Name associated with the task
            "product_type": task['priority'],  # Optional: Category or type of task
            "date": task.get('created_at', '').split('T')[0] if task.get('created_at') else '',  # Optional: Relevant date
            "underwriter": task['responsible'],  # Optional: Person responsible
            "amount": 0,  # Optional: Numeric value (not applicable for tasks)
            "risk_rating": task['priority'],  # Optional: Risk assessment (using priority)
            "source": "Family",  # Optional: Source of the task
            "custom_html": custom_html,  # Optional: Custom HTML content
            "title": title_with_priority,
            "description": task['description'],
            "responsible": task['responsible'],
            "priority": task['priority']
        })
    
    return kanban_deals

def update_task_status_from_kanban(kanban_result, tasks):
    """Update task status based on kanban board changes"""
    if kanban_result:
        # Handle different possible return formats
        try:
            # Check if it's a list of dictionaries
            if isinstance(kanban_result, list):
                for item in kanban_result:
                    if isinstance(item, dict):
                        # Extract numeric ID from deal_id (e.g., "TASK-1" -> 1)
                        deal_id = item.get('deal_id', '')
                        if deal_id.startswith('TASK-'):
                            task_id = int(deal_id.replace('TASK-', ''))
                        else:
                            task_id = int(deal_id) if deal_id.isdigit() else 0
                        
                        new_stage = item.get('stage', 'To Do')
                        
                        # Map stage back to status
                        stage_to_status = {
                            "To Do": "Open",
                            "In Progress": "In Progress",
                            "Done": "Done"
                        }
                        
                        new_status = stage_to_status.get(new_stage, "Open")
                        
                        # Find and update the task
                        for task in tasks:
                            if task['id'] == task_id:
                                task['status'] = new_status
                                break
            elif isinstance(kanban_result, dict):
                # Handle single dictionary result
                deal_id = kanban_result.get('deal_id', '')
                if deal_id.startswith('TASK-'):
                    task_id = int(deal_id.replace('TASK-', ''))
                else:
                    task_id = int(deal_id) if deal_id.isdigit() else 0
                
                new_stage = kanban_result.get('stage', 'To Do')
                
                # Map stage back to status
                stage_to_status = {
                    "To Do": "Open",
                    "In Progress": "In Progress",
                    "Done": "Done"
                }
                
                new_status = stage_to_status.get(new_stage, "Open")
                
                # Find and update the task
                for task in tasks:
                    if task['id'] == task_id:
                        task['status'] = new_status
                        break
            else:
                # If it's neither list nor dict, log it but don't error
                st.write(f"Kanban result type: {type(kanban_result)}")
                
        except Exception as e:
            st.warning(f"Could not process kanban result: {e}")
    
    return tasks

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

if 'show_form' not in st.session_state:
    st.session_state.show_form = False

if 'editing_task' not in st.session_state:
    st.session_state.editing_task = None

# Main header
st.markdown('<h1 class="main-header">👨‍👩‍👧‍👦 Family Task Manager</h1>', unsafe_allow_html=True)

# Initialize filter states
if 'filter_stage' not in st.session_state:
    st.session_state.filter_stage = "All"
if 'filter_priority' not in st.session_state:
    st.session_state.filter_priority = "All"
if 'filter_responsible' not in st.session_state:
    st.session_state.filter_responsible = "All"

# Filter section in main content area
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.subheader("🔍 Filter Tasks")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    # Stage filter
    stages = ["All"] + list(set([task['status'] for task in st.session_state.tasks]))
    if st.session_state.filter_stage in stages:
        current_stage_index = stages.index(st.session_state.filter_stage)
    else:
        current_stage_index = 0
    st.session_state.filter_stage = st.selectbox("📊 Filter by Stage:", stages, index=current_stage_index)

with col2:
    # Priority filter
    priorities = ["All"] + list(set([task['priority'] for task in st.session_state.tasks]))
    if st.session_state.filter_priority in priorities:
        current_priority_index = priorities.index(st.session_state.filter_priority)
    else:
        current_priority_index = 0
    st.session_state.filter_priority = st.selectbox("⚡ Filter by Priority:", priorities, index=current_priority_index)

with col3:
    # Responsible person filter
    responsible_people = ["All"] + list(set([task['responsible'] for task in st.session_state.tasks]))
    if st.session_state.filter_responsible in responsible_people:
        current_responsible_index = responsible_people.index(st.session_state.filter_responsible)
    else:
        current_responsible_index = 0
    st.session_state.filter_responsible = st.selectbox("👤 Filter by Person:", responsible_people, index=current_responsible_index)

with col4:
    st.write("")  # Empty space for alignment
    st.write("")  # Empty space for alignment
    # Clear filters button
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.filter_stage = "All"
        st.session_state.filter_priority = "All"
        st.session_state.filter_responsible = "All"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Additional management options
    st.subheader("🔧 Management")
    
    if st.button("🎯 Load Example Tasks", use_container_width=True):
        st.session_state.tasks = get_example_family_tasks()
        save_tasks(st.session_state.tasks)
        st.success("Example family tasks loaded!")
        st.rerun()
    
    if st.button("🗑️ Delete All Tasks", use_container_width=True):
        if st.session_state.get("confirm_delete_all", False):
            st.session_state.tasks = []
            save_tasks(st.session_state.tasks)
            st.session_state["confirm_delete_all"] = False
            st.success("All tasks deleted!")
            st.rerun()
        else:
            st.session_state["confirm_delete_all"] = True
            st.warning("⚠️ Are you sure you want to delete ALL tasks?")
            st.rerun()
    
    if st.session_state.get("confirm_delete_all", False):
        if st.button("✅ Confirm Delete All", use_container_width=True):
            st.session_state.tasks = []
            save_tasks(st.session_state.tasks)
            st.session_state["confirm_delete_all"] = False
            st.success("All tasks deleted!")
            st.rerun()
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state["confirm_delete_all"] = False
            st.rerun()

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
    # Apply filters to tasks
    filtered_tasks = filter_tasks(
        st.session_state.tasks,
        st.session_state.filter_stage,
        st.session_state.filter_priority,
        st.session_state.filter_responsible
    )
    
    if not filtered_tasks:
        st.warning("🔍 No tasks match your current filters. Try adjusting the filter settings in the sidebar.")
    else:
        # Convert filtered tasks to kanban format
        kanban_deals = convert_tasks_to_kanban_format(filtered_tasks)
        
        # Define the kanban board stages (columns)
        stages = ["To Do", "In Progress", "Done"]
        
        # Display the kanban board
        kanban_result = kanban_board(
            stages=stages,
            deals=kanban_deals,
            key="family_task_kanban"
        )
        
        # Handle kanban board changes - re-enabled with better error handling
        if kanban_result:
            # Update tasks based on kanban changes
            updated_tasks = update_task_status_from_kanban(kanban_result, st.session_state.tasks)
            st.session_state.tasks = updated_tasks
            save_tasks(st.session_state.tasks)
            st.success("✅ Task moved successfully!")
            st.rerun()
    
    # Display task management options below the kanban board
    st.subheader("🔧 Task Management")
    
    # Create a detailed task list for editing and deleting
    if st.session_state.tasks:
        st.write("**📋 Task Details & Management**")
        st.write("Use the Kanban board above to move tasks between stages. Use the details below to edit or delete tasks.")
        
        # Use filtered tasks for the management section too
        management_tasks = filtered_tasks if 'filtered_tasks' in locals() else st.session_state.tasks
        
        for task in management_tasks:
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            status_emoji = {"Open": "🟢", "In Progress": "🟡", "Done": "✅"}
            
            with st.expander(f"{status_emoji.get(task['status'], '📋')} {task['title']} {priority_emoji.get(task['priority'], '')} - {task['status']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**📝 Description:** {task['description']}")
                    st.write(f"**👤 Responsible:** {task['responsible']}")
                    st.write(f"**📊 Priority:** {task['priority']}")
                    st.write(f"**📅 Created:** {task.get('created_at', 'Unknown')}")
                    
                    # Status change dropdown
                    new_status = st.selectbox(
                        "Change Status:",
                        ["Open", "In Progress", "Done"],
                        index=["Open", "In Progress", "Done"].index(task['status']),
                        key=f"status_change_{task['id']}"
                    )
                    
                    if new_status != task['status']:
                        if st.button(f"Update to {new_status}", key=f"update_status_{task['id']}"):
                            task['status'] = new_status
                            save_tasks(st.session_state.tasks)
                            st.success(f"Task status updated to {new_status}!")
                            st.rerun()
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_task_{task['id']}"):
                        st.session_state.editing_task = task['id']
                        st.session_state.show_form = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_task_{task['id']}"):
                        if st.session_state.get(f"confirm_delete_{task['id']}", False):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                            save_tasks(st.session_state.tasks)
                            st.session_state[f"confirm_delete_{task['id']}"] = False
                            st.success(f"Task '{task['title']}' deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.warning(f"⚠️ Delete '{task['title']}'?")
                            st.rerun()
                
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    if st.button("✅ Confirm Delete", key=f"confirm_delete_task_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.success(f"Task '{task['title']}' deleted!")
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_delete_task_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>👨‍👩‍👧‍👦 Family Task Manager - Keep your family organized and productive!</p>
    <p>Made with ❤️ using Streamlit and streamlit-kanban-board-goviceversa</p>
</div>
""", unsafe_allow_html=True)
