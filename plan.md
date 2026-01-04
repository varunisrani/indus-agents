Project: RealEstate Startup — Static Site (HTML, CSS, Vanilla JS)

# 1. Project Overview & Objectives

- Build a modern, responsive, accessible marketing website for a real estate startup using plain HTML, CSS, and vanilla JavaScript (no frameworks).
- Primary goals:
  - Attraction and conversion: present listings, nurture leads through CTAs on every page.
  - Fast performance and good SEO fundamentals.
  - High accessibility and mobile-first responsive design.
- Deliverables: plan.md (this file) and the fully implemented static site files in the repository structure below.

# 2. Smart Defaults (no questions asked)

- Design: minimal, clean UI inspired by modern real estate websites.
- Color palette: primary #0b6efd (blue), accent #ff6b6b (coral), neutral bg #f7f8fb, text #0f1724.
- Typography: system stack (Inter if available) — fallback stack: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif.
- Layout: mobile-first CSS with progressive enhancement for larger screens.
- Data: static JSON (data/listings.json) as source of truth for demo content.
- Images: prefer WebP with JPEG fallback; use responsive srcset and loading="lazy".

# 3. Success Criteria

- Core pages implemented: homepage, listings, property detail, about, contact, 404.
- Listings load client-side from data/listings.json and can be filtered on the client.
- Property page accepts query string id and renders details.
- Accessibility: keyboard operable, ARIA where needed, semantic HTML, visible focus states.
- Performance: defer JS, lazy-load images, modest asset sizes.
- SEO: meta tags, OG tags, JSON-LD for properties.

# 4. Project Structure (root)

realestate-site/
- plan.md
- README.md
- index.html
- listings.html
- property.html
- about.html
- contact.html
- 404.html
- css/
  - utilities.css       # reset, helpers, .sr-only, container
  - styles.css          # main styles, variables, layout, components
- js/
  - main.js             # mobile menu, fetch listings, filters, lazy load
  - gallery.js          # minimal carousel + lightbox
- assets/
  - img/
    - hero-1.jpg (hero-1.webp)
    - property-1.jpg (property-1.webp)
    - property-2.jpg ...
  - icons/
    - menu.svg, close.svg, bed.svg, bath.svg, area.svg, map.svg
- data/
  - listings.json       # sample property data used by listings & property pages
- sitemap.xml
- robots.txt
- manifest.json (optional)

# 5. File Descriptions

- index.html
  - Hero with CTA and quick search, featured listings, how-it-works, testimonials, footer.
- listings.html
  - Client-side rendered grid of Property Cards, filter controls, pagination/load-more.
- property.html
  - Reads ?id=<id> from URL and renders property details, gallery, features, contact CTA.
- about.html
  - Company mission, team, values.
- contact.html
  - Contact form (client-side validation) and map placeholder.
- 404.html
  - Friendly 404 with links back to homepage.
- css/utilities.css
  - CSS reset, container class, grid helpers, .sr-only, .visually-hidden, utility spacing.
- css/styles.css
  - Variables, typography, header, hero, property-card, grid, footer, responsive breakpoints.
- js/main.js
  - DOMContentLoaded handlers, mobile menu toggle & focus trap, fetch data/listings.json, client-side filtering and rendering, lazy image loader.
- js/gallery.js
  - Lightweight carousel and lightbox with keyboard support.
- data/listings.json
  - Array of property objects: id, title, price, city, beds, baths, area, images[], description, tags, lat/lng(optional).

# 6. UX Components and Patterns

- Header
  - Left: logo. Right: nav links and primary CTA ("List a Property" or "Contact"). Mobile: hamburger toggles off-canvas nav.
  - Accessible toggle button with aria-expanded and aria-controls.
- Hero
  - Large headline, subhead, quick-search with three inputs (location, price range, beds) and primary CTA.
- Property Card
  - Image, price, title, location, meta (beds/baths/area), heart icon to "save" (localStorage demo), and view button.
- Listings Grid
  - Responsive grid (1 col mobile, 2 medium, 3 desktop), client-side filters show real-time result count.
- Property Page
  - Gallery with thumbnails, main image; details side panel with contact CTA.
- Footer
  - Links, social icons, contact info, copyright.

# 7. Asset Handling

- Use local assets/assets/img/ for repository portability. If no provided example images, use placeholders from https://picsum.photos or https://images.unsplash.com source URLs.
- Provide WebP + JPEG pairs for important images. Example markup using picture element:

