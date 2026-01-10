Summary

- I reviewed plan.md (root) for the Oppo AI static website (lines cited below). The plan is a reasonable high-level start but contains critical gaps, ambiguity, and contradictory requirements that will cause implementation errors, security/privacy exposure, and accessibility failures unless corrected before coding.

Findings (ordered by severity)

1) Critical: CMS requirement conflicts with static-only brief
- Issue: plan.md includes "Implement a content management system (CMS) for easy content updates" but the project brief requires a static multi-page site using only HTML/CSS/JS (no frameworks).
- Why it matters: A CMS implies server-side components, authentication, secret handling, and deployment complexity that break the static-only constraint and expand scope/security surface.
- Where observed: plan.md line 19.
- Mitigation: Either remove CMS from v1 and use a static content workflow (content/*.md or content/*.json + a simple build script) or explicitly scope a third‑party headless CMS integration (and add secret management, OAuth, and privacy controls). Prefer the static workflow for minimal scope and security.
- Severity: Critical

2) High: Pages list mismatch vs. user brief
- Issue: User requested pages: index, about, products, contact. plan.md lists Home/Services/Portfolio/Blog/Contact.
- Why it matters: Implementing the wrong pages wastes developer time and produces a site that doesn't meet the stakeholder's needs.
- Where observed: plan.md lines 5–9 and folder structure lines 32–42.
- Mitigation: Update plan.md to require index.html, about.html, products.html, contact.html. Treat services/portfolio/blog as v2 items and explicitly mark them optional.
- Severity: High

3) High: Missing acceptance criteria and deliverables per page
- Issue: The plan lacks precise acceptance criteria (required components, metadata, mobile breakpoints, WCAG target) for each page.
- Why it matters: Subjective QA will cause rework and missed accessibility/security requirements.
- Where observed: plan.md pages and implementation steps (lines 5–21), folder structure (lines 32–44).
- Mitigation: Add a concise checklist per page (see Tests below). Target WCAG 2.1 AA for v1.
- Severity: High

4) Critical: Contact form and PII/data flow undefined
- Issue: Contact page exists but the plan doesn't define how submissions are handled, where data is stored, retention, or consent.
- Why it matters: Misconfigured forms can leak PII, violate GDPR/CCPA, or post data to insecure endpoints. Also introduces requirement for backend or third‑party services.
- Where observed: plan.md lines 8–9, 18–21.
- Mitigation: For a static site, mandate one of: mailto link, Formspree/Netlify Forms/StaticForms with documented privacy and TLS endpoints, or a serverless function with documented storage. Add spam mitigation (honeypot or reCAPTCHA) and a privacy notice on the contact page.
- Severity: Critical

5) High: Accessibility requirements are high-level and incomplete
- Issue: The plan references Lighthouse/WAVE but lacks concrete success criteria and required accessible patterns (skip link, keyboard navigation, form labels, color contrast, reduced-motion support).
- Why it matters: Accessibility regressions commonly slip in without explicit acceptance targets; legal/UX risk.
- Where observed: plan.md line 31.
- Mitigation: Target WCAG 2.1 AA, require semantic HTML5, visible focus states, aria attributes where appropriate, skip-link, aria-live for form errors, prefers-reduced-motion support, and color contrast >= 4.5:1 for normal text.
- Severity: High

6) High/Medium: Security & privacy gaps
- Issue: No CSP guidance, no secrets handling policy, and no documentation of third-party data-sharing or analytics.
- Why it matters: Inadvertent commit of API keys, insecure form endpoints, or privacy-violating third-party services can create legal and security exposure.
- Where observed: plan.md testing/security mentions (lines 21, 27–31) are generic.
- Mitigation: Add a 'Security' section: require HTTPS endpoints, no client-side secrets, implement CSP (or document exceptions), perform a secrets scan, limit third‑party scripts, and select privacy-preserving analytics (or none).
- Severity: High

7) Medium: Performance and asset strategy missing
- Issue: No guidance on responsive images (srcset/sizes), modern formats (WebP/AVIF), image compression, lazy-loading policy, or caching strategy.
- Why it matters: Large assets slow LCP and harm SEO and UX on mobile.
- Where observed: plan.md responsive/design mentions (lines 17, 32–42) but no specifics.
- Mitigation: Add image optimization requirements, critical CSS strategy, defer non-critical JS, performance budget (e.g., <=500 KB above-the-fold), and set caching headers on static assets.
- Severity: Medium

8) Medium: Testing scope is vague
- Issue: The plan lists "unit/integration/UAT" without defining what to test on a static site, missing accessibility/manual tests, e2e smoke tests, link-checkers, and negative cases.
- Why it matters: Tests may be skipped or ineffective.
- Where observed: plan.md lines 27–31.
- Mitigation: Add concrete tests (see Tests section) and CI steps (Lighthouse/axe, HTML validation, link-check, secrets scan).
- Severity: Medium

9) Medium: Folder structure ambiguity and package.json presence
- Issue: plan.md includes package.json in folder list, implying tooling; unclear whether build tooling is allowed.
- Why it matters: Developers may add unnecessary build/deploy complexity or commit node_modules or secrets.
- Where observed: plan.md lines 32–44.
- Mitigation: Clarify allowed dev toolchain: permit npm for dev-only tools (linting, image optimization, light build script) but state the final deliverable must be pure static HTML/CSS/JS with no server runtime required.
- Severity: Medium

10) Low/Medium: SEO and metadata omitted
- Issue: No explicit meta strategy, structured data, sitemap or robots specification.
- Why it matters: AI companies rely on organic discovery and thought leadership; missing SEO will reduce reach.
- Where observed: plan.md lacks SEO section.
- Mitigation: Add required meta tags, Open Graph, JSON-LD for Organization, sitemap.xml generation instruction, and robots.txt.
- Severity: Low

Tests (concrete cases to add to plan/CI)

- Per-page acceptance tests (index.html, about.html, products.html, contact.html):
  - Files exist, linked in header/footer.
  - Each page includes: <title>, meta description, viewport meta, and canonical link.
  - Hero section, main content area with H1, at least one CTA, and footer with contact info.
  - Responsive verified at 360px / 768px / 1024px / 1440px.

- Accessibility (automated + manual):
  - Run axe-core and fail build on any critical/serious rule.
  - Manual keyboard-only navigation: focus order, visible focus indicator, skip-to-main link.
  - Form controls: labels, aria-describedby for errors, error announcements via aria-live.
  - prefers-reduced-motion: animations disabled when set.
  - Color contrast checks: >=4.5:1 for normal text.

- Security & privacy tests:
  - Secrets scan: grep for common patterns (API_KEY, SECRET, PASSWORD) and run a simple token regex check.
  - Confirm form endpoints are HTTPS and documented; no client-side secrets.
  - CSP meta header present; list any allowed external origins.
  - Verify third-party scripts flagged and documented with privacy impact.

- Functional tests:
  - Link-checker to ensure no broken links.
  - Contact form submission flow using an allowed test endpoint; validate success UX and email delivery to test address.
  - JS component tests (menu toggle, product listing filters) with basic unit tests if JS exists.

- Performance tests:
  - Lighthouse target: Performance >= 80, Accessibility >= 90 for v1; set higher goals for production.
  - Core Web Vitals smoke checks under a simulated slow network (LCP, INP, CLS).
  - Image size budgets and total page weight threshold.

Next steps (1–3 immediate changes for the Coder)

1) Update plan.md to remove or re-scope the CMS requirement (line 19):
   - Replace with: "V1 will be a pure static site. Content stored under /content as JSON or Markdown; a small build script (optional) may compile content into HTML. No server-side CMS for v1." This is blocking.

2) Align pages with the user brief (lines 5–9):
   - Replace the current pages list with: index.html, about.html, products.html, contact.html. Mark services/portfolio/blog as v2 items.
   - Add per-page acceptance checklist (meta tags, hero, CTA, H1 presence, responsive breakpoints, WCAG AA items).

3) Add a Contact Form & Security section to plan.md describing allowed handling methods and required controls:
   - Allowed v1 form options: mailto link (basic), Formspree/Netlify Forms/StaticForms with documented privacy, or a serverless endpoint with TLS.
   - Require spam mitigation (honeypot or reCAPTCHA), privacy notice link, no client-side secrets, and documented receiver email/retention policy.

Blocking items

- Do not implement pages or components until plan.md is updated to resolve the CMS vs static conflict and contact form data flow. These are blocking because they change architecture and security requirements.

Reproduction / verification steps (for QA & coder)

1) Confirm plan.md changes: pages aligned to index/about/products/contact and CMS replaced with static workflow. If these changes are present, proceed.
2) Create a feature branch and scaffold the folder structure exactly: index.html, about.html, products.html, contact.html, /styles, /scripts, /images, /content.
3) Implement a minimal header/footer and verify navigation across all pages.
4) Implement contact form using an allowed test endpoint (Formspree test) and verify submissions over HTTPS; check that no secrets are committed.
5) Run automated checks: axe-core (accessibility), Lighthouse (performance), link-checker, and a secrets grep. Fix any critical failures before further feature work.

Files/lines referenced

- plan.md lines referenced: pages (5–9), CMS line (19), implementation steps (16–22), testing (27–31), folder structure (32–44).

Handoff to Coder (3 concrete edits)

- Edit 1 (plan.md): Replace pages list with the exact deliverables: index.html, about.html, products.html, contact.html; list other pages as v2.
- Edit 2 (plan.md): Remove CMS line and replace with static content workflow (content/*.md or content/*.json + optional build script). State "No server-side CMS for v1." (blocking).
- Edit 3 (plan.md): Add a Contact/Form handling section that documents allowed endpoints (Formspree/Netlify/mailto), spam mitigation, privacy notice, and no client-side secrets. Also add WCAG 2.1 AA acceptance criteria and basic SEO metadata requirements.

If you want, I can now hand these three change requests directly to the Coder agent.
