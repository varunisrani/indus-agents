# Todo App - Modern Task Management Application

A fully-featured, responsive todo application built with vanilla HTML, CSS, and JavaScript. No frameworks required!

## Features

### Core Functionality
- ✅ Create, edit, and delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Category organization (Work, Personal, Shopping, Health)
- ✅ Priority levels (Low, Medium, High, Urgent)
- ✅ Due dates with overdue highlighting
- ✅ Real-time search across all tasks
- ✅ Filter by status (All, Active, Completed)
- ✅ Sort by creation date, due date, or priority

### Advanced Features
- 🌙 Dark/Light theme toggle
- 📊 Statistics dashboard
- 💾 Data persistence with localStorage
- ⬇️ Export data as JSON
- ⬆️ Import data from JSON
- ⌨️ Keyboard shortcuts (Ctrl+N: Add task, Ctrl+F: Search, Esc: Close modal)
- 📱 Fully responsive design
- ♿ WCAG 2.1 AA accessible

## Tech Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern layout (Grid, Flexbox), CSS custom properties
- **Vanilla JavaScript (ES6+)** - No frameworks
- **LocalStorage API** - Client-side data persistence

## Project Structure

```
todo-app/
├── index.html                 # Main HTML file
├── css/
│   ├── variables.css         # CSS custom properties
│   ├── main.css              # Base styles and reset
│   ├── layout.css            # App layout (sidebar, main content)
│   ├── components.css        # UI components (tasks, forms, modals)
│   └── themes.css            # Light/dark theme styles
├── js/
│   ├── app.js                # Main application entry point
│   ├── model/
│   │   ├── Task.js           # Task model
│   │   ├── Category.js       # Category model
│   │   └── Store.js          # LocalStorage wrapper
│   ├── view/
│   │   ├── Renderer.js       # DOM rendering utilities
│   │   ├── TaskView.js       # Task list rendering
│   │   ├── CategoryView.js   # Category sidebar rendering
│   │   └── DashboardView.js  # Statistics dashboard
│   ├── controller/
│   │   ├── TaskController.js # Task CRUD operations
│   │   ├── CategoryController.js # Category operations
│   │   └── FilterController.js # Search/filter logic
│   └── utils/
│       ├── uuid.js           # UUID generator
│       ├── dateFormatter.js  # Date formatting utilities
│       ├── validator.js      # Input validation and sanitization
│       └── shortcuts.js      # Keyboard shortcuts
└── README.md                 # This file
```

## How to Use

### Getting Started

1. Open `index.html` in a modern web browser
2. Start adding tasks!

### Adding Tasks

1. Enter task title in the input field
2. Optionally select category, priority, and due date
3. Click "Add" or press Enter

### Managing Tasks

- **Complete**: Click the checkbox to mark tasks as complete
- **Edit**: Click the ✏️ icon to edit task details
- **Delete**: Click the 🗑️ icon to delete a task

### Categories

- Click on categories in the sidebar to filter tasks
- Click "+ Add Category" to create new categories
- Tasks are automatically organized by category

### Search & Filter

- Use the search bar to find tasks by title
- Filter by status (All, Active, Completed)
- Sort by creation date, due date, or priority

### Data Management

- **Export**: Click "Export" to download your tasks as JSON
- **Import**: Click "Import" to load tasks from a JSON file
- All data is automatically saved to your browser's localStorage

### Keyboard Shortcuts

- `Ctrl/Cmd + N` - Focus on new task input
- `Ctrl/Cmd + F` - Focus on search
- `Esc` - Close modal dialogs

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Features

- XSS prevention through input sanitization
- No external API calls
- All data stored locally
- No analytics or tracking

## Architecture

The application follows a Model-View-Controller (MVC) pattern:

- **Model**: Data structures and storage operations
- **View**: DOM rendering and UI updates
- **Controller**: Business logic and event handling

## Risk Mitigations

Based on critical risk assessment, the following mitigations are implemented:

1. **Data Persistence**: Export/import functionality for backup
2. **Cross-Browser Compatibility**: Feature detection and progressive enhancement
3. **State Management**: Centralized state with controlled mutations
4. **Accessibility**: ARIA labels, keyboard navigation, semantic HTML
5. **Input Validation**: Sanitization to prevent XSS attacks

## Future Enhancements

Potential features for future versions:
- Subtasks/checklists
- Task tags
- Recurring tasks
- Cloud sync (optional)
- PWA features for offline support
- Calendar view
- Drag-and-drop reordering

## License

Free to use and modify.

## Credits

Built with modern web standards and best practices.