<picture>
  <source srcset="assets/img/property-1-1200.webp 1200w, assets/img/property-1-768.webp 768w" type="image/webp">
  <source srcset="assets/img/property-1-1200.jpg 1200w, assets/img/property-1-768.jpg 768w" type="image/jpeg">
  <img src="assets/img/property-1-768.jpg" alt="3 bed family home in Downtown" loading="lazy" sizes="(max-width: 600px) 100vw, 33vw">
</picture>

- Thumbnails: smaller sizes (320/480). Use srcset with sizes attribute.
- Lazy loading: use loading="lazy" and IntersectionObserver for polyfill/enhanced behavior.

# 8. Accessibility (A11y) Requirements

- Use semantic HTML: header, nav, main, article, section, footer.
- Skip link to main content: <a class="skip-link" href="#main-content">Skip to content</a>
- Descriptive alt text for images.
- Color contrast: ensure text meets WCAG AA (check with contrast tools).
- ARIA: use aria-expanded, aria-controls for menu; aria-modal for gallery; role="dialog" for lightbox.
- Keyboard:
  - Mobile menu: trap focus while open and return focus to toggle on close.
  - Lightbox: close on ESC, navigate images via left/right.
- Visible focus outlines for interactive elements (not removed)

# 9. Responsive & Mobile-first Strategy

- Base styles target mobile first (width < 600px). Add breakpoints at 600px, 900px, 1200px.
- Grid behavior:
  - 0–599px: 1 column
  - 600–899px: 2 columns
  - 900px+: 3 columns
- Navigation collapses to hamburger on small screens.
- Touch targets: minimum 44x44 px for interactive elements.

# 10. SEO & Structured Data

- Meta tags per page: title, description, viewport, canonical.
- Open Graph tags for social sharing: og:title, og:description, og:image, og:url, og:type.
- Twitter card tags.
- JSON-LD structured data:
  - Add Organization or LocalBusiness on index.
  - Add schema.org/Residence or Offer annotations on property pages (sample inlined JSON-LD).
- Friendly URLs: use listings.html and property.html?id=1 for static demo. For production consider /listings/ and /property/slug/.
- sitemap.xml and robots.txt included in root.

# 11. Performance Best Practices

- Single CSS file, minimal utility CSS; defer heavy JS (use defer attribute).
- Minimize DOM size and CSS selectors' complexity.
- Use responsive images and WebP where available.
- Use lazy loading for offscreen images.
- Use preconnect for critical external hosts (e.g., fonts). Prefer system fonts to avoid render-blocking.
- Set long-lived cache headers on static assets via hosting provider.
- Optional: add small service worker for caching static assets.

# 12. Testing & Validation Checklist

Manual tests
- [ ] Pages load and render correctly on mobile & desktop
- [ ] Keyboard navigation works (menu, gallery, filters)
- [ ] All images have alt text
- [ ] Contact form validation & submission flow (or mailto fallback)
- [ ] Filters produce expected result counts
- [ ] Property page renders correct data for multiple ids

Automated / Tools
- [ ] Lighthouse: performance, accessibility, best practices, SEO (aim >90)
- [ ] axe-core scan for accessibility violations
- [ ] W3C HTML validation
- [ ] Cross-browser sanity: Chrome, Firefox, Safari, Edge (latest)

Edge cases
- Missing images: show placeholder with aria-hidden and descriptive text
- Slow network: ensure loading states for property grid (skeleton cards)
- No JS: ensure content degrade gracefully (basic HTML content + links accessible)

# 13. Deployment Instructions

Recommended hosts: GitHub Pages, Netlify, Vercel (all support static sites). Steps (example GitHub Pages):

1. Commit repository to GitHub.
2. In repo settings -> Pages, set source to main branch / root.
3. Add CNAME if using custom domain and configure DNS.
4. Ensure sitemap.xml is at root and robots.txt present.
5. (Optional) Configure redirects on Netlify if using clean URLs.
6. Configure cache-control headers via hosting provider (e.g., Netlify _headers file or platform UI).

