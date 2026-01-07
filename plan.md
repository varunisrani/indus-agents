# Hare Krishna Agarbati Shop - Website Development Plan

## Project Overview
A multi-page informational and e-commerce showcase website for "Hare Krishna Agarbati Shop" - a traditional incense manufacturing company. The website will showcase their products, brand story, and provide contact information using pure HTML and CSS with modern design principles.

**Technology Stack:**
- HTML5 (semantic markup)
- CSS3 (modern features: Grid, Flexbox, Custom Properties, CSS Animations)
- Vanilla JavaScript (minimal, for mobile menu and simple interactions)
- No frameworks or libraries - pure, lightweight implementation

**Design Approach:**
- Warm, spiritual color palette reflecting traditional Indian aesthetics
- Modern, clean layout with excellent readability
- Fully responsive (mobile-first approach)
- Accessible (WCAG AA compliant)
- Fast loading with optimized assets

---

## Folder Structure

```
hare-krishna-agarbati/
├── index.html                    # Homepage
├── about.html                    # About Us page
├── products.html                 # Products catalog
├── contact.html                  # Contact page
├── css/
│   ├── styles.css                # Main stylesheet
│   ├── responsive.css            # Mobile/tablet responsiveness
│   └── animations.css            # CSS animations and transitions
├── js/
│   └── main.js                   # Minimal JavaScript (mobile menu, smooth scroll)
├── images/
│   ├── logo.png                  # Company logo
│   ├── hero-bg.jpg               # Homepage hero background
│   ├── products/
│   │   ├── incense-1.jpg
│   │   ├── incense-2.jpg
│   │   ├── incense-3.jpg
│   │   ├── incense-4.jpg
│   │   ├── incense-5.jpg
│   │   └── incense-6.jpg
│   └── icons/
│       ├── cart.svg
│       ├── menu.svg
│       ├── close.svg
│       └── social-icons.svg
├── fonts/                        # Custom fonts (optional, can use Google Fonts)
└── favicon.ico                   # Site favicon
```

---

## File Breakdown

### HTML Pages

#### 1. **index.html** (Homepage)
- **Hero Section:** Full-screen banner with welcoming message, CTA button
- **Features Section:** 3-4 key selling points (handmade, natural ingredients, traditional methods)
- **Featured Products:** Showcase 6 popular products with images and brief descriptions
- **Why Choose Us:** Trust indicators (quality, heritage, customer satisfaction)
- **Testimonials:** Customer reviews carousel
- **Newsletter Signup:** Email subscription form
- **Footer:** Links, social media, contact info

#### 2. **about.html** (About Us)
- **Company Story:** History and heritage of Hare Krishna Agarbati Shop
- **Mission & Values:** Spiritual approach, quality commitment
- **Manufacturing Process:** Step-by-step visual journey
- **Team Section:** Key team members
- **Certifications:** Quality assurance badges

#### 3. **products.html** (Products Catalog)
- **Product Filters:** Categories (Floral, Woody, Herbal, Special)
- **Product Grid:** 12-15 products with:
  - Product image
  - Product name
  - Scent description
  - Price
  - "Enquire" button
- **Product Modal/Details:** Expanded view (optional, can be simple)

#### 4. **contact.html** (Contact Page)
- **Contact Form:** Name, email, phone, message
- **Contact Information:** Address, phone, email, business hours
- **Location Map:** Embedded Google Map (placeholder)
- **Social Media Links:** Facebook, Instagram, WhatsApp
- **FAQ Section:** Common questions

### CSS Files

#### **css/styles.css** (Main Styles)
- **CSS Custom Properties:** Color palette, spacing, typography
- **Reset & Base Styles:** Normalize, consistent defaults
- **Typography:** Font families, sizes, weights, line heights
- **Layout Components:** Container, grid systems, flexbox utilities
- **Header/Navigation:** Logo, nav links, mobile menu trigger
- **Buttons:** Primary, secondary, outline variants
- **Forms:** Input fields, textareas, buttons
- **Cards:** Product cards, feature cards
- **Footer:** Multi-column layout

#### **css/responsive.css** (Media Queries)
- **Breakpoints:** 320px, 480px, 768px, 1024px, 1200px
- **Mobile Navigation:** Hamburger menu, slide-out drawer
- **Responsive Grids:** 1 column → 2 columns → 3 columns → 4 columns
- **Typography Scaling:** Adjusted font sizes for mobile
- **Image Optimization:** Responsive images with srcset

#### **css/animations.css** (Animations)
- **Fade-in animations:** Scroll-triggered reveals
- **Hover effects:** Button transforms, card lifts
- **Loading animations:** Skeleton screens (optional)
- **Smooth transitions:** All interactive elements

### JavaScript

