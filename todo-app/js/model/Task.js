import { generateUUID } from '../utils/uuid.js';
import { sanitizeInput, validateTaskTitle } from '../utils/validator.js';

export class Task {
    constructor({ id, title, description = null, completed = false, priority = 'medium', category = 'default', dueDate = null, createdAt = null, completedAt = null } = {}) {
        this.id = id || generateUUID();
        this.title = sanitizeInput(title);
        this.description = description ? sanitizeInput(description) : null;
        this.completed = Boolean(completed);
        this.priority = this.validatePriority(priority);
        this.category = category || 'default';
        this.dueDate = dueDate || null;
        this.createdAt = createdAt || new Date().toISOString();
        this.completedAt = completedAt || null;
    }
    
    validatePriority(priority) {
        const validPriorities = ['low', 'medium', 'high', 'urgent'];
        return validPriorities.includes(priority) ? priority : 'medium';
    }
    
    toggleComplete() {
        this.completed = !this.completed;
        this.completedAt = this.completed ? new Date().toISOString() : null;
    }
    
    update(updates) {
        const allowedUpdates = ['title', 'description', 'priority', 'category', 'dueDate'];
        
        for (const [key, value] of Object.entries(updates)) {
            if (allowedUpdates.includes(key)) {
                if (key === 'priority') {
                    this[key] = this.validatePriority(value);
                } else if (key === 'title' || key === 'description') {
                    this[key] = sanitizeInput(value);
                } else {
                    this[key] = value;
                }
            }
        }
    }
    
    toJSON() {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            completed: this.completed,
            priority: this.priority,
            category: this.category,
            dueDate: this.dueDate,
            createdAt: this.createdAt,
            completedAt: this.completedAt
        };
    }
    
    static fromJSON(data) {
        return new Task(data);
    }
}