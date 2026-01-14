export function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

export function validateTaskTitle(title) {
    if (!title || title.trim().length === 0) {
        return { valid: false, error: 'Task title is required' };
    }
    if (title.length > 200) {
        return { valid: false, error: 'Task title is too long (max 200 characters)' };
    }
    return { valid: true };
}

export function validateCategoryName(name) {
    if (!name || name.trim().length === 0) {
        return { valid: false, error: 'Category name is required' };
    }
    if (name.length > 50) {
        return { valid: false, error: 'Category name is too long (max 50 characters)' };
    }
    return { valid: true };
}

export function validateImportData(data) {
    if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Invalid data format' };
    }
    
    if (!Array.isArray(data.tasks)) {
        return { valid: false, error: 'Invalid tasks data' };
    }
    
    if (!Array.isArray(data.categories)) {
        return { valid: false, error: 'Invalid categories data' };
    }
    
    return { valid: true };
}