#### **js/main.js** (Minimal Interactions)
- **Mobile Menu Toggle:** Open/close navigation drawer
- **Smooth Scrolling:** Anchor link animations
- **Scroll Animations:** Intersection Observer for fade-ins
- **Form Handling:** Basic form validation (no backend)
- **Sticky Header:** Add shadow on scroll

---

## Design Specifications

### Color Palette (CSS Custom Properties)
```css
:root {
  /* Primary - Warm, spiritual tones */
  --color-primary: #D4AF37;        /* Gold */
  --color-primary-dark: #B8962E;
  
  /* Secondary - Earthy, natural */
  --color-secondary: #8B4513;      /* Saddle brown */
  --color-secondary-light: #A0522D;
  
  /* Accent - Deep maroon/red */
  --color-accent: #800020;         /* Burgundy */
  
  /* Neutrals */
  --color-bg: #FFFEF9;             /* Off-white, cream */
  --color-bg-alt: #F5F0E8;         /* Light beige */
  --color-text: #2C1810;           /* Dark brown */
  --color-text-light: #6B4423;     /* Medium brown */
  --color-border: #E8DCC8;
  
  /* Semantic */
  --color-success: #2E7D32;
  --color-error: #C62828;
  
  /* Spacing */
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 2rem;
  --spacing-lg: 4rem;
  --spacing-xl: 6rem;
  
  /* Typography */
  --font-primary: 'Georgia', serif;
  --font-secondary: system-ui, sans-serif;
}
```

### Typography
- **Headings:** Georgia or similar serif (traditional, elegant)
- **Body Text:** System UI sans-serif (clean, readable)
- **Accent Text:** Decorative font for quotes (optional)

### Layout Principles
- **Container:** Max-width 1200px, centered
- **Grid:** CSS Grid for product layouts
- **Flexbox:** Navigation, card layouts, alignments
- **Spacing:** Consistent padding/margins using variables

---

## Implementation Steps

### Phase 1: Setup & Foundation
1. **Create project folder structure**
2. **Set up HTML5 boilerplate** for all pages (index, about, products, contact)
3. **Create CSS custom properties** in styles.css (colors, typography, spacing)
4. **Add CSS reset** and base styles
5. **Set up Google Fonts** (optional: Playfair Display for headings, Lato for body)

### Phase 2: Header & Navigation
6. **Build consistent header** component across all pages
7. **Create navigation menu** with logo and links
8. **Implement mobile hamburger menu** with CSS/JS
9. **Add smooth scroll behavior** for anchor links

### Phase 3: Homepage Development
10. **Create hero section** with background image and CTA
11. **Build features section** (3-4 key selling points)
12. **Add featured products grid** (6 products)
13. **Create testimonials section** with customer reviews
14. **Build newsletter signup** form
15. **Design footer** with links and social media

### Phase 4: About Page
16. **Create company story section** with imagery
17. **Build mission & values** section
18. **Add manufacturing process** visual timeline
19. **Create team section** (optional)
20. **Add certifications** badges

### Phase 5: Products Page
21. **Create product filter buttons** (Floral, Woody, Herbal, Special)
22. **Build product grid** with 12-15 products
23. **Design product cards** with image, name, description, price, button
24. **Add hover effects** and transitions
25. **Implement filter functionality** (JavaScript)

### Phase 6: Contact Page
26. **Create contact form** with proper input fields
27. **Add contact information** section
28. **Embed Google Map** (placeholder iframe)
29. **Build FAQ section** with accordion (optional)
30. **Add social media links**

### Phase 7: Responsive Design
31. **Implement mobile navigation** (hamburger menu, slide-out drawer)
32. **Create responsive breakpoints** for all sections
33. **Optimize images** for different screen sizes
34. **Test on mobile devices** (320px - 768px)
35. **Test on tablets** (768px - 1024px)

### Phase 8: Interactions & Polish
36. **Add scroll animations** (fade-in on scroll using Intersection Observer)
37. **Implement form validation** (HTML5 + basic JS)
38. **Add hover effects** to buttons and cards
39. **Create loading states** (optional skeleton screens)
40. **Add smooth transitions** throughout

### Phase 9: Content & Assets
41. **Add placeholder images** from Unsplash/Picsum for development
42. **Write compelling copy** for all sections
43. **Create SVG icons** for menu, cart, social media
44. **Optimize images** (compress, WebP format)
45. **Add favicon** to all pages

### Phase 10: Testing & Optimization
46. **Cross-browser testing** (Chrome, Firefox, Safari, Edge)
47. **Accessibility audit** (WCAG AA compliance)
48. **Performance optimization** (minify CSS, optimize images)
49. **Mobile testing** on actual devices
50. **Final review** and bug fixes

---

