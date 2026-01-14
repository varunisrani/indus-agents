class TodoApp {
    constructor() {
        this.todos = [];
        this.filter = 'all';
        this.sort = 'date';
        this.searchQuery = '';
        this.selectedTodos = new Set();
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        this.init();
    }

    init() {
        this.loadTodos();
        this.applyTheme();
        this.cacheElements();
        this.bindEvents();
        this.render();
    }

    cacheElements() {
        this.elements = {
            todoForm: document.getElementById('todoForm'),
            todoInput: document.getElementById('todoInput'),
            todoDescription: document.getElementById('todoDescription'),
            todoCategory: document.getElementById('todoCategory'),
            todoPriority: document.getElementById('todoPriority'),
            todoDueDate: document.getElementById('todoDueDate'),
            todoList: document.getElementById('todoList'),
            emptyState: document.getElementById('emptyState'),
            filterBtns: document.querySelectorAll('.filter-btn'),
            searchInput: document.getElementById('searchInput'),
            sortSelect: document.getElementById('sortSelect'),
            themeToggle: document.getElementById('themeToggle'),
            exportBtn: document.getElementById('exportBtn'),
            importBtn: document.getElementById('importBtn'),
            importFile: document.getElementById('importFile'),
            bulkActionsBar: document.getElementById('bulkActionsBar'),
            selectedCount: document.getElementById('selectedCount'),
            bulkComplete: document.getElementById('bulkComplete'),
            bulkDelete: document.getElementById('bulkDelete'),
            bulkCancel: document.getElementById('bulkCancel'),
            toast: document.getElementById('toast'),
            toastMessage: document.getElementById('toastMessage'),
            confirmDialog: document.getElementById('confirmDialog'),
            confirmTitle: document.getElementById('confirmTitle'),
            confirmMessage: document.getElementById('confirmMessage'),
            confirmCancel: document.getElementById('confirmCancel'),
            confirmOk: document.getElementById('confirmOk'),
            totalTodos: document.getElementById('totalTodos'),
            activeTodos: document.getElementById('activeTodos'),
            completedTodos: document.getElementById('completedTodos'),
            completionRate: document.getElementById('completionRate')
        };
    }

    bindEvents() {
        this.elements.todoForm.addEventListener('submit', (e) => this.handleAddTodo(e));
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', () => this.handleFilterChange(btn));
        });
        this.elements.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        this.elements.sortSelect.addEventListener('change', (e) => this.handleSort(e));
        this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
        this.elements.exportBtn.addEventListener('click', () => this.exportTodos());
        this.elements.importBtn.addEventListener('click', () => this.elements.importFile.click());
        this.elements.importFile.addEventListener('change', (e) => this.importTodos(e));
        this.elements.bulkComplete.addEventListener('click', () => this.bulkComplete());
        this.elements.bulkDelete.addEventListener('click', () => this.bulkDelete());
        this.elements.bulkCancel.addEventListener('click', () => this.clearSelection());
        this.elements.confirmCancel.addEventListener('click', () => this.hideConfirmDialog());
        this.elements.confirmOk.addEventListener('click', () => this.confirmAction());

        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    sanitizeInput(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    handleAddTodo(e) {
        e.preventDefault();
        
        const title = this.elements.todoInput.value.trim();
        if (!title) return;

        const todo = {
            id: this.generateId(),
            title: this.sanitizeInput(title),
            description: this.sanitizeInput(this.elements.todoDescription.value.trim()),
            category: this.elements.todoCategory.value,
            priority: this.elements.todoPriority.value,
            dueDate: this.elements.todoDueDate.value || null,
            completed: false,
            createdAt: new Date().toISOString()
        };

        this.todos.unshift(todo);
        this.saveTodos();
        this.render();
        this.resetForm();
        this.showToast('Todo added successfully!', 'success');
    }

    resetForm() {
        this.elements.todoForm.reset();
        this.elements.todoInput.focus();
    }

    toggleTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (todo) {
            todo.completed = !todo.completed;
            todo.completedAt = todo.completed ? new Date().toISOString() : null;
            this.saveTodos();
            this.render();
        }
    }

    deleteTodo(id) {
        this.showConfirmDialog(
            'Delete Todo',
            'Are you sure you want to delete this todo? This action cannot be undone.',
            () => {
                this.todos = this.todos.filter(t => t.id !== id);
                this.selectedTodos.delete(id);
                this.saveTodos();
                this.render();
                this.showToast('Todo deleted successfully!', 'success');
            }
        );
    }

    selectTodo(id) {
        if (this.selectedTodos.has(id)) {
            this.selectedTodos.delete(id);
        } else {
            this.selectedTodos.add(id);
        }
        this.render();
        this.updateBulkActionsBar();
    }

    clearSelection() {
        this.selectedTodos.clear();
        this.render();
        this.updateBulkActionsBar();
    }

    bulkComplete() {
        this.todos.forEach(todo => {
            if (this.selectedTodos.has(todo.id)) {
                todo.completed = true;
                todo.completedAt = new Date().toISOString();
            }
        });
        this.clearSelection();
        this.saveTodos();
        this.showToast('Selected todos completed!', 'success');
    }

    bulkDelete() {
        this.showConfirmDialog(
            'Delete Selected Todos',
            `Are you sure you want to delete ${this.selectedTodos.size} todo(s)? This action cannot be undone.`,
            () => {
                this.todos = this.todos.filter(t => !this.selectedTodos.has(t.id));
                this.clearSelection();
                this.saveTodos();
                this.showToast('Selected todos deleted!', 'success');
            }
        );
    }

    handleFilterChange(btn) {
        this.filter = btn.dataset.filter;
        this.elements.filterBtns.forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        this.render();
    }

    handleSearch(e) {
        this.searchQuery = e.target.value.toLowerCase();
        this.render();
    }

    handleSort(e) {
        this.sort = e.target.value;
        this.render();
    }

    getFilteredAndSortedTodos() {
        let filtered = [...this.todos];

        if (this.filter === 'active') {
            filtered = filtered.filter(t => !t.completed);
        } else if (this.filter === 'completed') {
            filtered = filtered.filter(t => t.completed);
        }

        if (this.searchQuery) {
            filtered = filtered.filter(t => 
                t.title.toLowerCase().includes(this.searchQuery) ||
                t.description.toLowerCase().includes(this.searchQuery)
            );
        }

        filtered.sort((a, b) => {
            if (this.sort === 'priority') {
                const priorityOrder = { high: 3, medium: 2, low: 1 };
                return priorityOrder[b.priority] - priorityOrder[a.priority];
            } else if (this.sort === 'name') {
                return a.title.localeCompare(b.title);
            } else {
                return new Date(b.createdAt) - new Date(a.createdAt);
            }
        });

        return filtered;
    }

    isOverdue(dueDate) {
        if (!dueDate) return false;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return new Date(dueDate) < today;
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (date.toDateString() === tomorrow.toDateString()) {
            return 'Tomorrow';
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
    }

    getCategoryIcon(category) {
        const icons = {
            personal: '🏠',
            work: '💼',
            shopping: '🛒',
            health: '💪'
        };
        return icons[category] || '📌';
    }

    render() {
        const filteredTodos = this.getFilteredAndSortedTodos();
        
        if (filteredTodos.length === 0) {
            this.elements.todoList.innerHTML = '';
            this.elements.emptyState.classList.remove('hidden');
        } else {
            this.elements.emptyState.classList.add('hidden');
            this.elements.todoList.innerHTML = filteredTodos.map(todo => this.createTodoHTML(todo)).join('');
        }

        this.updateStats();
        this.updateBulkActionsBar();
    }

    createTodoHTML(todo) {
        const overdue = this.isOverdue(todo.dueDate);
        const selected = this.selectedTodos.has(todo.id);
        
        return `
            <div class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
                <div class="todo-checkbox ${todo.completed ? 'checked' : ''}" 
                     role="checkbox" 
                     aria-checked="${todo.completed}"
                     tabindex="0"
                     onclick="app.toggleTodo('${todo.id}')"
                     onkeypress="if(event.key==='Enter')app.toggleTodo('${todo.id}')">
                    ${todo.completed ? '✓' : ''}
                </div>
                <div class="todo-content">
                    <div class="todo-title">${todo.title}</div>
                    ${todo.description ? `<div class="todo-description">${todo.description}</div>` : ''}
                    <div class="todo-meta">
                        <span class="todo-badge badge-category">
                            ${this.getCategoryIcon(todo.category)} ${todo.category}
                        </span>
                        <span class="todo-badge badge-priority priority-${todo.priority}">
                            ${todo.priority.toUpperCase()}
                        </span>
                        ${todo.dueDate ? `
                            <span class="todo-badge badge-date ${overdue ? 'overdue' : ''}">
                                📅 ${this.formatDate(todo.dueDate)} ${overdue ? '(Overdue)' : ''}
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="btn-action select ${selected ? 'selected' : ''}" 
                            aria-label="Select todo"
                            onclick="app.selectTodo('${todo.id}')">
                        ${selected ? '✓' : ''}
                    </button>
                    <button class="btn-action delete" 
                            aria-label="Delete todo"
                            onclick="app.deleteTodo('${todo.id}')">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }

    updateStats() {
        const total = this.todos.length;
        const completed = this.todos.filter(t => t.completed).length;
        const active = total - completed;
        const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

        this.elements.totalTodos.textContent = total;
        this.elements.activeTodos.textContent = active;
        this.elements.completedTodos.textContent = completed;
        this.elements.completionRate.textContent = rate + '%';
    }

    updateBulkActionsBar() {
        if (this.selectedTodos.size > 0) {
            this.elements.bulkActionsBar.classList.remove('hidden');
            this.elements.selectedCount.textContent = this.selectedTodos.size;
        } else {
            this.elements.bulkActionsBar.classList.add('hidden');
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        const icon = this.elements.themeToggle.querySelector('.icon');
        icon.textContent = this.currentTheme === 'light' ? '🌙' : '☀️';
    }

    saveTodos() {
        try {
            localStorage.setItem('todos', JSON.stringify(this.todos));
        } catch (error) {
            if (error.name === 'QuotaExceededError') {
                this.showToast('Storage full! Please export your data.', 'error');
            } else {
                this.showToast('Failed to save todos!', 'error');
            }
        }
    }

    loadTodos() {
        try {
            const stored = localStorage.getItem('todos');
            if (stored) {
                this.todos = JSON.parse(stored);
            }
        } catch (error) {
            this.showToast('Failed to load todos!', 'error');
            this.todos = [];
        }
    }

    exportTodos() {
        try {
            const dataStr = JSON.stringify(this.todos, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `todos-backup-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            URL.revokeObjectURL(url);
            this.showToast('Todos exported successfully!', 'success');
        } catch (error) {
            this.showToast('Failed to export todos!', 'error');
        }
    }

    importTodos(e) {
        const file = e.target.files[0];
        if (!file) return;

        if (file.size > 5 * 1024 * 1024) {
            this.showToast('File too large! Maximum size is 5MB.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const imported = JSON.parse(event.target.result);
                
                if (!Array.isArray(imported)) {
                    throw new Error('Invalid format');
                }

                const validTodos = imported.filter(todo => {
                    return todo.title && typeof todo.title === 'string' &&
                           todo.id && typeof todo.id === 'string';
                });

                if (validTodos.length === 0) {
                    throw new Error('No valid todos found');
                }

                this.showConfirmDialog(
                    'Import Todos',
                    `This will add ${validTodos.length} todo(s) to your list. Continue?`,
                    () => {
                        this.todos = [...validTodos, ...this.todos];
                        this.saveTodos();
                        this.render();
                        this.showToast('Todos imported successfully!', 'success');
                    }
                );
            } catch (error) {
                this.showToast('Failed to import! Invalid file format.', 'error');
            }
        };
        reader.readAsText(file);
        e.target.value = '';
    }

    showToast(message, type = 'info') {
        this.elements.toastMessage.textContent = message;
        this.elements.toast.className = `toast ${type}`;
        this.elements.toast.classList.remove('hidden');
        
        setTimeout(() => {
            this.elements.toast.classList.add('hidden');
        }, 3000);
    }

    showConfirmDialog(title, message, onConfirm) {
        this.elements.confirmTitle.textContent = title;
        this.elements.confirmMessage.textContent = message;
        this.elements.confirmDialog.classList.remove('hidden');
        this.confirmCallback = onConfirm;
    }

    hideConfirmDialog() {
        this.elements.confirmDialog.classList.add('hidden');
        this.confirmCallback = null;
    }

    confirmAction() {
        if (this.confirmCallback) {
            this.confirmCallback();
        }
        this.hideConfirmDialog();
    }

    handleKeyboard(e) {
        if (e.key === '?' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            this.showToast('Keyboard shortcuts: N (new), / (search), Escape (close)', 'info');
        }
        
        if (e.key === 'n' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            this.elements.todoInput.focus();
        }
        
        if (e.key === '/' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            this.elements.searchInput.focus();
        }
        
        if (e.key === 'Escape') {
            if (!this.elements.confirmDialog.classList.contains('hidden')) {
                this.hideConfirmDialog();
            } else if (this.selectedTodos.size > 0) {
                this.clearSelection();
            }
        }
    }
}

const app = new TodoApp();