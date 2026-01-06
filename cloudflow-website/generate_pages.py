import os

# Base template for pages
base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <title>{title} - CloudFlow</title>
  <link rel="stylesheet" href="../css/main.css">
</head>
<body>
  <header>
    <div class="header-container">
      <a href="../index.html" class="logo">
        <svg class="logo-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="currentColor"/>
          <path d="M16 8L24 16L16 24L8 16L16 8Z" fill="white"/>
        </svg>
        CloudFlow
      </a>
      <nav class="nav-menu">
        <a href="../index.html" class="nav-link">Home</a>
        <a href="about.html" class="nav-link">About</a>
        <a href="features.html" class="nav-link">Features</a>
        <a href="pricing.html" class="nav-link">Pricing</a>
        <a href="product/overview.html" class="nav-link">Product</a>
        <a href="industries/healthcare.html" class="nav-link">Industries</a>
        <a href="resources.html" class="nav-link">Resources</a>
        <a href="contact.html" class="nav-cta">Get Started</a>
      </nav>
      <div class="mobile-toggle"><span></span><span></span><span></span></div>
    </div>
    <div class="mobile-overlay"></div>
    <div class="mobile-menu">
      <a href="../index.html" class="nav-link">Home</a>
      <a href="about.html" class="nav-link">About</a>
      <a href="features.html" class="nav-link">Features</a>
      <a href="pricing.html" class="nav-link">Pricing</a>
      <a href="product/overview.html" class="nav-link">Product</a>
      <a href="industries/healthcare.html" class="nav-link">Industries</a>
      <a href="resources.html" class="nav-link">Resources</a>
      <a href="contact.html" class="nav-cta">Get Started</a>
    </div>
  </header>

  <main>
    <section class="section" style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; padding: var(--space-20) 0;">
      <div class="container text-center">
        <h1 style="color: white; margin-bottom: var(--space-4);">{hero_title}</h1>
        <p style="font-size: var(--text-xl); max-width: 700px; margin: 0 auto; opacity: 0.9;">{hero_subtitle}</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="card">
          <h2 style="margin-bottom: var(--space-4);">{content_title}</h2>
          <p style="color: var(--gray-600); margin-bottom: var(--space-6);">{content}</p>
          <a href="contact.html" class="btn btn-primary">Learn More</a>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="container">
      <div class="footer-grid">
        <div class="footer-column">
          <h4>Product</h4>
          <ul class="footer-links">
            <li><a href="product/overview.html">Overview</a></li>
            <li><a href="product/automation.html">Automation</a></li>
            <li><a href="product/integrations.html">Integrations</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>Company</h4>
          <ul class="footer-links">
            <li><a href="about.html">About Us</a></li>
            <li><a href="contact.html">Contact</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>Stay Updated</h4>
          <form id="newsletter-form" style="display: flex; gap: 0.5rem;">
            <input type="email" placeholder="Enter your email" class="form-input" style="flex: 1;" required>
            <button type="submit" class="btn btn-primary">Subscribe</button>
          </form>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 CloudFlow. All rights reserved.</p>
      </div>
    </div>
  </footer>

  <script type="module" src="../js/main.js"></script>
</body>
</html>'''

# Pages to generate
pages = {
    'resources.html': {
        'title': 'Resources',
        'description': 'Access CloudFlow resources including whitepapers, ebooks, and webinars',
        'hero_title': 'Resources & Learning',
        'hero_subtitle': 'Everything you need to succeed with CloudFlow',
        'content_title': 'Explore Our Resources',
        'content': 'Access our library of whitepapers, ebooks, webinars, and documentation to help you get the most out of CloudFlow.'
    },
    'careers.html': {
        'title': 'Careers',
        'description': 'Join the CloudFlow team and help build the future of work',
        'hero_title': 'Join Our Team',
        'hero_subtitle': 'Build the future of workflow automation with us',
        'content_title': 'Open Positions',
        'content': 'We\'re always looking for talented people to join our growing team. Check out our open positions and apply today.'
    },
    'partners.html': {
        'title': 'Partners',
        'description': 'Become a CloudFlow partner and grow your business',
        'hero_title': 'Partner Program',
        'hero_subtitle': 'Grow your business with CloudFlow',
        'content_title': 'Why Partner With Us?',
        'content': 'Join our partner program and access exclusive benefits, training, and resources to help you succeed.'
    },
    'support.html': {
        'title': 'Support',
        'description': 'Get help and support from the CloudFlow team',
        'hero_title': 'Help & Support',
        'hero_subtitle': 'We\'re here to help you succeed',
        'content_title': 'How Can We Help?',
        'content': 'Access our documentation, community forums, and contact our support team for assistance.'
    }
}

# Generate pages
for filename, data in pages.items():
    filepath = f'pages/{filename}'
    content = base_template.format(**data)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created {filename}')

print('\nAll pages created successfully!')
