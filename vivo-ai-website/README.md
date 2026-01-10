# Vivo AI Website

A modern, professional multi-page website for Vivo AI - an artificial intelligence company.

## Features

- **8 Complete Pages**: Homepage, About, Products, Research, Careers, Contact, Privacy Policy, Terms of Service
- **Responsive Design**: Mobile-first approach, works seamlessly on all devices
- **Modern UI/UX**: Clean design with smooth animations and transitions
- **Pure HTML/CSS/JS**: No frameworks or dependencies required
- **Accessible**: WCAG 2.1 AA compliant with semantic HTML and ARIA labels
- **Interactive Elements**: Mobile navigation, tab filtering, form validation, scroll animations

## Project Structure

```
vivo-ai-website/
├── index.html              # Homepage
├── about.html              # About page
├── products.html           # Products & Solutions
├── research.html           # Research & Innovation
├── careers.html            # Careers page
├── contact.html            # Contact page with form
├── privacy.html            # Privacy Policy
├── terms.html              # Terms of Service
├── css/
│   ├── main.css            # Core styles and design system
│   ├── header.css          # Navigation styles
│   ├── footer.css          # Footer styles
│   ├── homepage.css        # Homepage-specific styles
│   ├── about.css           # About page styles
│   └── products.css        # Products page styles
├── js/
│   ├── main.js             # Core functionality
│   ├── navigation.js       # Mobile menu & scroll effects
│   └── animations.js       # Scroll animations & interactions
└── images/                 # Image assets
    ├── icons/
    ├── products/
    ├── team/
    └── office/
```

## Getting Started

1. **Open the website**:
   - Simply open `index.html` in your web browser
   - Or use a local server (recommended for best results)

2. **Using a local server**:
   ```bash
   # With Python 3
   python -m http.server 8000
   
   # With Node.js (http-server)
   npx http-server
   
   # With PHP
   php -S localhost:8000
   ```

3. **Navigate to**:
   - http://localhost:8000

## Design System

### Colors
- **Primary**: Royal Blue (#2563eb)
- **Secondary**: Purple (#8b5cf6)
- **Accent**: Cyan (#06b6d4)
- **Dark**: Dark Slate (#0f172a)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Bold weights (600-800)
- **Body**: Regular/Medium weights (400-500)

### Spacing
- Consistent spacing scale from 0.25rem to 6rem
- Generous white space for readability

## Features by Page

### Homepage
- Hero section with gradient background
- Statistics showcase
- Feature highlights
- Product previews
- Client testimonials
- Partner logos
- CTA section

### About
- Mission & Vision
- Core values
- Company story & timeline
- Leadership team
- Company culture
- Awards & recognition

### Products
- Product filtering by category
- Product cards with features
- Industry solutions
- Integration partners
- Demo CTA

### Research
- Research areas
- Featured publications
- Newsletter signup

### Careers
- Benefits showcase
- Job listings with filtering
- Application process
- Culture highlights

### Contact
- Contact form with validation
- Contact information
- Office locations
- Social media links

### Legal Pages
- Privacy Policy
- Terms of Service

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Performance

- Minimal JavaScript
- CSS animations (GPU accelerated)
- Lazy loading for images
- Optimized for 90+ Lighthouse score

## Accessibility

- Semantic HTML5
- ARIA labels
- Keyboard navigation
- Skip to content link
- Focus indicators
- Alt text for images
- WCAG AA compliant

## Customization

### Colors
Edit CSS variables in `css/main.css`:
```css
:root {
  --primary-color: #2563eb;
  --secondary-color: #8b5cf6;
  /* etc. */
}
```

### Fonts
Change in `<head>` of each HTML file:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

### Content
All text content can be edited directly in HTML files.

## Deployment

This is a static website and can be deployed to:
- **Netlify**: Drag & drop the folder
- **Vercel**: Import from Git
- **GitHub Pages**: Push to gh-pages branch
- **AWS S3**: Enable static website hosting
- **Any web server**: Upload all files

## License

© 2025 Vivo AI. All rights reserved.

## Contact

For questions or support:
- Email: contact@vivoai.com
- Website: www.vivoai.com
