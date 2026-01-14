import { Renderer } from './Renderer.js';
import { formatDate, isOverdue, isDueToday } from '../utils/dateFormatter.js';

export class TaskView {
    constructor(taskListElement) {
        this.taskListElement = taskListElement;
    }
    
    renderTasks(tasks, categories = []) {
        this.taskListElement.innerHTML = '';
        
        if (tasks.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        tasks.forEach(task => {
            const taskElement = this.createTaskElement(task, categories);
            this.taskListElement.appendChild(taskElement);
        });
    }
    
    createTaskElement(task, categories = []) {
        const li = Renderer.createElement('li', `task-item ${task.completed ? 'completed' : ''}`);
        li.dataset.taskId = task.id;
        
        const checkbox = Renderer.createElement('button', `task-checkbox ${task.completed ? 'checked' : ''}`, task.completed ? '✓' : '');
        checkbox.setAttribute('aria-label', task.completed ? 'Mark as incomplete' : 'Mark as complete');
        checkbox.dataset.action = 'toggle';
        
        const content = Renderer.createElement('div', 'task-content');
        
        const title = Renderer.createElement('div', 'task-title', task.title);
        
        const meta = Renderer.createElement('div', 'task-meta');
        
        if (task.category) {
            const category = categories.find(c => c.id === task.category);
            if (category) {
                const categoryBadge = Renderer.createElement('span', 'task-category', `${category.icon} ${category.name}`);
                meta.appendChild(categoryBadge);
            }
        }
        
        if (task.priority) {
            const priorityBadge = Renderer.createElement('span', `priority-badge ${task.priority}`, task.priority);
            meta.appendChild(priorityBadge);
        }
        
        if (task.dueDate) {
            const dueDateSpan = Renderer.createElement('span', 'task-due-date');
            if (isOverdue(task.dueDate)) {
                dueDateSpan.classList.add('overdue');
                dueDateSpan.textContent = `⚠️ ${formatDate(task.dueDate)}`;
            } else if (isDueToday(task.dueDate)) {
                dueDateSpan.classList.add('due-today');
                dueDateSpan.textContent = `📅 ${formatDate(task.dueDate)}`;
            } else {
                dueDateSpan.textContent = `📅 ${formatDate(task.dueDate)}`;
            }
            meta.appendChild(dueDateSpan);
        }
        
        content.appendChild(title);
        content.appendChild(meta);
        
        const actions = Renderer.createElement('div', 'task-actions');
        
        const editBtn = Renderer.createElement('button', 'task-action-btn', '✏️');
        editBtn.setAttribute('aria-label', 'Edit task');
        editBtn.dataset.action = 'edit';
        
        const deleteBtn = Renderer.createElement('button', 'task-action-btn delete', '🗑️');
        deleteBtn.setAttribute('aria-label', 'Delete task');
        deleteBtn.dataset.action = 'delete';
        
        actions.appendChild(editBtn);
        actions.appendChild(deleteBtn);
        
        li.appendChild(checkbox);
        li.appendChild(content);
        li.appendChild(actions);
        
        return li;
    }
    
    renderEmptyState() {
        const emptyState = Renderer.createElement('li', 'empty-state');
        emptyState.innerHTML = `
            <div class="empty-icon">📝</div>
            <p>No tasks found. Add a new task to get started!</p>
        `;
        this.taskListElement.appendChild(emptyState);
    }
    
    updateTaskElement(task, categories = []) {
        const existingElement = this.taskListElement.querySelector(`[data-task-id="${task.id}"]`);
        if (existingElement) {
            const newElement = this.createTaskElement(task, categories);
            existingElement.replaceWith(newElement);
        }
    }
    
    removeTaskElement(taskId) {
        const element = this.taskListElement.querySelector(`[data-task-id="${taskId}"]`);
        if (element) {
            element.style.animation = 'slideOut 0.2s ease';
            setTimeout(() => element.remove(), 200);
        }
    }
}