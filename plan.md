Project: Oppo AI - Static Company Website

Overview and Objectives

- Build a multi-page static website for "Oppo AI" using only HTML, CSS, and vanilla JavaScript (no frameworks, no build tools required).
- Pages: index (home), about, products, contact. Responsive, accessible, performant, and easy to maintain.

Acceptance criteria per page (added):

- Each page must include: <title>, meta description, viewport meta, canonical link, H1 element, skip-to-main link, and a footer with contact info.
- Target WCAG 2.1 AA for accessibility. Visible focus states, semantic HTML, and keyboard operability required.
- Responsive verified at 360px / 768px / 1024px.

- Contact form/data flow: V1 is static-only. Allowed form options: Formspree/Netlify Forms/StaticForms with documented HTTPS endpoints, or a mailto fallback. Must include a consent checkbox, privacy note, and a simple honeypot for spam mitigation. No client-side secrets or server-side CMS for v1.

- CMS: Removed for v1. Use a static content workflow: store content under /content as JSON or Markdown; an optional small build script may compile content into HTML. No server-side CMS for v1.
- Deliverables: production-ready static site files that can be deployed to GitHub Pages, Netlify, or any static host.

Success criteria

- Fully functional static site with all pages and navigation.
- Passes basic accessibility checks (keyboard navigable, semantic markup, ARIA where appropriate, contrast >= WCAG AA when possible).
- Responsive layout across mobile/tablet/desktop breakpoints.
- Images optimized with responsive srcset and lazy-loading.
- Minimal, well-documented code with consistent patterns and comments.

Smart defaults and assumptions

- Design: modern, clean, minimalistic tech/company aesthetic.
- Typography: system font stack with optional Google Fonts fallback (include instructions to use local font files if needed).
- Color palette: primary (brand) color, dark/neutral text, light background. Ensure contrast.
- Navigation: top nav plus mobile hamburger menu.
- Contact form: static-friendly integration using Formspree or mailto fallback; provide both options.
- No server-side processing. All interactions run client-side or via third-party APIs.

Folder structure (root)

oppo-ai-site/
- index.html
- about.html
- products.html
- contact.html
- 404.html
- assets/
  - css/
    - styles.css           # main stylesheet (BEM conventions)
    - utilities.css        # small utility helpers (spacing, text, helpers)
  - js/
    - main.js              # global behaviors (menu, accessibility helpers, form handling)
    - products.js          # product page behaviors (filters, modals)
  - images/
    - logo.svg
    - hero/                # hero images in multiple sizes (jpg/webp)
    - products/            # product images with responsive sizes
    - team/                # team photo assets
  - icons/
    - svg-sprite.svg       # SVG sprites or individual svgs
- data/
  - products.json         # structured product data used by products.html (optional)
- docs/
  - README.md             # project notes and deployment instructions
- plan.md                 # this file

File breakdown and descriptions

- index.html
  - Purpose: homepage introducing Oppo AI, hero, value propositions, featured products, CTA.
  - Sections: skip-nav link, header (logo + nav), hero, features overview, featured products, customer logos/testimonials, footer.

- about.html
  - Purpose: company story, mission, team, timeline, careers CTA.
  - Sections: header, company mission, timeline, team grid (accessible cards), values, footer.

- products.html
  - Purpose: product catalog with brief descriptions, search/filter, product detail modal (client-side).
  - Sections: header, product filter/search bar, product grid, accessible product modal, footer.
  - Data: products.json used to populate the grid (fallback to inline HTML if JS disabled).

- contact.html
  - Purpose: contact details and contact form (Formspree integration or mailto fallback).
  - Sections: header, contact info (address, email, phone), contact form, map placeholder (static image or embedded iframe if allowed), footer.

- 404.html
  - Simple friendly not-found page matching site branding.

- assets/css/styles.css
  - Layout, typography, color variables, responsive grid, component styles (header, hero, cards, modals, forms).
  - Use CSS custom properties for theme variables.
  - BEM class naming for components.

- assets/js/main.js
  - Mobile menu toggle, focus management, skip link handling, lazy-loading polyfill if needed, form submission handler (with unobtrusive enhancement), storing site-wide constants.

- assets/js/products.js
  - Load products.json, render grid, implement client-side search and filters, keyboard-accessible product modal.

- data/products.json
  - Example JSON array of product objects: id, name, shortDescription, longDescription, images (array), features, price (if relevant), tags.

Content outlines (copy placeholders and structure)

- index.html
  - Title/meta description reflecting Oppo AI branding and hero keywords.
  - Hero: H1 "Oppo AI — Intelligent Solutions for Modern Businesses"
  - 3-4 feature cards: "AI Assistants", "Computer Vision", "Predictive Analytics", "Enterprise Integration"
  - CTA buttons: "Explore Products", "Contact Sales"