Production build suggestions
- Minify css/styles.css and js/*.js (use online minifier or small npm scripts).
- Pre-generate optimized WebP images and sizes and include them in assets/img/.

# 14. Implementation Steps & Timeline (Milestones)

Milestone 1 — Scaffold & sample data (1.5 hours)
- Create file/folder structure and empty files.
- Add data/listings.json with 8 sample properties and placeholder images.
- Add placeholder icons and hero image.

Milestone 2 — Base styles & header/nav (2.5 hours)
- Implement utilities.css and styles.css variables.
- Build header/navigation and mobile menu toggle (JS).
- Create hero section & CTA on index.html.

Milestone 3 — Property card & listings page (3.5 hours)
- Design property-card component and responsive grid styles.
- Implement fetch('data/listings.json') and render grid in listings.html.
- Add client-side filtering UI and result count.

Milestone 4 — Property detail & gallery (3 hours)
- Implement property.html to read ?id from URL and render details.
- Implement gallery.js for carousel and lightbox with keyboard support.
- Add contact CTA and simple contact form validation.

Milestone 5 — Accessibility, SEO & responsive polish (2 hours)
- Add skip link, ARIA labels, focus trapping, JSON-LD, OG meta tags.
- Tweak responsive layouts and spacing.

Milestone 6 — Performance optimization & final QA (1.5 hours)
- Optimize images, add srcset, apply lazy loading.
- Minify CSS/JS and run Lighthouse audits.
- Prepare README and deploy to chosen host.

Estimated total: 14–15 hours (single developer).

# 15. Prioritized TODOs (Immediate)

1. Scaffold files & sample data
2. Implement header/nav + mobile menu
3. Implement property card and listing render
4. Implement property page & gallery
5. Accessibility & SEO adjustments
6. Image optimization & deploy

# 16. Example Code Snippets (copy-ready)

HTML - header + skip link (index.html):

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Haven Homes — Find your next home</title>
  <meta name="description" content="Haven Homes — curated homes, rentals, and investment properties.">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header">
    <div class="container">
      <a class="logo" href="/">Haven<span class="accent">Homes</span></a>
      <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">☰</button>
      <nav id="primary-nav" class="primary-nav" role="navigation">
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="listings.html">Listings</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <main id="main-content"></main>
  <script src="js/main.js" defer></script>
</body>
</html>

CSS - variables, container, header (css/styles.css):

:root {
  --color-primary: #0b6efd;
  --color-accent: #ff6b6b;
  --bg: #f7f8fb;
  --text: #0f1724;
  --radius: 12px;
  --max-width: 1100px;
}
*{box-sizing:border-box}
html{font-size:16px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;margin:0;background:var(--bg);color:var(--text);}
.container{max-width:var(--max-width);margin:0 auto;padding:0 1rem}
.site-header{background:#fff;border-bottom:1px solid rgba(15,23,36,0.06)}
.site-header .container{display:flex;align-items:center;justify-content:space-between;padding:0.75rem 0}
.menu-toggle{background:none;border:0;font-size:1.25rem}
.primary-nav{display:none}
@media(min-width:768px){.menu-toggle{display:none}.primary-nav{display:block}}

JS - menu toggle & basic fetch (js/main.js):

document.addEventListener('DOMContentLoaded',()=>{
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('primary-nav');
  if(menuToggle){
    menuToggle.addEventListener('click',()=>{
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('open');
    });
  }

  // Example: load featured properties into a container with id 'featured'
  fetch('data/listings.json')
    .then(r=>r.json())
    .then(data=>{
      const featured = document.querySelector('#featured');
      if(!featured) return;
      data.slice(0,3).forEach(item=>{
        const card = createPropertyCard(item); // implement createPropertyCard to return element
        featured.appendChild(card);
      });
    }).catch(err=>{console.error('Listings fetch failed',err)});
});

# 17. Sample data/listings.json schema (example single item)

[
  {
    "id": "1",
    "title": "Modern 3 Bed Family Home",
    "price": 725000,
    "city": "San Francisco",
    "beds": 3,
    "baths": 2,
    "area": 1550,
    "images": ["assets/img/property-1-1200.jpg","assets/img/property-1-768.jpg"],
    "description": "Beautiful 3 bedroom home located close to downtown with bright open plan living.",
    "tags": ["featured","garden"]
  }
]

# 18. Testing Checklist (Developer)

- Run a local static server: python3 -m http.server 8000 or npx http-server
- Verify index -> listings -> property flows
- Run Lighthouse audits and record results
- Run accessibility scan (axe extension)

# 19. README / Local Dev Notes

- To preview locally: python3 -m http.server 8000 then visit http://localhost:8000
- Use `npx http-server` or any static server for local dev.
- To add more listings, edit data/listings.json and place images in assets/img/ then reference them in the JSON.

# 20. Handoff

This plan is complete and prescriptive. The next step is implementation according to the milestones above.

