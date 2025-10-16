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
    
    .kanban-column {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        min-height: 400px;
        border: 2px solid #e9ecef;
    }
    
    .open-column {
        border-left: 5px solid #28a745;
    }
    
    .progress-column {
        border-left: 5px solid #ffc107;
    }
    
    .done-column {
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
        
        .kanban-column {
            margin: 0.25rem;
            min-height: 300px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Data storage functions
def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists('tasks_pt.json'):
        try:
            with open('tasks_pt.json', 'r') as f:
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
            "title": "Planear piquenique familiar do fim de semana",
            "description": "Pesquisar parques, preparar lanches e organizar jogos ao ar livre",
            "responsible": "Mãe",
            "priority": "High",
            "status": "In Progress",
            "created_at": "2025-01-15T10:00:00"
        },
        {
            "id": 2,
            "title": "Organizar o quarto dos brinquedos das crianças",
            "description": "Separar brinquedos, doar itens não utilizados e criar sistema de arrumação",
            "responsible": "Pai",
            "priority": "Medium",
            "status": "In Progress",
            "created_at": "2025-01-14T15:30:00"
        },
        {
            "id": 3,
            "title": "Compras de supermercado para a semana",
            "description": "Comprar ingredientes para refeições familiares e lanches",
            "responsible": "Mãe",
            "priority": "High",
            "status": "Done",
            "created_at": "2025-01-13T09:00:00"
        },
        {
            "id": 4,
            "title": "Preparar noite de cinema familiar",
            "description": "Escolher filme, preparar pipocas e arrumar lugares confortáveis",
            "responsible": "Crianças",
            "priority": "Low",
            "status": "Done",
            "created_at": "2025-01-12T19:00:00"
        },
        {
            "id": 5,
            "title": "Limpar e organizar a garagem",
            "description": "Separar ferramentas, organizar armazenamento e criar espaço de trabalho",
            "responsible": "Pai",
            "priority": "Medium",
            "status": "Done",
            "created_at": "2025-01-11T14:00:00"
        },
        {
            "id": 6,
            "title": "Preparar álbum de fotografias da família",
            "description": "Imprimir fotos das últimas férias e organizar no álbum",
            "responsible": "Mãe",
            "priority": "Low",
            "status": "Done",
            "created_at": "2025-01-10T16:45:00"
        }
    ]

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open('tasks_pt.json', 'w') as f:
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

# Kanban Board using native Streamlit components
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
        st.warning("🔍 No tasks match your current filters. Try adjusting the filter settings above.")
    else:
        # Create three columns for the Kanban board using Streamlit's native columns
        col1, col2, col3 = st.columns(3)
        
        # Open Tasks Column
        with col1:
            st.markdown('<div class="kanban-column open-column">', unsafe_allow_html=True)
            st.markdown('<div class="column-header">🟢 Open Tasks</div>', unsafe_allow_html=True)
            
            open_tasks = [task for task in filtered_tasks if task['status'] == 'Open']
            for task in open_tasks:
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                
                st.markdown(f'''
                <div class="task-card priority-{task['priority'].lower()}">
                    <div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem; color: #2c3e50;">
                        {task['title']} {priority_emoji.get(task['priority'], '')}
                    </div>
                    <div style="color: #6c757d; margin-bottom: 0.5rem; font-size: 0.9rem; font-style: italic;">
                        {task['description']}
                    </div>
                    <div style="color: #2E86AB; font-weight: 500; margin-bottom: 0.5rem;">
                        👤 {task['responsible']}
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        Priority: {task['priority']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("➡️", key=f"move_progress_{task['id']}", help="Move to In Progress"):
                        task['status'] = 'In Progress'
                        save_tasks(st.session_state.tasks)
                        st.success("Task moved to In Progress!")
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
                            st.success(f"Task '{task['title']}' deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.warning(f"⚠️ Delete '{task['title']}'?")
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    if st.button("✅ Confirm Delete", key=f"confirm_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.success(f"Task '{task['title']}' deleted!")
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                
                st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # In Progress Tasks Column
        with col2:
            st.markdown('<div class="kanban-column progress-column">', unsafe_allow_html=True)
            st.markdown('<div class="column-header">🟡 In Progress</div>', unsafe_allow_html=True)
            
            progress_tasks = [task for task in filtered_tasks if task['status'] == 'In Progress']
            for task in progress_tasks:
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                
                st.markdown(f'''
                <div class="task-card priority-{task['priority'].lower()}">
                    <div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem; color: #2c3e50;">
                        {task['title']} {priority_emoji.get(task['priority'], '')}
                    </div>
                    <div style="color: #6c757d; margin-bottom: 0.5rem; font-size: 0.9rem; font-style: italic;">
                        {task['description']}
                    </div>
                    <div style="color: #2E86AB; font-weight: 500; margin-bottom: 0.5rem;">
                        👤 {task['responsible']}
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        Priority: {task['priority']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("✅", key=f"move_done_{task['id']}", help="Move to Done"):
                        task['status'] = 'Done'
                        save_tasks(st.session_state.tasks)
                        st.success("Task moved to Done!")
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
                            st.success(f"Task '{task['title']}' deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.warning(f"⚠️ Delete '{task['title']}'?")
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    if st.button("✅ Confirm Delete", key=f"confirm_progress_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.success(f"Task '{task['title']}' deleted!")
                        st.rerun()
                    if st.button("❌ Cancel", key=f"cancel_progress_{task['id']}"):
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.rerun()
                
                st.divider()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Done Tasks Column
        with col3:
            st.markdown('<div class="kanban-column done-column">', unsafe_allow_html=True)
            st.markdown('<div class="column-header">✅ Done</div>', unsafe_allow_html=True)
            
            done_tasks = [task for task in filtered_tasks if task['status'] == 'Done']
            for task in done_tasks:
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                
                st.markdown(f'''
                <div class="task-card priority-{task['priority'].lower()}">
                    <div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem; color: #2c3e50;">
                        {task['title']} {priority_emoji.get(task['priority'], '')}
                    </div>
                    <div style="color: #6c757d; margin-bottom: 0.5rem; font-size: 0.9rem; font-style: italic;">
                        {task['description']}
                    </div>
                    <div style="color: #2E86AB; font-weight: 500; margin-bottom: 0.5rem;">
                        👤 {task['responsible']}
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        Priority: {task['priority']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("⬅️", key=f"move_back_{task['id']}", help="Move back to In Progress"):
                        task['status'] = 'In Progress'
                        save_tasks(st.session_state.tasks)
                        st.success("Task moved back to In Progress!")
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
                            st.success(f"Task '{task['title']}' deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task['id']}"] = True
                            st.warning(f"⚠️ Delete '{task['title']}'?")
                            st.rerun()
                
                # Confirmation prompt
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    if st.button("✅ Confirm Delete", key=f"confirm_done_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.session_state[f"confirm_delete_{task['id']}"] = False
                        st.success(f"Task '{task['title']}' deleted!")
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
