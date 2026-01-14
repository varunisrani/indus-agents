import { Task } from '../model/Task.js';
import { Renderer } from '../view/Renderer.js';

export class TaskController {
    constructor(store, taskView) {
        this.store = store;
        this.taskView = taskView;
        this.onTasksChange = null;
    }
    
    addTask(taskData) {
        const task = new Task(taskData);
        this.store.addTask(task.toJSON());
        this.notifyChange();
        return task;
    }
    
    updateTask(taskId, updates) {
        this.store.updateTask(taskId, updates);
        this.notifyChange();
    }
    
    deleteTask(taskId) {
        this.store.deleteTask(taskId);
        this.notifyChange();
    }
    
    toggleTaskComplete(taskId) {
        const tasks = this.store.getTasks();
        const task = tasks.find(t => t.id === taskId);
        
        if (task) {
            const updatedTask = new Task(task);
            updatedTask.toggleComplete();
            this.store.updateTask(taskId, { 
                completed: updatedTask.completed,
                completedAt: updatedTask.completedAt 
            });
            this.notifyChange();
            
            const message = updatedTask.completed ? 'Task completed!' : 'Task marked as active';
            Renderer.showNotification(message, 'success');
        }
    }
    
    openEditModal(taskId, categories) {
        const tasks = this.store.getTasks();
        const task = tasks.find(t => t.id === taskId);
        
        if (!task) return;
        
        const modal = document.getElementById('editModal');
        const form = document.getElementById('editForm');
        
        document.getElementById('editTaskId').value = task.id;
        document.getElementById('editTaskTitle').value = task.title;
        document.getElementById('editTaskPriority').value = task.priority;
        document.getElementById('editTaskDueDate').value = task.dueDate || '';
        
        const categorySelect = document.getElementById('editTaskCategory');
        categorySelect.innerHTML = '<option value="">No Category</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = `${cat.icon} ${cat.name}`;
            if (cat.id === task.category) option.selected = true;
            categorySelect.appendChild(option);
        });
        
        Renderer.showModal('editModal');
        document.getElementById('editTaskTitle').focus();
    }
    
    saveEditedTask() {
        const taskId = document.getElementById('editTaskId').value;
        const title = document.getElementById('editTaskTitle').value.trim();
        const priority = document.getElementById('editTaskPriority').value;
        const category = document.getElementById('editTaskCategory').value;
        const dueDate = document.getElementById('editTaskDueDate').value || null;
        
        if (!title) {
            Renderer.showNotification('Task title is required', 'error');
            return;
        }
        
        this.updateTask(taskId, { title, priority, category, dueDate });
        Renderer.hideModal('editModal');
        Renderer.showNotification('Task updated successfully', 'success');
    }
    
    getFilteredTasks(filter = 'all', category = 'all', searchQuery = '', sortBy = 'created') {
        let tasks = [...this.store.getTasks()];
        
        if (category !== 'all') {
            tasks = tasks.filter(t => t.category === category);
        }
        
        if (filter === 'active') {
            tasks = tasks.filter(t => !t.completed);
        } else if (filter === 'completed') {
            tasks = tasks.filter(t => t.completed);
        }
        
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            tasks = tasks.filter(t => 
                t.title.toLowerCase().includes(query) ||
                (t.description && t.description.toLowerCase().includes(query))
            );
        }
        
        tasks = this.sortTasks(tasks, sortBy);
        
        return tasks;
    }
    
    sortTasks(tasks, sortBy) {
        return tasks.sort((a, b) => {
            switch (sortBy) {
                case 'dueDate':
                    if (!a.dueDate) return 1;
                    if (!b.dueDate) return -1;
                    return new Date(a.dueDate) - new Date(b.dueDate);
                
                case 'priority':
                    const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
                    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
                    if (priorityDiff !== 0) return priorityDiff;
                    return new Date(b.createdAt) - new Date(a.createdAt);
                
                case 'created':
                default:
                    return new Date(b.createdAt) - new Date(a.createdAt);
            }
        });
    }
    
    notifyChange() {
        if (this.onTasksChange) {
            this.onTasksChange();
        }
    }
}