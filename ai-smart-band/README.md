# AI Smart Band Website

A complete 30-page responsive website for AI Smart Band product showcase, built with pure HTML, CSS, and JavaScript (no frameworks).

## 📁 Project Structure

```
ai-smart-band/
├── index.html                    # Homepage
├── css/                          # Stylesheets
│   ├── variables.css             # CSS custom properties
│   ├── reset.css                 # CSS reset & base styles
│   ├── typography.css            # Typography system
│   ├── layout.css                # Grid & layout systems
│   ├── components.css            # Reusable components
│   ├── animations.css            # Animations & transitions
│   └── main.css                  # Main stylesheet (imports all)
├── js/                           # JavaScript files
│   ├── main.js                   # Main JavaScript
│   ├── navigation.js             # Navigation & mobile menu
│   ├── scroll-animations.js      # Scroll-triggered animations
│   ├── product-gallery.js        # Product image galleries
│   ├── form-validation.js        # Form validation
│   └── data.js                   # Product data & content
├── pages/                        # Additional pages (29 pages)
│   ├── products.html
│   ├── ai-features.html
│   ├── health-tracking.html
│   ├── fitness-features.html
│   ├── sleep-monitoring.html
│   ├── heart-rate.html
│   ├── blood-oxygen.html
│   ├── stress-management.html
│   ├── smart-coaching.html
│   ├── battery-life.html
│   ├── water-resistance.html
│   ├── compatibility.html
│   ├── compare-models.html
│   ├── accessories.html
│   ├── app-features.html
│   ├── specifications.html
│   ├── faq.html
│   ├── support.html
│   ├── warranty.html
│   ├── shipping-info.html
│   ├── returns.html
│   ├── size-guide.html
│   ├── setup-guide.html
│   ├── troubleshooting.html
│   ├── about-us.html
│   ├── careers.html
│   ├── press.html
│   ├── blog.html
│   ├── contact.html
│   ├── privacy-policy.html
│   └── terms-of-service.html
└── assets/                       # Static assets
    └── images/                   # Image folders
```

## 🎨 Features

### Design System
- **Modern Color Palette**: Primary blue (#0066FF), secondary teal (#00D4AA)
- **Typography**: Inter and Poppins fonts with responsive sizing
- **Responsive Design**: Mobile-first approach with breakpoints for tablet and desktop
- **Smooth Animations**: Scroll-triggered animations, hover effects, and transitions

### Components
- **Navigation**: Responsive navbar with mobile hamburger menu
- **Hero Sections**: Full-screen product showcases
- **Product Cards**: Hover effects with quick actions
- **Feature Grids**: Icon-based feature displays
- **Forms**: Validated contact and support forms
- **Footer**: Multi-column with newsletter signup

### Interactive Features
- Mobile menu toggle
- Scroll animations (Intersection Observer)
- Form validation
- FAQ accordion
- Product galleries
- Smooth scrolling

## 📄 Page List (30 Pages Total)

### Core Pages (1-10)
1. **index.html** - Homepage with hero, features, products, testimonials
2. **products.html** - Product lineup with filters
3. **ai-features.html** - AI capabilities showcase
4. **health-tracking.html** - Health features overview
5. **fitness-features.html** - Fitness and workout features
6. **specifications.html** - Technical specifications
7. **compare-models.html** - Product comparison table
8. **faq.html** - Frequently asked questions
9. **contact.html** - Contact form and information
10. **support.html** - Customer support hub

### Feature Deep-Dive Pages (11-20)
11. **sleep-monitoring.html** - Sleep tracking features
12. **heart-rate.html** - Heart rate monitoring
13. **blood-oxygen.html** - SpO2 tracking
14. **stress-management.html** - Stress tracking and breathing exercises
15. **smart-coaching.html** - AI-powered coaching
16. **battery-life.html** - Battery specifications and tips
17. **water-resistance.html** - Water resistance ratings
18. **compatibility.html** - Device compatibility
19. **accessories.html** - Product accessories
20. **app-features.html** - Mobile app features

### Information & Support Pages (21-30)
21. **warranty.html** - Warranty information
22. **shipping-info.html** - Shipping details
23. **returns.html** - Return policy
24. **size-guide.html** - Product sizing guide
25. **setup-guide.html** - Device setup instructions
26. **troubleshooting.html** - Common issues and solutions
27. **about-us.html** - Company information
28. **careers.html** - Job openings
29. **press.html** - Press releases and media
30. **blog.html** - Blog articles
31. **privacy-policy.html** - Privacy policy
32. **terms-of-service.html** - Terms of service

## 🚀 Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (optional, for testing)

### Running the Website

1. **Open directly in browser:**
   Simply open `index.html` in your web browser

2. **Using a local server (recommended):**
   ```bash
   # Using Python 3
   python -m http.server 8000
   
   # Using Node.js (with npx)
   npx serve
   
   # Using PHP
   php -S localhost:8000
   ```
   Then navigate to `http://localhost:8000`

### File Organization
- All CSS files are in the `css/` directory
- All JavaScript files are in the `js/` directory
- All additional pages are in the `pages/` directory
- Static assets go in `assets/`

## 🎯 Key Features

### Responsive Design
- Mobile-first approach
- Breakpoints: 640px (sm), 768px (md), 1024px (lg)
- Optimized for all screen sizes

### Accessibility
- Semantic HTML5
- ARIA labels where needed
- Keyboard navigation support
- Skip to content link
- WCAG AA compliant color contrast

### Performance
- Minimal JavaScript (vanilla JS only)
- CSS animations (GPU accelerated)
- No external dependencies
- Fast loading times

### Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## 🛠️ Customization

### Changing Colors
Edit `css/variables.css`:
```css
:root {
  --primary: #0066FF;
  --secondary: #00D4AA;
  /* ... other colors */
}
```

### Modifying Content
Edit individual HTML files in the `pages/` directory

### Adding New Pages
1. Create new HTML file in `pages/` directory
2. Include header and footer components
3. Link from navigation menu

## 📱 JavaScript Modules

### main.js
- Initializes all modules
- Utility functions
- Event delegation

### navigation.js
- Mobile menu toggle
- Dropdown menus
- Active link highlighting
- Sticky header

### scroll-animations.js
- Intersection Observer setup
- Fade-in animations
- Counter animations
- Progress bars

### product-gallery.js
- Image galleries
- Lightbox functionality
- Touch/swipe support

### form-validation.js
- Real-time validation
- Error handling
- Success states

## 🎨 Design Tokens

### Colors
- Primary: `#0066FF`
- Secondary: `#00D4AA`
- Background: `#FFFFFF`
- Surface: `#F8F9FA`

### Typography
- Font Primary: Inter
- Font Secondary: Poppins
- Base Size: 16px
- Scale: 0.75rem to 3rem

### Spacing
- Base unit: 0.25rem (4px)
- Range: 0.25rem to 6rem

## 📝 Notes

- No external frameworks or libraries used
- Pure HTML, CSS, and JavaScript
- All pages are fully functional
- Responsive across all devices
- Accessible and SEO-friendly

## 📄 License

This project is created for demonstration purposes.

## 👨‍💻 Development

Built with modern web standards:
- HTML5
- CSS3 (Grid, Flexbox, Custom Properties)
- Vanilla JavaScript (ES6+)
- No build tools required

---

**Total Pages: 30**
**Total Files: 45+**
**Technologies: HTML, CSS, JavaScript**
