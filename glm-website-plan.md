# GLM Model Pricing Website - Complete Implementation Plan

## Project Overview
Build a professional multi-page website that presents the GLM (General Language Model) similar to how Anthropic presents Claude Sonnet. The site will feature modern design, pricing information, model comparisons, and responsive layout using pure HTML, CSS, and JavaScript.

## Design Philosophy
- **Clean, minimalist aesthetic** inspired by Anthropic's design language
- **Professional color palette**: Deep navy (#1a1a2e), soft cream (#f8f9fa), accent coral (#ff6b6b), and slate grays
- **Typography**: System fonts with clear hierarchy (Inter/San Francisco/Segoe UI)
- **Smooth animations** and micro-interactions for polish
- **Mobile-first responsive design**
- **Accessibility-first** approach (WCAG AA compliant)

---

## Folder Structure

```
glm-website/
├── index.html                    # Homepage
├── pricing.html                  # Pricing page (main feature)
├── models.html                   # Models comparison page
├── about.html                    # About GLM page
├── documentation.html            # Documentation page
├── contact.html                  # Contact page
├── css/
│   ├── main.css                  # Global styles, variables, reset
│   ├── header.css                # Navigation and header styles
│   ├── footer.css                # Footer styles
│   ├── pricing.css               # Pricing-specific styles
│   ├── models.css                # Models page styles
│   └── responsive.css            # Media queries and responsive adjustments
├── js/
│   ├── main.js                   # Global JavaScript
│   ├── pricing.js                # Pricing calculator/interactivity
│   ├── models.js                 # Model comparison functionality
│   └── navigation.js             # Mobile menu, smooth scrolling
├── assets/
│   ├── images/
│   │   ├── glm-logo.svg          # GLM logo
│   │   ├── hero-bg.svg           # Hero section background
│   │   ├── model-icon.svg        # Generic model icon
│   │   └── check-icon.svg        # Checkmark for features
│   └── fonts/                    # (Optional) Custom fonts if needed
└── README.md                     # Project documentation
```

---

## Page Breakdown

### 1. **index.html** - Homepage
**Purpose**: Landing page introducing GLM with key highlights

**Sections**:
- Hero section with headline, subheadline, and CTA buttons
- Quick stats (parameters, context window, speed)
- Feature highlights (3-4 key benefits)
- Mini pricing preview (teaser)
- Testimonials/trust indicators
- Final CTA section

**Key Elements**:
```html
- Navigation header (logo + menu)
- Hero: "Meet GLM - The Next Generation Language Model"
- Stats grid: 175B parameters, 200K context, etc.
- Features section with icons
- "Get Started" and "View Pricing" CTAs
- Footer
```

---

### 2. **pricing.html** - Pricing Page (Primary Feature)
**Purpose**: Detailed pricing information similar to Anthropic's Claude pricing

**Sections**:
- Header with pricing overview
- Pricing tiers table (Free, Pro, Enterprise)
- Usage calculator (interactive)
- API pricing breakdown
- FAQ section
- Comparison with competitors

**Pricing Structure** (Mock):
```
FREE Tier:
- Price: $0/month
- Messages: 50/day
- Context: 32K tokens
- Speed: Standard

PRO Tier:
- Price: $20/month
- Messages: Unlimited
- Context: 200K tokens
- Speed: Fast
- Priority support

ENTERPRISE:
- Custom pricing
- Unlimited everything
- Dedicated support
- Custom models
```

**Interactive Elements**:
- Toggle between monthly/annual billing (20% discount)
- Usage calculator slider
- Cost estimation tool
- Tier comparison cards

**JavaScript Features**:
```javascript
- Billing toggle (monthly/annual)
- Dynamic price updates
- Usage calculator with sliders
- Cost estimator based on input/output tokens
```

---

### 3. **models.html** - Models Comparison
**Purpose**: Showcase different GLM model variants

**Sections**:
- Model overview cards
- Comparison table (GLM-Tiny, GLM-Base, GLM-Pro, GLM-Ultra)
- Performance benchmarks
- Use case recommendations
- Technical specifications

**Model Variants**:
```
GLM-Tiny:   Fast, simple tasks, 7B parameters
GLM-Base:   Balanced performance, 13B parameters
GLM-Pro:    Advanced reasoning, 70B parameters
GLM-Ultra:  Maximum capability, 175B parameters
```

**Interactive Elements**:
- Model selector dropdown
- Side-by-side comparison view
- Performance charts (simple CSS-based bar charts)

---

### 4. **about.html** - About GLM
**Purpose**: Company/mission information

**Sections**:
- Mission statement
- Team/organization info
- Research philosophy
- Safety approach
- Timeline/milestones
- Partnerships

---

### 5. **documentation.html** - Documentation
**Purpose**: Developer documentation and API reference

**Sections**:
- Quick start guide
- API reference
- Code examples (syntax highlighted)
- Rate limits
- Authentication
- SDK information

---

### 6. **contact.html** - Contact Page
**Purpose**: Contact form and information

**Sections**:
- Contact form (name, email, subject, message)
- Support email
- Business hours
- Office locations
- Social media links

---

## CSS Architecture

### **main.css** - Global Styles
```css
/* CSS Variables for consistent theming */
:root {
  --color-primary: #1a1a2e;        /* Deep navy */
  --color-secondary: #16213e;      /* Darker navy */
  --color-accent: #ff6b6b;         /* Coral accent */
  --color-accent-hover: #ff5252;
  --color-text: #2d3436;           /* Dark gray text */
  --color-text-light: #636e72;     /* Light gray text */
  --color-bg: #f8f9fa;             /* Off-white background */
  --color-white: #ffffff;
  --color-border: #dfe6e9;

  --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  --font-mono: 'SF Mono', 'Monaco', 'Inconsolata', monospace;

  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 2rem;
  --spacing-lg: 4rem;
  --spacing-xl: 6rem;

  --border-radius: 8px;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);

  --transition: all 0.3s ease;
}

/* Reset and base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-primary);
  color: var(--color-text);
  line-height: 1.6;
  background: var(--color-bg);
}

/* Typography hierarchy */
h1 { font-size: 3rem; font-weight: 700; line-height: 1.2; }
h2 { font-size: 2.5rem; font-weight: 600; }
h3 { font-size: 1.75rem; font-weight: 600; }
h4 { font-size: 1.25rem; font-weight: 600; }
```

### **header.css** - Navigation Styles
```css
/* Sticky header with blur effect */
header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
  z-index: 1000;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo */
.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Navigation menu */
nav ul {
  display: flex;
  list-style: none;
  gap: 2rem;
}

nav a {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  transition: var(--transition);
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
}

nav a:hover, nav a.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

/* Mobile menu button */
.menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
```

### **pricing.css** - Pricing Page Styles
```css
/* Pricing tiers grid */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

/* Pricing card */
.pricing-card {
  background: var(--color-white);
  border-radius: var(--border-radius);
  padding: 2.5rem;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.pricing-card.featured {
  border-color: var(--color-accent);
}

.pricing-card.featured::before {
  content: 'Most Popular';
  position: absolute;
  top: 1rem;
  right: -2.5rem;
  background: var(--color-accent);
  color: white;
  padding: 0.25rem 3rem;
  transform: rotate(45deg);
  font-size: 0.75rem;
  font-weight: 600;
}

/* Price display */
.price {
  font-size: 3.5rem;
  font-weight: 700;
  color: var(--color-primary);
  margin: 1.5rem 0;
}

.price-period {
  font-size: 1rem;
  color: var(--color-text-light);
  font-weight: 400;
}

/* Features list */
.features-list {
  list-style: none;
  margin: 2rem 0;
}

.features-list li {
  padding: 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.features-list li::before {
  content: '✓';
  color: var(--color-accent);
  font-weight: bold;
  font-size: 1.25rem;
}

/* CTA buttons */
.cta-button {
  display: inline-block;
  padding: 1rem 2rem;
  background: var(--color-primary);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  transition: var(--transition);
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: center;
}

.cta-button:hover {
  background: var(--color-secondary);
  transform: translateY(-2px);
}

.cta-button.secondary {
  background: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.cta-button.secondary:hover {
  background: var(--color-primary);
  color: white;
}

/* Billing toggle */
.billing-toggle {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 2rem 0;
}

.toggle-switch {
  position: relative;
  width: 60px;
  height: 30px;
  background: var(--color-border);
  border-radius: 30px;
  cursor: pointer;
  transition: var(--transition);
}

.toggle-switch.active {
  background: var(--color-accent);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  transition: var(--transition);
}

.toggle-switch.active::after {
  left: 33px;
}

.discount-badge {
  background: var(--color-accent);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 600;
}
```

### **models.css** - Models Page Styles
```css
/* Model cards */
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.model-card {
  background: var(--color-white);
  border-radius: var(--border-radius);
  padding: 2rem;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
  cursor: pointer;
  border: 2px solid transparent;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.model-card.selected {
  border-color: var(--color-accent);
}

.model-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.model-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.model-description {
  color: var(--color-text-light);
  margin-bottom: 1.5rem;
}

/* Specs grid */
.specs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.spec-item {
  background: var(--color-bg);
  padding: 0.75rem;
  border-radius: 4px;
}

.spec-label {
  font-size: 0.75rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.spec-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-primary);
}

/* Comparison table */
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  margin: 3rem 0;
  background: var(--color-white);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.comparison-table th,
.comparison-table td {
  padding: 1.25rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.comparison-table th {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
}

.comparison-table tr:hover {
  background: rgba(0,0,0,0.02);
}
```

### **responsive.css** - Media Queries
```css
/* Tablet */
@media (max-width: 768px) {
  h1 { font-size: 2.5rem; }
  h2 { font-size: 2rem; }

  .pricing-grid {
    grid-template-columns: 1fr;
  }

  nav ul {
    display: none;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    padding: 1rem;
    box-shadow: var(--shadow-lg);
  }

  nav ul.active {
    display: flex;
  }

  .menu-toggle {
    display: block;
  }
}

/* Mobile */
@media (max-width: 480px) {
  h1 { font-size: 2rem; }
  h2 { font-size: 1.75rem; }

  .pricing-card {
    padding: 1.5rem;
  }

  .price {
    font-size: 2.5rem;
  }

  .specs-grid {
    grid-template-columns: 1fr;
  }

  .comparison-table {
    font-size: 0.875rem;
  }

  .comparison-table th,
  .comparison-table td {
    padding: 0.75rem;
  }
}
```

---

## JavaScript Functionality

### **main.js** - Global Scripts
```javascript
// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Add active class to current page navigation
const currentPage = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('nav a').forEach(link => {
  if (link.getAttribute('href') === currentPage) {
    link.classList.add('active');
  }
});

// Intersection Observer for fade-in animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in');
    }
  });
}, observerOptions);

document.querySelectorAll('.pricing-card, .model-card, section').forEach(el => {
  observer.observe(el);
});
```

### **pricing.js** - Pricing Calculator
```javascript
// Pricing data
const pricingData = {
  monthly: {
    free: 0,
    pro: 20,
    enterprise: null
  },
  annual: {
    free: 0,
    pro: 16,  // 20% discount
    enterprise: null
  }
};

// Billing toggle functionality
const billingToggle = document.querySelector('.toggle-switch');
let isAnnual = false;

billingToggle?.addEventListener('click', () => {
  isAnnual = !isAnnual;
  billingToggle.classList.toggle('active', isAnnual);
  updatePrices();
});

function updatePrices() {
  const period = isAnnual ? 'annual' : 'monthly';
  document.querySelectorAll('.pricing-card').forEach(card => {
    const tier = card.dataset.tier;
    const price = pricingData[period][tier];
    const priceElement = card.querySelector('.price');
    const periodElement = card.querySelector('.price-period');

    if (price !== null) {
      priceElement.textContent = `$${price}`;
      periodElement.textContent = isAnnual ? '/month (billed annually)' : '/month';
    }
  });
}

// Usage calculator
const inputSlider = document.querySelector('#input-slider');
const outputSlider = document.querySelector('#output-slider');
const costDisplay = document.querySelector('#estimated-cost');

function calculateCost() {
  const inputTokens = parseInt(inputSlider.value);
  const outputTokens = parseInt(outputSlider.value);

  // Mock pricing: $3 per million input tokens, $15 per million output tokens
  const inputCost = (inputTokens / 1000000) * 3;
  const outputCost = (outputTokens / 1000000) * 15;
  const totalCost = inputCost + outputCost;

  costDisplay.textContent = `$${totalCost.toFixed(2)}`;
}

[inputSlider, outputSlider].forEach(slider => {
  slider?.addEventListener('input', calculateCost);
});
```

### **models.js** - Model Comparison
```javascript
// Model selection
const modelCards = document.querySelectorAll('.model-card');

modelCards.forEach(card => {
  card.addEventListener('click', () => {
    modelCards.forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    updateComparison(card.dataset.model);
  });
});

function updateComparison(modelId) {
  // Update comparison table or details view
  const modelData = {
    'glm-tiny': { params: '7B', context: '32K', speed: '150+ tok/s' },
    'glm-base': { params: '13B', context: '128K', speed: '100+ tok/s' },
    'glm-pro': { params: '70B', context: '200K', speed: '50+ tok/s' },
    'glm-ultra': { params: '175B', context: '200K', speed: '30+ tok/s' }
  };

  const data = modelData[modelId];
  if (data) {
    document.querySelector('#compare-params').textContent = data.params;
    document.querySelector('#compare-context').textContent = data.context;
    document.querySelector('#compare-speed').textContent = data.speed;
  }
}

// Simple bar chart for performance
function renderPerformanceChart() {
  const chartData = [
    { model: 'GLM-Tiny', score: 65 },
    { model: 'GLM-Base', score: 78 },
    { model: 'GLM-Pro', score: 89 },
    { model: 'GLM-Ultra', score: 96 }
  ];

  const chartContainer = document.querySelector('#performance-chart');
  if (!chartContainer) return;

  chartContainer.innerHTML = chartData.map(item => `
    <div class="chart-bar">
      <div class="bar-label">${item.model}</div>
      <div class="bar-fill" style="width: ${item.score}%"></div>
      <div class="bar-value">${item.score}%</div>
    </div>
  `).join('');
}
```

### **navigation.js** - Mobile Navigation
```javascript
// Mobile menu toggle
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('nav ul');

menuToggle?.addEventListener('click', () => {
  navMenu.classList.toggle('active');
  menuToggle.textContent = navMenu.classList.contains('active') ? '✕' : '☰';
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('header')) {
    navMenu?.classList.remove('active');
    menuToggle.textContent = '☰';
  }
});

// Sticky header shadow on scroll
const header = document.querySelector('header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    header.style.boxShadow = 'var(--shadow-md)';
  } else {
    header.style.boxShadow = 'none';
  }
});
```

---

## Implementation Steps

### Phase 1: Foundation Setup
1. Create project folder structure
2. Set up all HTML files with basic structure
3. Create main.css with CSS variables and reset
4. Build header and footer components
5. Implement responsive navigation

### Phase 2: Homepage (index.html)
1. Build hero section with headline and CTAs
2. Create stats grid component
3. Add features section
4. Implement testimonial section
5. Add final CTA section

### Phase 3: Pricing Page (pricing.html)
1. Create pricing tier cards
2. Build comparison table
3. Implement billing toggle
4. Create usage calculator with sliders
5. Add FAQ section with accordion
6. Build cost estimator tool

### Phase 4: Models Page (models.html)
1. Create model cards for each variant
2. Build comparison table
3. Implement model selection functionality
4. Add performance charts (CSS-based)
5. Create use case recommendations

### Phase 5: Additional Pages
1. Build about.html with mission and team info
2. Create documentation.html with code examples
3. Implement contact.html with form
4. Add form validation

### Phase 6: JavaScript & Interactivity
1. Implement all navigation features
2. Add smooth scrolling
3. Create pricing calculator
4. Build model comparison functionality
5. Add form validation for contact page
6. Implement intersection observer animations

### Phase 7: Polish & Testing
1. Add hover effects and transitions
2. Implement loading states
3. Test all responsive breakpoints
4. Verify accessibility (ARIA labels, keyboard navigation)
5. Cross-browser testing
6. Performance optimization

---

## Responsive Design Breakpoints

```css
/* Mobile First Approach */
/* Base styles: 320px+ */

/* Small devices: 480px */
@media (min-width: 480px) {
  /* Adjust spacing, font sizes */
}

/* Tablets: 768px */
@media (min-width: 768px) {
  /* Two-column layouts, larger navigation */
}

/* Laptops: 1024px */
@media (min-width: 1024px) {
  /* Three-column layouts, full features */
}

/* Desktops: 1280px */
@media (min-width: 1280px) {
  /* Maximum width containers, enhanced spacing */
}
```

---

## Accessibility Features

- Semantic HTML5 elements (`<nav>`, `<main>`, `<section>`, `<article>`)
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators for all interactive elements
- Color contrast ratios meeting WCAG AA (4.5:1)
- Alt text for all images
- Skip to main content link
- Form labels and error messages
- Responsive text sizing using `rem` units

---

## Performance Considerations

- Lazy loading for images below the fold
- CSS animations using `transform` and `opacity` (GPU-accelerated)
- Minimal JavaScript (no frameworks)
- System fonts for faster loading
- Optimized SVG icons
- CSS variables for easy theming
- Efficient event delegation

---

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Testing Checklist

- [ ] All pages render correctly at all breakpoints
- [ ] Navigation works on all pages
- [ ] Pricing calculator updates correctly
- [ ] Model comparison functions properly
- [ ] Form validation works
- [ ] All links are functional
- [ ] Smooth scrolling works
- [ ] Mobile menu toggles correctly
- [ ] Hover states work on desktop
- [ ] Animations are smooth
- [ ] No console errors
- [ ] Accessibility audit passes
- [ ] Cross-browser testing complete

---

## Success Criteria

1. **Visual Design**: Professional, modern aesthetic matching Anthropic's style
2. **Functionality**: All interactive elements work correctly
3. **Responsiveness**: Seamless experience from 320px to 1920px+
4. **Performance**: Fast load times (<2s on 3G)
5. **Accessibility**: WCAG AA compliant
6. **Code Quality**: Clean, semantic, maintainable code
7. **Browser Support**: Works on all modern browsers

---

## Notes

- Use SVG icons for scalability
- Implement CSS Grid for complex layouts
- Use Flexbox for component layouts
- Keep JavaScript modular and organized
- Add comments for complex logic
- Use meaningful class names (BEM methodology preferred)
- Test on real devices, not just browser dev tools
