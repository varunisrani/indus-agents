import { Renderer } from './Renderer.js';

export class CategoryView {
    constructor(categoryListElement) {
        this.categoryListElement = categoryListElement;
    }
    
    renderCategories(categories, tasks, currentCategory = 'all') {
        const allItem = this.categoryListElement.querySelector('[data-category="all"]');
        if (allItem) {
            const countSpan = allItem.querySelector('.category-count');
            if (countSpan) {
                countSpan.textContent = tasks.length;
            }
        }
        
        categories.forEach(category => {
            let categoryItem = this.categoryListElement.querySelector(`[data-category="${category.id}"]`);
            
            if (!categoryItem) {
                categoryItem = this.createCategoryElement(category);
                this.categoryListElement.appendChild(categoryItem);
            }
            
            const count = tasks.filter(t => t.category === category.id).length;
            const countSpan = categoryItem.querySelector('.category-count');
            if (countSpan) {
                countSpan.textContent = count;
            }
            
            if (category.id === currentCategory) {
                categoryItem.classList.add('active');
                categoryItem.querySelector('.category-button')?.setAttribute('aria-current', 'page');
            } else {
                categoryItem.classList.remove('active');
                categoryItem.querySelector('.category-button')?.removeAttribute('aria-current');
            }
        });
    }
    
    createCategoryElement(category) {
        const li = Renderer.createElement('li', 'category-item');
        li.dataset.category = category.id;
        
        const button = Renderer.createElement('button', 'category-button');
        button.innerHTML = `
            <span class="category-icon">${category.icon}</span>
            <span class="category-name">${category.name}</span>
            <span class="category-count">0</span>
        `;
        button.setAttribute('aria-label', `Filter by ${category.name}`);
        
        li.appendChild(button);
        
        return li;
    }
    
    updateCategorySelect(categories, selectElement) {
        selectElement.innerHTML = '<option value="">Select Category</option>';
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = `${category.icon} ${category.name}`;
            selectElement.appendChild(option);
        });
    }
    
    setActiveCategory(categoryId) {
        this.categoryListElement.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
            item.querySelector('.category-button')?.removeAttribute('aria-current');
        });
        
        const activeItem = this.categoryListElement.querySelector(`[data-category="${categoryId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
            activeItem.querySelector('.category-button')?.setAttribute('aria-current', 'page');
        }
    }
    
    removeCategoryElement(categoryId) {
        const element = this.categoryListElement.querySelector(`[data-category="${categoryId}"]`);
        if (element) {
            element.remove();
        }
    }
}