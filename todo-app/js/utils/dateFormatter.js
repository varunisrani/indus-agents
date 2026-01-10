export function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (isSameDay(date, today)) {
        return 'Today';
    } else if (isSameDay(date, tomorrow)) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
        });
    }
}

export function isOverdue(dateString) {
    if (!dateString) return false;
    
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return date < today;
}

export function isDueToday(dateString) {
    if (!dateString) return false;
    
    const date = new Date(dateString);
    const today = new Date();
    
    return isSameDay(date, today);
}

export function isSameDay(date1, date2) {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
}

export function getDueTasksCount(tasks) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return tasks.filter(task => {
        if (!task.dueDate || task.completed) return false;
        const taskDate = new Date(task.dueDate);
        return isSameDay(taskDate, today) || isOverdue(task.dueDate);
    }).length;
}