# 👨‍👩‍👧‍👦 Family Task Manager

A simple and intuitive web application for managing family tasks with a Kanban-style interface.

## Features

✅ **Full CRUD Operations**: Create, Read, Update, and Delete tasks  
✅ **Task Fields**: Title, Description, Responsible Person, Priority (Low/Medium/High), Status  
✅ **Kanban Board**: Three columns (Open, In Progress, Done)  
✅ **Visual Task Cards**: Color-coded by priority with clear information display  
✅ **Data Persistence**: Tasks are saved to a local JSON file  
✅ **Mobile-Friendly**: Responsive design that works on all devices  
✅ **User-Friendly**: Simple interface perfect for non-technical family members  

## How to Run the App

### Prerequisites
- Python 3.7 or higher
- Streamlit library

### Step 1: Install Streamlit
Open your terminal/command prompt and run:
```bash
pip install streamlit
```

### Step 2: Navigate to the App Directory
```bash
cd /path/to/your/vibecoding-cursor-streamlit/folder
```

### Step 3: Run the App
```bash
streamlit run family_task_manager.py
```

### Step 4: Open in Browser
Streamlit will automatically open your web browser and display the app at:
```
http://localhost:8501
```

## How to Use

1. **Add a New Task**: Click the "➕ Add New Task" button in the sidebar
2. **Fill in Details**: Enter the task title, description, responsible person, priority, and status
3. **Save**: Click "💾 Save Task" to add it to your board
4. **Move Tasks**: Use the arrow buttons (➡️, ✅, ⬅️) to move tasks between columns
5. **Edit Tasks**: Click the ✏️ button to modify any task
6. **Delete Tasks**: Click the 🗑️ button and confirm to remove tasks

## Data Storage

- All tasks are automatically saved to a `tasks.json` file in the same directory
- Your data persists between app sessions
- No external database required - everything runs locally

## Mobile Usage

The app is fully responsive and works great on:
- 📱 Smartphones
- 📱 Tablets  
- 💻 Laptops
- 🖥️ Desktop computers

## Troubleshooting

**App won't start?**
- Make sure Python and Streamlit are installed correctly
- Check that you're in the right directory
- Try running `python -m streamlit run family_task_manager.py`

**Tasks not saving?**
- Check that the app has permission to write files in the directory
- Look for a `tasks.json` file in the same folder as the app

**Need help?**
- The interface is designed to be intuitive
- All buttons have helpful tooltips
- Try the sidebar for quick task statistics

---

*Keep your family organized and productive with this simple task management tool!* 🎉
