# 👨‍👩‍👧‍👦 Family Task Manager (Kanban Version)

A modern family task management app featuring a **drag-and-drop Kanban board** powered by the `streamlit-kanban-board-goviceversa` library.

## 🆕 What's New in This Version

✅ **Interactive Kanban Board**: Drag and drop tasks between columns  
✅ **Real-time Updates**: Changes are saved automatically  
✅ **Rich Task Cards**: Beautiful task display with priority indicators  
✅ **Enhanced Management**: Additional tools for bulk operations  
✅ **Professional Interface**: Clean, modern design  

## Features

### 🎯 **Core Functionality**
- **Full CRUD Operations**: Create, Read, Update, and Delete tasks
- **Drag & Drop**: Move tasks between Open, In Progress, and Done columns
- **Rich Task Information**: Title, description, responsible person, priority, status
- **Data Persistence**: Tasks saved to local JSON file

### 🎨 **Interactive Kanban Board**
- **Three Columns**: To Do, In Progress, Done
- **Rich Task Cards**: Beautiful HTML-rendered task cards with full details
- **Visual Priority**: Color-coded priority indicators (🔴 High, 🟡 Medium, 🟢 Low)
- **Drag & Drop**: Intuitive task movement between columns
- **Real-time Sync**: Changes saved automatically

### 🔧 **Enhanced Management**
- **Task Statistics**: Live counts in sidebar
- **Bulk Operations**: Delete all tasks option
- **Task Details**: Expandable task information
- **Quick Actions**: Edit and delete from task list

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install streamlit streamlit-kanban-board-goviceversa
```

### Step 2: Run the App
```bash
streamlit run family_task_manager_kanban.py
```

### Step 3: Open in Browser
The app will open at: `http://localhost:8501`

## How to Use

### 📋 **Creating Tasks**
1. Click "➕ Add New Task" in the sidebar
2. Fill in the task details:
   - **Title**: Task name
   - **Description**: Detailed description
   - **Responsible Person**: Who's doing the task
   - **Priority**: Low, Medium, or High
   - **Status**: Open, In Progress, or Done
3. Click "💾 Save Task"

### 🎯 **Using the Kanban Board**
1. **View Tasks**: Tasks appear as cards in their respective columns
2. **Move Tasks**: Drag and drop tasks between columns
3. **Priority Indicators**: See task priority with colored emojis
4. **Auto-Save**: Changes are saved automatically

### 🔧 **Managing Tasks**
1. **Edit Tasks**: Click "✏️ Edit" in the task list below the board
2. **Delete Tasks**: Click "🗑️ Delete" with confirmation prompt
3. **Bulk Delete**: Use "🗑️ Delete All Tasks" in sidebar (with confirmation)
4. **View Statistics**: Check task counts in the sidebar

## Key Differences from Standard Version

| Feature | Standard Version | Kanban Version |
|---------|------------------|----------------|
| **Board Type** | Static columns | Interactive drag & drop |
| **Task Movement** | Button clicks | Drag and drop |
| **Visual Appeal** | Basic cards | Rich task cards |
| **User Experience** | Form-based | Intuitive interactions |
| **Library** | Native Streamlit | streamlit-kanban-board-goviceversa |

## Data Storage

- **File**: `tasks.json` (same as standard version)
- **Format**: JSON with full task information
- **Compatibility**: Can switch between versions using the same data file

## Mobile Support

✅ **Responsive Design**: Works on all devices  
✅ **Touch Support**: Drag and drop works on mobile  
✅ **Optimized Layout**: Mobile-friendly interface  

## Troubleshooting

**Library not found?**
```bash
pip install streamlit-kanban-board-goviceversa
```

**Drag and drop not working?**
- Ensure you're using a modern browser
- Check that JavaScript is enabled
- Try refreshing the page

**Tasks not saving?**
- Check file permissions in the app directory
- Look for `tasks.json` file creation

## Comparison: Which Version to Use?

### Choose **Standard Version** if:
- You prefer simple, button-based interactions
- You want fewer dependencies
- You need maximum compatibility

### Choose **Kanban Version** if:
- You want modern, interactive experience
- You prefer drag-and-drop functionality
- You want a more professional look
- You enjoy rich, visual task management

---

*Both versions maintain the same core functionality while offering different user experiences. Choose the one that fits your family's preferences!* 🎯
