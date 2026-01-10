import { Store } from './model/Store.js';
import { TaskView } from './view/TaskView.js';
import { CategoryView } from './view/CategoryView.js';
import { DashboardView } from './view/DashboardView.js';
import { TaskController } from './controller/TaskController.js';
import { CategoryController } from './controller/CategoryController.js';
import { FilterController } from './controller/FilterController.js';
import { KeyboardShortcuts } from './utils/shortcuts.js';
import { Renderer } from './view/Renderer.js';

class TodoApp {
    constructor() {
        this.store = new Store();
        this.filterController = new FilterController();
        
        this.taskView = new TaskView(document.getElementById('taskList'));
        this.categoryView = new CategoryView(document.getElementById('categoryList'));
        this.dashboardView = new DashboardView();
        
        this.taskController = new TaskController(this.store, this.taskView);
        this.categoryController = new CategoryController(this.store, this.categoryView);
        
        this.shortcuts = new KeyboardShortcuts();
        
        this.init();
    }
    
    init() {
        this.initTheme();
        this.initEventListeners();
        this.initKeyboardShortcuts();
        this.render();
    }
    
    initTheme() {
        const settings = this.store.getSettings();
        const theme = settings.theme || 'light';
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeIcon(theme);
    }
    
    updateThemeIcon(theme) {
        const icon = document.querySelector('.theme-icon');
        if (icon) {
            icon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        this.store.updateSettings({ theme: newTheme });
        this.updateThemeIcon(newTheme);
    }
    
    initEventListeners() {
        this.taskForm = document.getElementById('taskForm');
        this.searchInput = document.getElementById('searchInput');
        this.filterSelect = document.getElementById('filterSelect');
        this.sortSelect = document.getElementById('sortSelect');
        this.themeToggle = document.getElementById('themeToggle');
        this.exportBtn = document.getElementById('exportBtn');
        this.importInput = document.getElementById('importInput');
        
        this.taskForm.addEventListener('submit', (e) => this.handleAddTask(e));
        this.searchInput.addEventListener('input', this.debounce((e) => this.handleSearch(e), 300));
        this.filterSelect.addEventListener('change', (e) => this.handleFilterChange(e));
        this.sortSelect.addEventListener('change', (e) => this.handleSortChange(e));
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        this.exportBtn.addEventListener('click', () => this.handleExport());
        this.importInput.addEventListener('change', (e) => this.handleImport(e));
        
        document.getElementById('taskList').addEventListener('click', (e) => this.handleTaskAction(e));
        document.getElementById('categoryList').addEventListener('click', (e) => this.handleCategoryClick(e));
        document.getElementById('addCategoryBtn').addEventListener('click', () => this.handleAddCategory());
        
        const modalClose = document.getElementById('modalClose');
        const modalOverlay = document.getElementById('modalOverlay');
        const editCancel = document.getElementById('editCancel');
        const editForm = document.getElementById('editForm');
        
        modalClose.addEventListener('click', () => Renderer.hideModal('editModal'));
        modalOverlay.addEventListener('click', () => Renderer.hideModal('editModal'));
        editCancel.addEventListener('click', () => Renderer.hideModal('editModal'));
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.taskController.saveEditedTask();
            this.render();
        });
        
        this.taskController.onTasksChange = () => this.render();
        this.categoryController.onCategoriesChange = () => this.render();
        
        window.addEventListener('storage', () => {
            this.store.data = this.store.load();
            this.render();
        });
    }
    
    initKeyboardShortcuts() {
        this.shortcuts.register('ctrl+n', () => {
            document.getElementById('taskTitle').focus();
        }, 'Quick add task');
        
        this.shortcuts.register('ctrl+f', () => {
            this.searchInput.focus();
        }, 'Focus search');
        
        this.shortcuts.register('escape', () => {
            Renderer.hideModal('editModal');
        }, 'Close modal');
    }
    
    handleAddTask(e) {
        e.preventDefault();
        
        const title = document.getElementById('taskTitle').value.trim();
        const category = document.getElementById('taskCategory').value;
        const priority = document.getElementById('taskPriority').value;
        const dueDate = document.getElementById('taskDueDate').value || null;
        
        if (!title) {
            Renderer.showNotification('Please enter a task title', 'error');
            return;
        }
        
        this.taskController.addTask({ title, category, priority, dueDate });
        
        this.taskForm.reset();
        document.getElementById('taskPriority').value = 'medium';
        
        Renderer.showNotification('Task added successfully', 'success');
    }
    
    handleTaskAction(e) {
        const button = e.target.closest('button');
        if (!button) return;
        
        const taskItem = button.closest('.task-item');
        if (!taskItem) return;
        
        const taskId = taskItem.dataset.taskId;
        const action = button.dataset.action;
        
        switch (action) {
            case 'toggle':
                this.taskController.toggleTaskComplete(taskId);
                break;
            case 'edit':
                this.taskController.openEditModal(taskId, this.categoryController.getCategories());
                break;
            case 'delete':
                if (confirm('Are you sure you want to delete this task?')) {
                    this.taskController.deleteTask(taskId);
                    Renderer.showNotification('Task deleted', 'success');
                }
                break;
        }
    }
    
    handleCategoryClick(e) {
        const button = e.target.closest('.category-button');
        if (!button) return;
        
        const categoryItem = button.closest('.category-item');
        const categoryId = categoryItem.dataset.category;
        
        this.filterController.setCategory(categoryId);
        this.render();
    }
    
    handleAddCategory() {
        const name = prompt('Enter category name:');
        if (name && name.trim()) {
            this.categoryController.addCategory(name.trim());
        }
    }
    
    handleSearch(e) {
        this.filterController.setSearchQuery(e.target.value);
        this.render();
    }
    
    handleFilterChange(e) {
        this.filterController.setFilter(e.target.value);
        this.render();
    }
    
    handleSortChange(e) {
        this.filterController.setSortBy(e.target.value);
        this.render();
    }
    
    handleExport() {
        try {
            this.store.exportData();
            Renderer.showNotification('Data exported successfully', 'success');
        } catch (error) {
            Renderer.showNotification(error.message, 'error');
        }
    }
    
    handleImport(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                this.store.importData(event.target.result);
                Renderer.showNotification('Data imported successfully', 'success');
                this.render();
            } catch (error) {
                Renderer.showNotification(error.message, 'error');
            }
        };
        reader.readAsText(file);
        e.target.value = '';
    }
    
    render() {
        const { filter, category, searchQuery, sortBy } = this.filterController.getFilterState();
        const categories = this.categoryController.getCategories();
        const tasks = this.taskController.getFilteredTasks(filter, category, searchQuery, sortBy);
        
        this.taskView.renderTasks(tasks, categories);
        this.categoryView.renderCategories(categories, this.store.getTasks(), category);
        this.dashboardView.updateStats(this.store.getTasks());
        
        const categorySelect = document.getElementById('taskCategory');
        this.categoryView.updateCategorySelect(categories, categorySelect);
        
        const categoryTitle = document.getElementById('currentCategoryTitle');
        if (category === 'all') {
            categoryTitle.textContent = 'All Tasks';
        } else {
            const cat = categories.find(c => c.id === category);
            categoryTitle.textContent = cat ? `${cat.icon} ${cat.name}` : 'All Tasks';
        }
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TodoApp();
});