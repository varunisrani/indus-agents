import { Category } from '../model/Category.js';
import { Renderer } from '../view/Renderer.js';

export class CategoryController {
    constructor(store, categoryView) {
        this.store = store;
        this.categoryView = categoryView;
        this.onCategoriesChange = null;
    }
    
    addCategory(name) {
        const category = new Category({ name });
        this.store.addCategory(category.toJSON());
        this.notifyChange();
        Renderer.showNotification('Category added successfully', 'success');
        return category;
    }
    
    deleteCategory(categoryId) {
        if (categoryId === 'all') {
            Renderer.showNotification('Cannot delete "All Tasks" category', 'error');
            return;
        }
        
        const categories = this.store.getCategories();
        const category = categories.find(c => c.id === categoryId);
        
        if (category) {
            const taskCount = this.store.getTasks().filter(t => t.category === categoryId).length;
            const message = taskCount > 0 
                ? `Category "${category.name}" deleted. ${taskCount} task(s) moved to default.`
                : `Category "${category.name}" deleted.`;
            
            this.store.deleteCategory(categoryId);
            this.notifyChange();
            Renderer.showNotification(message, 'success');
        }
    }
    
    getCategories() {
        return this.store.getCategories();
    }
    
    notifyChange() {
        if (this.onCategoriesChange) {
            this.onCategoriesChange();
        }
    }
}