- about.html
  - H1 "About Oppo AI"
  - Mission statement paragraph
  - Timeline: founding year, milestones
  - Team: cards with name, role, short bio, social links (optional)

- products.html
  - H1 "Products"
  - Search input (label + accessible description)
  - Filter chips (category, industry, deployment: cloud/on-prem)
  - Product cards with image, name, short description, CTA "Learn more" that opens modal or navigates to anchored detail.

- contact.html
  - H1 "Contact Us"
  - Contact info block (address, phone, support email)
  - Contact form fields: name, email (required, type=email), organization (optional), subject, message (required), consent checkbox (privacy), submit button.
  - Form behavior: client-side validation, unobtrusive ARIA live region for errors/success, sends to Formspree or opens mailto fallback.

Accessibility (WCAG-focused)

- Semantic HTML5 elements: header, nav, main, article, section, footer, form, fieldset/legend when appropriate.
- Landmark roles and aria-labels where needed.
- Skip to main content link at top of each page.
- Keyboard accessibility: all interactive elements focusable and operable with keyboard.
- Focus styles: visible outline for focus state (do not remove outlines unless replaced with equivalent visible indicator).
- Color contrast: ensure text/background contrast meets WCAG AA. Provide alternative color suggestions in CSS variables for maintainers.
- Images: include meaningful alt text; decorative images use empty alt="".
- Forms: labels explicitly associated with inputs, error messages announced via aria-live="polite".
- Modals/dialogs: trap focus when open, return focus on close, provide role="dialog" and aria-modal="true".
- Use aria-hidden on inert content when modal open.

Responsive design

- Mobile-first CSS approach.
- Breakpoints: small (<=480px), medium (481–768px), large (769–1024px), xlarge (>=1025px). Prefer fluid layouts with max-width containers.
- Grid system: simple CSS Grid / Flexbox utilities for responsive columns.
- Nav: collapses to hamburger + accessible toggle on small screens.
- Images: use srcset and sizes attributes for responsive images; modern formats (webp) with fallbacks.

Performance and best practices

- Minimize HTTP requests: combine sprites, inline critical CSS if needed.
- Use compressed images (WebP + JPEG fallback), appropriate dimensions, and lazy-loading (loading="lazy").
- Defer non-critical JS (use defer attribute) and keep JS small and modular.
- Limit external requests; if using Google Fonts, use font-display:swap and host locally if privacy desired.
- Use caching headers when deploying; add simple link rel="preconnect" for external domains if used.

Privacy and security basics (static site)

- Do not collect unnecessary PII. Contact form includes consent checkbox and short privacy note.
- If integrating Formspree or similar, document that third-party services will process form submissions.
- No client-side secrets. Any API keys must be omitted or proxied by a server (not in scope).

Assets list

- Logo: logo.svg (vector)
- Favicons: favicon.ico + touch icons (png) in multiple sizes and site manifest (optional)
- Hero images: hero-320.webp/.jpg, hero-768.webp/.jpg, hero-1280.webp/.jpg
- Product images: product-<id>-320.webp/.jpg, product-<id>-640.webp/.jpg, product-<id>-1280.webp/.jpg
- Team photos: avatar-<name>-200.webp/.jpg
- SVG icons for features and social links (separate SVG files or one sprite)
- robots.txt and sitemap.xml (optional but recommended for SEO)

SEO and metadata

- Each page: unique title, meta description, canonical link, open graph tags (og:title, og:description, og:image), twitter card tags.
- Structured data: JSON-LD for Organization on index/about, and Product for product pages (optional).

Implementation steps (ordered, for Coder to execute)

1. Initialize repository and base files
   - Create project root with folder structure above.
   - Add index.html, about.html, products.html, contact.html, 404.html with basic HTML skeleton and shared header/footer includes (if not using includes, duplicate consistent header/footer across pages).
   - Add assets directories and empty placeholder files: css/styles.css, js/main.js, icons/logo.svg, images placeholders.
   - Deliverable: Project scaffolding committed.

2. Create global HTML template and header/footer
   - Implement consistent header with logo and nav links (Home, About, Products, Contact) and a skip link.
   - Implement footer with contact info, social links, small nav.
   - Ensure semantic markup and ARIA attributes where necessary.
   - Deliverable: Navigable site header/footer across all pages.

3. Implement responsive CSS base
   - Add CSS reset/normalize (small), CSS variables for colors/spacing/typography, base typography, anchor/focus styles.
   - Create layout utilities (container, grid, stack, spacing utilities) in utilities.css.
   - Deliverable: Base appearances implemented and consistent across pages.

4. Build homepage sections
   - Implement hero section (responsive image, H1, intro copy, CTA buttons).
   - Implement features cards and featured products section (use product cards markup or dynamic injection later).
   - Implement testimonial/logo strip and footer.
   - Deliverable: Completed home page layout and content placeholders.

