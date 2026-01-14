export class FilterController {
    constructor() {
        this.currentFilter = 'all';
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.sortBy = 'created';
    }
    
    setFilter(filter) {
        this.currentFilter = filter;
    }
    
    setCategory(category) {
        this.currentCategory = category;
    }
    
    setSearchQuery(query) {
        this.searchQuery = query;
    }
    
    setSortBy(sortBy) {
        this.sortBy = sortBy;
    }
    
    getFilterState() {
        return {
            filter: this.currentFilter,
            category: this.currentCategory,
            searchQuery: this.searchQuery,
            sortBy: this.sortBy
        };
    }
    
    reset() {
        this.currentFilter = 'all';
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.sortBy = 'created';
    }
}