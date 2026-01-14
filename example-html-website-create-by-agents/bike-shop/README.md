# BikeHub - E-Commerce Bike Shop Website

A modern, fully functional e-commerce website for a bike shop built with pure HTML, CSS, and JavaScript (no frameworks).

## 🚴 Features

### Complete E-Commerce Functionality
- **Product Catalog**: 8 sample products across 5 categories (Road, Mountain, Hybrid, Electric, Kids)
- **Shopping Cart System**: Add, remove, update quantities with localStorage persistence
- **Product Filtering**: Filter by category, brand, and price range
- **Product Sorting**: Sort by featured, price, name, and newest
- **Search Functionality**: Real-time product search
- **Multi-Step Checkout**: Contact, shipping, and payment information
- **Order Summary**: Real-time cart totals with shipping and tax calculation

### Pages Included
1. **Home** (`index.html`) - Hero section, categories, featured products, testimonials
2. **Shop** (`shop.html`) - Full product catalog with filters and sorting
3. **Cart** (`cart.html`) - Shopping cart with item management
4. **Checkout** (`checkout.html`) - Multi-step checkout process
5. **About** (placeholder) - Company information
6. **Services** (placeholder) - Service offerings
7. **Contact** (placeholder) - Contact form and information

### Technical Features
- **Responsive Design**: Mobile-first approach with breakpoints
- **Modern CSS**: CSS Grid, Flexbox, CSS Variables, Animations
- **Vanilla JavaScript**: ES6+ features, no frameworks
- **localStorage**: Cart persistence across sessions
- **Form Validation**: Real-time validation with error handling
- **Smooth Animations**: Fade-in effects, hover states, transitions

## 📁 Project Structure

```
bike-shop/
├── index.html              # Home page
├── shop.html               # Product catalog
├── cart.html               # Shopping cart
├── checkout.html           # Checkout process
├── about.html              # About page (placeholder)
├── services.html           # Services page (placeholder)
├── contact.html            # Contact page (placeholder)
├── README.md               # This file
├── css/
│   ├── style.css           # Main styles
│   ├── components.css      # Reusable components
│   └── responsive.css      # Media queries
├── js/
│   ├── main.js             # Core functionality
│   ├── cart.js             # Shopping cart system
│   └── products.js         # Product management
└── data/
    └── products.json       # Product database
```

## 🎨 Design System

### Color Palette
- **Primary**: #E63946 (Vibrant Red)
- **Secondary**: #1D3557 (Navy Blue)
- **Accent**: #457B9D (Medium Blue)
- **Success**: #28A745
- **Warning**: #FFC107
- **Danger**: #DC3545

### Typography
- **Headings**: Poppins (Google Fonts)
- **Body**: Inter (Google Fonts)
- **Prices**: Roboto Mono (monospace)

### Components
- Buttons (Primary, Secondary, Outline)
- Product Cards with hover effects
- Forms with validation states
- Badges and tags
- Modal system
- Accordion components

## 🛠️ Setup & Installation

1. **Clone or download** the project
2. **Open** `index.html` in a web browser
3. **No build process required** - pure HTML/CSS/JS

### Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No server required (works locally)
- No dependencies to install

## 💡 Usage

### Shopping Cart
The cart system uses localStorage to persist items across sessions:
- Add items from the shop page
- Update quantities in the cart
- Remove items
- Cart persists even after closing the browser

### Product Management
Products are stored in `data/products.json` with the following structure:
```json
{
  "id": 1,
  "name": "Product Name",
  "brand": "Brand Name",
  "category": "road",
  "price": 1299.99,
  "salePrice": null,
  "description": "Short description",
  "images": ["image1.jpg", "image2.jpg"],
  "sizes": ["S", "M", "L", "XL"],
  "colors": ["Red", "Blue"],
  "stock": 15,
  "rating": 4.5,
  "reviewCount": 28,
  "featured": true,
  "new": true
}
```

### Adding New Products
1. Open `data/products.json`
2. Add a new product object following the structure above
3. Save the file
4. Refresh the shop page

## 🎯 Key Features Explained

### Cart System (`js/cart.js`)
- `addItem()` - Add product to cart
- `removeItem()` - Remove item from cart
- `updateQuantity()` - Update item quantity
- `getSubtotal()` - Calculate subtotal
- `getShippingCost()` - Calculate shipping
- `getTax()` - Calculate tax
- `getTotal()` - Calculate total
- `saveCart()` - Persist to localStorage
- `loadCart()` - Load from localStorage

### Product System (`js/products.js`)
- `loadProducts()` - Load products from JSON
- `applyFilters()` - Filter products
- `sortProducts()` - Sort products
- `renderProducts()` - Render product cards
- `createProductCard()` - Generate HTML for product card
- `getPaginatedProducts()` - Pagination support

### Main Functionality (`js/main.js`)
- Mobile navigation toggle
- Scroll animations
- Counter animations
- Form validation
- Accordion functionality
- Newsletter signup

## 📱 Responsive Breakpoints

- **Mobile**: < 576px
- **Tablet**: 576px - 992px
- **Desktop**: 992px - 1200px
- **Large**: > 1200px

## 🔧 Customization

### Changing Colors
Edit CSS variables in `css/style.css`:
```css
:root {
  --primary-color: #E63946;
  --secondary-color: #1D3557;
  --accent-color: #457B9D;
}
```

### Adding Pages
1. Create new HTML file in root directory
2. Include CSS files in `<head>`
3. Include JS files before `</body>`
4. Use existing components (header, footer)

### Modifying Products
Edit `data/products.json` to:
- Add new products
- Update prices
- Change images
- Modify categories

## 🚀 Future Enhancements

- User accounts and authentication
- Order history
- Product reviews and ratings
- Wishlist functionality
- Advanced search with autocomplete
- Product comparison
- Email notifications
- Payment gateway integration (Stripe, PayPal)
- Admin panel for product management
- Inventory management
- Analytics integration

## 📄 License

Free to use for personal and commercial projects.

## 👨‍💻 Development

Built with modern web standards:
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with Grid and Flexbox
- **JavaScript ES6+** - Modern syntax and features
- **localStorage API** - Client-side storage
- **Fetch API** - AJAX requests

## 🐛 Known Limitations

- No backend integration (demo only)
- No real payment processing
- No user authentication
- No email functionality
- Products loaded from JSON (not database)
- No inventory management

## 📞 Support

For questions or issues, please refer to the code comments or create an issue in the repository.

---

**Built with ❤️ for cyclists everywhere!**

Enjoy your new bike shop website! 🚴‍♂️🛒