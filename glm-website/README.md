# GLM Website

A professional multi-page website for GLM (General Language Model), inspired by Anthropic's Claude Sonnet presentation. Built with pure HTML, CSS, and JavaScript - no frameworks required.

## 📁 Project Structure

```
glm-website/
├── index.html                    # Homepage
├── pricing.html                  # Pricing page
├── models.html                   # Models comparison
├── about.html                    # About page
├── documentation.html            # Documentation
├── contact.html                  # Contact page
├── css/
│   ├── main.css                  # Global styles
│   ├── header.css                # Navigation
│   ├── footer.css                # Footer
│   ├── pricing.css               # Pricing styles
│   ├── models.css                # Models styles
│   └── responsive.css            # Media queries
├── js/
│   ├── main.js                   # Global JS
│   ├── pricing.js                # Pricing calculator
│   ├── models.js                 # Model comparison
│   └── navigation.js             # Mobile menu
├── assets/
│   └── images/
│       ├── glm-logo.svg          # Logo
│       ├── check-icon.svg        # Checkmark
│       └── model-icon.svg        # Model icon
└── README.md                     # This file
```

## 🎨 Features

### Pages
- **Homepage**: Hero section, stats, features, testimonials
- **Pricing**: 3-tier pricing, billing toggle, usage calculator
- **Models**: 4 GLM variants, comparison table, performance charts
- **About**: Mission, values, team, timeline
- **Documentation**: API reference, code examples, quick start
- **Contact**: Contact form, info, locations

### Interactive Features
- ✅ Mobile-responsive navigation with hamburger menu
- ✅ Monthly/annual billing toggle (20% discount)
- ✅ Usage calculator with real-time cost estimation
- ✅ Model comparison with interactive cards
- ✅ Smooth scrolling and fade-in animations
- ✅ Form validation
- ✅ Performance benchmark charts

### Design
- 🎨 Professional color palette (navy, coral accent)
- 📱 Mobile-first responsive design
- ♿ WCAG AA compliant accessibility
- 🌐 Cross-browser compatible
- ⚡ Fast loading (no frameworks)

## 🚀 Getting Started

### Option 1: Open Directly
Simply open `index.html` in your web browser.

### Option 2: Local Server
For best results, use a local server:

```bash
# Python 3
python -m http.server 8000

# Node.js (with npx)
npx serve

# PHP
php -S localhost:8000
```

Then visit `http://localhost:8000`

## 📱 Responsive Breakpoints

- **Mobile**: < 480px
- **Small**: 480px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1280px
- **Large**: > 1280px

## 🎯 Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🔧 Customization

### Colors
Edit CSS variables in `css/main.css`:

```css
:root {
  --color-primary: #1a1a2e;
  --color-accent: #ff6b6b;
  /* ... more variables */
}
```

### Pricing
Update pricing data in `js/pricing.js`:

```javascript
const pricingData = {
  monthly: {
    free: 0,
    pro: 20,
    enterprise: null
  },
  // ...
};
```

### Models
Modify model specs in `js/models.js`:

```javascript
const modelData = {
  'glm-tiny': {
    params: '7B',
    context: '32K',
    // ...
  },
  // ...
};
```

## 📄 License

This project is open source and available for use.

## 🙏 Acknowledgments

- Design inspired by Anthropic's Claude website
- Built with modern web standards
- No external frameworks or dependencies