## Content Requirements

### Sample Content Structure

**Hero Section:**
- Headline: "Experience the Divine Fragrance of Tradition"
- Subtext: "Handcrafted incense made with love, devotion, and the purest natural ingredients"
- CTA: "Explore Our Collection"

**Product Categories:**
- Floral Collection (Rose, Jasmine, Lavender)
- Woody Collection (Sandalwood, Cedar, Patchouli)
- Herbal Collection (Tulsi, Neem, Camphor)
- Special Collection (Premium, Meditation, Festival)

**Key Features:**
- 100% Natural Ingredients
- Handmade with Devotion
- Traditional Recipes
- Eco-friendly Packaging

---

## Technical Best Practices

### HTML
- ✅ Semantic HTML5 elements (header, nav, main, section, article, footer)
- ✅ Proper heading hierarchy (h1 → h2 → h3)
- ✅ Alt text for all images
- ✅ ARIA labels for accessibility
- ✅ Meta tags for SEO and responsiveness

### CSS
- ✅ CSS Custom Properties for theming
- ✅ Mobile-first approach (min-width media queries)
- ✅ BEM naming convention (optional, but recommended)
- ✅ Flexbox and Grid for layouts
- ✅ Relative units (rem, em, %) for scalability
- ✅ CSS animations over JavaScript (performance)

### JavaScript
- ✅ Minimal and lightweight
- ✅ No jQuery or frameworks
- ✅ Modern ES6+ syntax
- ✅ Progressive enhancement
- ✅ Event delegation for dynamic content

### Performance
- ✅ Lazy loading for images
- ✅ Optimized image formats (WebP with fallbacks)
- ✅ Minified CSS in production
- ✅ Font display: swap for custom fonts
- ✅ No render-blocking resources

### Accessibility
- ✅ Keyboard navigation support
- ✅ Focus indicators on interactive elements
- ✅ Sufficient color contrast (4.5:1 minimum)
- ✅ Screen reader friendly
- ✅ Semantic markup
- ✅ Skip to main content link

---

## Testing Checklist

### Functionality
- [ ] All navigation links work correctly
- [ ] Mobile menu opens/closes properly
- [ ] Forms validate correctly
- [ ] Product filters work (if implemented)
- [ ] Smooth scrolling works
- [ ] All buttons have hover/active states

### Responsive Design
- [ ] Displays correctly on mobile (320px+)
- [ ] Displays correctly on tablet (768px+)
- [ ] Displays correctly on desktop (1024px+)
- [ ] Images scale properly
- [ ] Text remains readable at all sizes
- [ ] No horizontal scrolling

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader reads content correctly
- [ ] Color contrast meets WCAG AA
- [ ] Forms have proper labels
- [ ] Alt text on all images

### Performance
- [ ] Page loads under 3 seconds
- [ ] Images are optimized
- [ ] No console errors
- [ ] Smooth 60fps animations

---

## Deployment Considerations

### Before Launch
1. **Replace placeholder content** with actual text and images
2. **Set up contact form** backend (or use service like Formspree)
3. **Add analytics** (Google Analytics, optional)
4. **Configure favicon** and touch icons
5. **Test all forms** for functionality
6. **Set up 404 page** (optional)

### Hosting Options
- **GitHub Pages** (free, static hosting)
- **Netlify** (free tier, easy deployment)
- **Vercel** (free tier, excellent performance)
- **Traditional web host** (any shared hosting)

---

## Future Enhancements (Optional)

- **E-commerce integration** (Shopify, WooCommerce)
- **Product search functionality**
- **Shopping cart** (localStorage-based)
- **Blog section** for recipes, tips
- **Photo gallery** for events
- **Multi-language support**
- **Dark mode toggle**
- **Product comparison feature**

---

## Success Criteria

✅ All 4 pages fully functional and linked  
✅ Fully responsive across all device sizes  
✅ Modern, professional design with spiritual aesthetic  
✅ Accessible (WCAG AA compliant)  
✅ Fast loading (under 3 seconds)  
✅ Cross-browser compatible  
✅ Clean, maintainable code  
✅ Ready for production deployment  

---

## Notes

- **Images:** Use placeholder services like Unsplash Source or Picsum for development
- **Forms:** Can use Formspree.io for free form handling without backend
- **Icons:** Use SVG icons directly in HTML or icon fonts (Font Awesome CDN)
- **Fonts:** Google Fonts (Playfair Display + Lato) or system fonts for zero dependencies
- **Colors:** Adjust based on brand guidelines if available

---

**Project Estimated Time:** 8-12 hours for full implementation  
**Difficulty Level:** Intermediate (requires HTML/CSS knowledge, minimal JS)  
**Maintainability:** High (clean, well-organized code structure)  
