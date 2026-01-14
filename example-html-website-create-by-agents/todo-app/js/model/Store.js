const STORAGE_KEY = 'todo-app-data';
const STORAGE_VERSION = '1.0';

export class Store {
    constructor() {
        this.data = this.load();
    }
    
    load() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) {
                return this.getInitialData();
            }
            
            const parsed = JSON.parse(stored);
            
            if (parsed.version !== STORAGE_VERSION) {
                return this.migrateData(parsed);
            }
            
            return parsed;
        } catch (error) {
            console.error('Error loading data:', error);
            return this.getInitialData();
        }
    }
    
    save() {
        try {
            const serialized = JSON.stringify(this.data);
            localStorage.setItem(STORAGE_KEY, serialized);
            return true;
        } catch (error) {
            console.error('Error saving data:', error);
            if (error.name === 'QuotaExceededError') {
                throw new Error('Storage quota exceeded. Please export your data and clear some tasks.');
            }
            return false;
        }
    }
    
    getInitialData() {
        return {
            version: STORAGE_VERSION,
            tasks: [],
            categories: this.getDefaultCategories(),
            settings: {
                theme: 'light',
                sortBy: 'created'
            }
        };
    }
    
    getDefaultCategories() {
        return [
            { id: 'work', name: 'Work', color: '#3B82F6', icon: '💼' },
            { id: 'personal', name: 'Personal', color: '#10B981', icon: '👤' },
            { id: 'shopping', name: 'Shopping', color: '#F59E0B', icon: '🛒' },
            { id: 'health', name: 'Health', color: '#EF4444', icon: '❤️' }
        ];
    }
    
    migrateData(oldData) {
        console.log('Migrating data from version:', oldData.version);
        
        const migrated = this.getInitialData();
        migrated.tasks = oldData.tasks || [];
        migrated.categories = oldData.categories || migrated.categories;
        migrated.settings = oldData.settings || migrated.settings;
        
        this.save();
        return migrated;
    }
    
    getTasks() {
        return this.data.tasks;
    }
    
    getCategories() {
        return this.data.categories;
    }
    
    getSettings() {
        return this.data.settings;
    }
    
    addTask(task) {
        this.data.tasks.push(task);
        this.save();
        this.notifyListeners();
    }
    
    updateTask(taskId, updates) {
        const index = this.data.tasks.findIndex(t => t.id === taskId);
        if (index !== -1) {
            Object.assign(this.data.tasks[index], updates);
            this.save();
            this.notifyListeners();
        }
    }
    
    deleteTask(taskId) {
        this.data.tasks = this.data.tasks.filter(t => t.id !== taskId);
        this.save();
        this.notifyListeners();
    }
    
    addCategory(category) {
        this.data.categories.push(category);
        this.save();
        this.notifyListeners();
    }
    
    deleteCategory(categoryId) {
        this.data.categories = this.data.categories.filter(c => c.id !== categoryId);
        this.data.tasks.forEach(task => {
            if (task.category === categoryId) {
                task.category = 'default';
            }
        });
        this.save();
        this.notifyListeners();
    }
    
    updateSettings(newSettings) {
        this.data.settings = { ...this.data.settings, ...newSettings };
        this.save();
    }
    
    exportData() {
        const dataStr = JSON.stringify(this.data, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `todo-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    importData(jsonString) {
        try {
            const imported = JSON.parse(jsonString);
            
            if (!imported.tasks || !Array.isArray(imported.tasks)) {
                throw new Error('Invalid data format');
            }
            
            this.data = {
                version: STORAGE_VERSION,
                tasks: imported.tasks || [],
                categories: imported.categories || this.getDefaultCategories(),
                settings: imported.settings || this.data.settings
            };
            
            this.save();
            this.notifyListeners();
            return true;
        } catch (error) {
            console.error('Import error:', error);
            throw new Error('Failed to import data. Please check the file format.');
        }
    }
    
    clearAll() {
        this.data = this.getInitialData();
        this.save();
        this.notifyListeners();
    }
    
    notifyListeners() {
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new Event('storage'));
        }
    }
}