5. Build About page
   - Implement mission, timeline, team grid (cards) with accessible markup.
   - Implement responsive layouts for team grid.
   - Deliverable: Completed about page.

6. Build Products page and data
   - Create data/products.json with product entries (5 sample products as default).
   - Implement product grid markup and product cards (use progressive enhancement: if JS disabled, show fallback static grid markup or message to enable JS).
   - Implement client-side products.js to fetch products.json, render cards, implement search/filter, and implement accessible product modal for details.
   - Deliverable: Interactive product catalog with keyboard-accessible modal.

7. Build Contact page and form handling
   - Implement form markup with labels and required validation attributes.
   - Implement JS form handler to post to Formspree (document how to swap endpoint) and show success/error message in aria-live region.
   - Provide mailto fallback link and instructions in HTML comments.
   - Deliverable: Working contact form with graceful fallback.

8. Accessibility and ARIA improvements
   - Add focus trapping in modal, aria-hidden toggling, and ensure all interactive widgets have keyboard support.
   - Run a11y checks (manual keyboard navigation, Lighthouse a11y audit, axe browser extension recommended).
   - Deliverable: Accessibility pass for main flows and documented a11y notes in docs/README.md.

9. Performance and optimization
   - Optimize and add responsive images and srcset, use loading="lazy" where appropriate.
   - Minify CSS and JS for production (provide minified assets or instruction to minify manually).
   - Deliverable: Optimized assets and performance notes.

10. Testing and validation
    - Cross-browser checks: Chrome, Firefox, Safari (mobile), Edge.
    - Responsive checks at common breakpoints and touch interactions.
    - Accessibility tests: keyboard only usage, Lighthouse, axe.
    - Link and HTML validation: run W3C validator for pages.
    - Deliverable: Test report summary in docs/README.md and fixes applied.

11. Deployment
    - Add docs/README.md with deployment options: GitHub Pages (push to gh-pages branch or use docs/ folder), Netlify, Vercel static deploy.
    - Provide robots.txt and sitemap.xml templates.
    - Deliverable: Deployed static site and deployment instructions.

Testing and validation approach

- Unit/test files: Not applicable for a static site, but test plans are provided.
- Manual QA checklist:
  - Navigation works and focus order logical
  - Header/footer consistent on all pages
  - Forms validate and provide accessible feedback
  - Product modal traps focus and is dismissible via Escape key
  - Images have alt text and responsive srcset
  - Page load performance reasonable (Lighthouse score >= 80 for Performance)
  - No console errors in browsers
- Automated/Tooling recommendations:
  - Lighthouse (Chrome) for performance/accessibility best-practices
  - axe DevTools or browser extension for deeper accessibility scanning
  - WAVE browser extension for visual accessibility issues

Dependencies and prerequisites

- No runtime dependencies. Modern browsers are expected.
- Optional: Formspree or other static form provider account if form submissions required.
- Optional: Node.js toolchain only if Coder wants to minify assets locally (not required). Provide guidance on manual minification alternatives.

Coding conventions and patterns

- CSS: BEM naming convention, CSS custom properties, mobile-first, keep components small and reusable.
- JS: Modular functions, use ES6+, use feature detection and progressive enhancement, attach event listeners with delegation for lists/grids.
- HTML: semantic markup, descriptive link text, avoid empty anchors.
- Comments: Add inline comments for non-obvious code and document any 3rd-party endpoints.

Edge cases and robustness

- Products page: gracefully handle products.json fetch failure (show message and provide fallback static content).
- Form submission: network failure should show clear error and allow retry.
- Images missing: use CSS background fallback color and alt text for informative fallback.

Deliverables checklist (what completion looks like)

- All pages present and navigable: index.html, about.html, products.html, contact.html, 404.html
- assets/css/styles.css and assets/css/utilities.css implemented
- assets/js/main.js and assets/js/products.js implemented
- data/products.json with sample products
- assets/images and assets/icons populated with placeholder assets
- docs/README.md with build, test, and deploy instructions
- Basic SEO meta tags and social cards included
- Accessibility checklist completed and documented

Estimated effort guidance (single developer)

- Scaffolding & base CSS: 4–8 hours
- Homepage & About page: 4–6 hours
- Products page + JS catalog: 8–12 hours
- Contact form + integration: 2–4 hours
- Accessibility fixes & testing: 4–6 hours
- Optimization & deployment: 2–4 hours

Notes for Coder (non-blocking assumptions)

- Use progressive enhancement: site must remain usable (content and navigation) without JavaScript. Enhanced interactions (modal, dynamic product loading) are optional progressive features.
- If any external service is added (Formspree, analytics), document it in docs/README.md and include privacy note on contact form.

Next steps for Coder

- Follow the Implementation steps in order. Create small commits per completed section.
- Run accessibility checks during development (keyboard testing + axe) rather than leaving until the end.
- Keep code modular and add comments for future maintainers.

End of plan.md
