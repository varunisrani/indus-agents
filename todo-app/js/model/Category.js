import { generateUUID } from '../utils/uuid.js';
import { sanitizeInput, validateCategoryName } from '../utils/validator.js';

export class Category {
    constructor({ id, name, color = '#3B82F6', icon = '📁' } = {}) {
        this.id = id || generateUUID();
        this.name = sanitizeInput(name);
        this.color = color;
        this.icon = icon;
    }
    
    update(updates) {
        const allowedUpdates = ['name', 'color', 'icon'];
        
        for (const [key, value] of Object.entries(updates)) {
            if (allowedUpdates.includes(key)) {
                if (key === 'name') {
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
            name: this.name,
            color: this.color,
            icon: this.icon
        };
    }
    
    static fromJSON(data) {
        return new Category(data);
    }
    
    static getDefaultCategories() {
        return [
            new Category({ id: 'work', name: 'Work', color: '#3B82F6', icon: '💼' }),
            new Category({ id: 'personal', name: 'Personal', color: '#10B981', icon: '👤' }),
            new Category({ id: 'shopping', name: 'Shopping', color: '#F59E0B', icon: '🛒' }),
            new Category({ id: 'health', name: 'Health', color: '#EF4444', icon: '❤️' })
        ];
    }
}