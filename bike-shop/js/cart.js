class Cart {
  constructor() {
    this.items = this.loadCart();
    this.coupon = null;
    this.shippingMethod = 'standard';
    this.init();
  }

  init() {
    this.updateCartCount();
    this.bindEvents();
  }

  loadCart() {
    const savedCart = localStorage.getItem('bikeShopCart');
    return savedCart ? JSON.parse(savedCart) : [];
  }

  saveCart() {
    localStorage.setItem('bikeShopCart', JSON.stringify(this.items));
    this.updateCartCount();
  }

  addItem(product, quantity = 1, size = null, color = null) {
    const existingItem = this.items.find(item => 
      item.productId === product.id && 
      item.size === size && 
      item.color === color
    );

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      this.items.push({
        productId: product.id,
        name: product.name,
        brand: product.brand,
        price: product.salePrice || product.price,
        image: product.images[0],
        quantity: quantity,
        size: size,
        color: color,
        addedAt: new Date().toISOString()
      });
    }

    this.saveCart();
    this.showNotification('Product added to cart!');
  }

  removeItem(index) {
    this.items.splice(index, 1);
    this.saveCart();
  }

  updateQuantity(index, quantity) {
    if (quantity <= 0) {
      this.removeItem(index);
    } else {
      this.items[index].quantity = quantity;
      this.saveCart();
    }
  }

  getSubtotal() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  getShippingCost() {
    const subtotal = this.getSubtotal();
    if (subtotal >= 1000) return 0;
    if (this.shippingMethod === 'express') return 49.99;
    return 19.99;
  }

  getTax() {
    return this.getSubtotal() * 0.08;
  }

  getTotal() {
    return this.getSubtotal() + this.getShippingCost() + this.getTax();
  }

  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  updateCartCount() {
    const count = this.getItemCount();
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(el => {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  }

  clear() {
    this.items = [];
    this.coupon = null;
    this.saveCart();
  }

  bindEvents() {
    document.addEventListener('click', (e) => {
      if (e.target.closest('.add-to-cart-btn')) {
        const btn = e.target.closest('.add-to-cart-btn');
        const productId = parseInt(btn.dataset.productId);
        this.handleAddToCart(productId);
      }
    });
  }

  async handleAddToCart(productId) {
    try {
      const response = await fetch('data/products.json');
      const data = await response.json();
      const product = data.products.find(p => p.id === productId);
      
      if (product) {
        const size = document.querySelector('.size-selector.active')?.dataset.size || null;
        const color = document.querySelector('.color-selector.active')?.dataset.color || null;
        const quantity = parseInt(document.querySelector('.quantity-selector')?.value) || 1;
        
        this.addItem(product, quantity, size, color);
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  }

  showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 100px;
      right: 20px;
      background: var(--success);
      color: white;
      padding: 15px 25px;
      border-radius: 4px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

const cart = new Cart();