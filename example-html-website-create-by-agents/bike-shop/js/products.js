class Products {
  constructor() {
    this.products = [];
    this.filteredProducts = [];
    this.filters = {
      category: 'all',
      priceRange: 'all',
      brand: 'all',
      search: ''
    };
    this.sortBy = 'featured';
    this.currentPage = 1;
    this.itemsPerPage = 12;
    this.init();
  }

  async init() {
    await this.loadProducts();
    this.bindEvents();
  }

  async loadProducts() {
    try {
      const response = await fetch('data/products.json');
      const data = await response.json();
      this.products = data.products;
      this.filteredProducts = [...this.products];
    } catch (error) {
      console.error('Error loading products:', error);
    }
  }

  applyFilters() {
    this.filteredProducts = this.products.filter(product => {
      if (this.filters.category !== 'all' && product.category !== this.filters.category) {
        return false;
      }
      if (this.filters.brand !== 'all' && product.brand !== this.filters.brand) {
        return false;
      }
      if (this.filters.search) {
        const search = this.filters.search.toLowerCase();
        return product.name.toLowerCase().includes(search) ||
               product.brand.toLowerCase().includes(search) ||
               product.description.toLowerCase().includes(search);
      }
      return true;
    });

    this.sortProducts();
  }

  sortProducts() {
    switch (this.sortBy) {
      case 'price-low':
        this.filteredProducts.sort((a, b) => (a.salePrice || a.price) - (b.salePrice || b.price));
        break;
      case 'price-high':
        this.filteredProducts.sort((a, b) => (b.salePrice || b.price) - (a.salePrice || a.price));
        break;
      case 'name':
        this.filteredProducts.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'new':
        this.filteredProducts.sort((a, b) => b.new - a.new);
        break;
      default:
        this.filteredProducts.sort((a, b) => b.featured - a.featured);
    }
  }

  getPaginatedProducts() {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.filteredProducts.slice(start, end);
  }

  getTotalPages() {
    return Math.ceil(this.filteredProducts.length / this.itemsPerPage);
  }

  renderProducts(container) {
    const products = this.getPaginatedProducts();
    
    if (products.length === 0) {
      container.innerHTML = `
        <div class="no-results">
          <h3>No products found</h3>
          <p>Try adjusting your filters or search terms</p>
        </div>
      `;
      return;
    }

    container.innerHTML = products.map(product => this.createProductCard(product)).join('');
  }

  createProductCard(product) {
    const salePrice = product.salePrice ? 
      `<span class="price-original">$${product.price.toFixed(2)}</span>` : '';
    
    const badges = [];
    if (product.new) badges.push('<span class="badge badge-new">New</span>');
    if (product.salePrice) badges.push('<span class="badge badge-sale">Sale</span>');
    if (product.stock < 5) badges.push('<span class="badge badge-low-stock">Low Stock</span>');

    const stars = this.createStarRating(product.rating);

    return `
      <div class="product-card" data-product-id="${product.id}">
        <div class="product-image">
          <img src="${product.images[0]}" alt="${product.name}" loading="lazy">
          <div class="product-badges">
            ${badges.join('')}
          </div>
          <div class="product-actions">
            <button class="action-btn wishlist-btn" data-product-id="${product.id}" title="Add to Wishlist">
              <i class="far fa-heart"></i>
            </button>
            <button class="action-btn quick-view-btn" data-product-id="${product.id}" title="Quick View">
              <i class="far fa-eye"></i>
            </button>
          </div>
        </div>
        <div class="product-info">
          <div class="product-category">${product.category}</div>
          <h3 class="product-title">
            <a href="product-detail.html?id=${product.id}">${product.name}</a>
          </h3>
          <div class="product-brand">${product.brand}</div>
          <div class="product-rating">
            <div class="rating">${stars}</div>
            <span class="review-count">(${product.reviewCount})</span>
          </div>
          <div class="product-price">
            ${salePrice}
            <span class="price">$${(product.salePrice || product.price).toFixed(2)}</span>
          </div>
          <div class="product-buttons">
            <button class="btn btn-primary add-to-cart-btn" data-product-id="${product.id}">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    `;
  }

  createStarRating(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
      if (i <= Math.floor(rating)) {
        stars += '<i class="fas fa-star"></i>';
      } else if (i - 0.5 <= rating) {
        stars += '<i class="fas fa-star-half-alt"></i>';
      } else {
        stars += '<i class="far fa-star"></i>';
      }
    }
    return stars;
  }

  bindEvents() {
    document.addEventListener('change', (e) => {
      if (e.target.matches('.filter-category')) {
        this.filters.category = e.target.value;
        this.currentPage = 1;
        this.applyFilters();
        this.refreshProducts();
      }
      if (e.target.matches('.filter-brand')) {
        this.filters.brand = e.target.value;
        this.currentPage = 1;
        this.applyFilters();
        this.refreshProducts();
      }
      if (e.target.matches('.sort-select')) {
        this.sortBy = e.target.value;
        this.applyFilters();
        this.refreshProducts();
      }
      if (e.target.matches('.search-input')) {
        this.filters.search = e.target.value;
        this.currentPage = 1;
        this.applyFilters();
        this.refreshProducts();
      }
    });
  }

  refreshProducts() {
    const container = document.querySelector('.products-grid');
    if (container) {
      this.renderProducts(container);
      this.updateResultsCount();
      this.renderPagination();
    }
  }

  updateResultsCount() {
    const countElement = document.querySelector('.results-count');
    if (countElement) {
      countElement.textContent = `${this.filteredProducts.length} products`;
    }
  }

  renderPagination() {
    const container = document.querySelector('.pagination');
    if (!container) return;

    const totalPages = this.getTotalPages();
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    let pagination = '<div class="pagination-controls">';
    
    if (this.currentPage > 1) {
      pagination += `<button class="btn btn-outline" data-page="${this.currentPage - 1}">Previous</button>`;
    }

    for (let i = 1; i <= totalPages; i++) {
      const active = i === this.currentPage ? 'active' : '';
      pagination += `<button class="btn btn-outline ${active}" data-page="${i}">${i}</button>`;
    }

    if (this.currentPage < totalPages) {
      pagination += `<button class="btn btn-outline" data-page="${this.currentPage + 1}">Next</button>`;
    }

    pagination += '</div>';
    container.innerHTML = pagination;

    container.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentPage = parseInt(btn.dataset.page);
        this.refreshProducts();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    });
  }
}

const products = new Products();