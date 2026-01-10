export class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }
    
    init() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    register(keyCombo, callback, description = '') {
        this.shortcuts.set(keyCombo, { callback, description });
    }
    
    handleKeyDown(e) {
        const keyCombo = this.getKeyCombo(e);
        
        if (this.shortcuts.has(keyCombo)) {
            e.preventDefault();
            const { callback } = this.shortcuts.get(keyCombo);
            callback(e);
        }
    }
    
    getKeyCombo(e) {
        const parts = [];
        
        if (e.ctrlKey) parts.push('ctrl');
        if (e.metaKey) parts.push('meta');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        
        parts.push(e.key.toLowerCase());
        
        return parts.join('+');
    }
    
    getShortcutsList() {
        return Array.from(this.shortcuts.entries()).map(([key, value]) => ({
            key,
            description: value.description
        }));
    }
}