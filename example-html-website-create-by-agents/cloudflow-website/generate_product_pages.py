import os

# Base template for product pages
base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <title>{title} - CloudFlow</title>
  <link rel="stylesheet" href="../../css/main.css">
</head>
<body>
  <header>
    <div class="header-container">
      <a href="../../index.html" class="logo">
        <svg class="logo-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="currentColor"/>
          <path d="M16 8L24 16L16 24L8 16L16 8Z" fill="white"/>
        </svg>
        CloudFlow
      </a>
      <nav class="nav-menu">
        <a href="../../index.html" class="nav-link">Home</a>
        <a href="../about.html" class="nav-link">About</a>
        <a href="../features.html" class="nav-link">Features</a>
        <a href="../pricing.html" class="nav-link">Pricing</a>
        <a href="overview.html" class="nav-link active">Product</a>
        <a href="../industries/healthcare.html" class="nav-link">Industries</a>
        <a href="../resources.html" class="nav-link">Resources</a>
        <a href="../contact.html" class="nav-cta">Get Started</a>
      </nav>
      <div class="mobile-toggle"><span></span><span></span><span></span></div>
    </div>
    <div class="mobile-overlay"></div>
    <div class="mobile-menu">
      <a href="../../index.html" class="nav-link">Home</a>
      <a href="../about.html" class="nav-link">About</a>
      <a href="../features.html" class="nav-link">Features</a>
      <a href="../pricing.html" class="nav-link">Pricing</a>
      <a href="overview.html" class="nav-link">Product</a>
      <a href="../industries/healthcare.html" class="nav-link">Industries</a>
      <a href="../resources.html" class="nav-link">Resources</a>
      <a href="../contact.html" class="nav-cta">Get Started</a>
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
        <div class="grid grid-cols-2 gap-8">
          <div>
            <h2 style="margin-bottom: var(--space-4);">{content_title}</h2>
            <p style="color: var(--gray-600); margin-bottom: var(--space-6);">{content}</p>
            <a href="../contact.html" class="btn btn-primary">Get Started</a>
          </div>
          <div class="card" style="padding: var(--space-8); background: var(--gray-50);">
            <h3 style="margin-bottom: var(--space-4);">Key Features</h3>
            <ul style="list-style: none; padding: 0;">
              <li style="padding: var(--space-2) 0;">✓ {feature1}</li>
              <li style="padding: var(--space-2) 0;">✓ {feature2}</li>
              <li style="padding: var(--space-2) 0;">✓ {feature3}</li>
              <li style="padding: var(--space-2) 0;">✓ {feature4}</li>
            </ul>
          </div>
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
            <li><a href="overview.html">Overview</a></li>
            <li><a href="automation.html">Automation</a></li>
            <li><a href="integrations.html">Integrations</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>Company</h4>
          <ul class="footer-links">
            <li><a href="../about.html">About Us</a></li>
            <li><a href="../contact.html">Contact</a></li>
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

  <script type="module" src="../../js/main.js"></script>
</body>
</html>'''

# Product pages to generate
product_pages = {
    'overview.html': {
        'title': 'Product Overview',
        'description': 'Overview of CloudFlow platform capabilities',
        'hero_title': 'CloudFlow Platform',
        'hero_subtitle': 'Powerful workflow automation for modern teams',
        'content_title': 'Everything You Need to Automate',
        'content': 'CloudFlow provides a complete platform for automating your business workflows. From simple tasks to complex processes, we have the tools you need.',
        'feature1': 'Visual workflow builder',
        'feature2': '500+ integrations',
        'feature3': 'Real-time analytics',
        'feature4': 'Enterprise security'
    },
    'automation.html': {
        'title': 'Workflow Automation',
        'description': 'Automate workflows with CloudFlow',
        'hero_title': 'Workflow Automation',
        'hero_subtitle': 'Automate anything without code',
        'content_title': 'Powerful Automation',
        'content': 'Create automated workflows with our drag-and-drop builder. Connect apps, automate tasks, and save time.',
        'feature1': 'No-code automation',
        'feature2': 'Custom triggers',
        'feature3': 'Conditional logic',
        'feature4': 'Scheduled workflows'
    },
    'integrations.html': {
        'title': 'Integrations',
        'description': 'Connect CloudFlow with your favorite apps',
        'hero_title': '500+ Integrations',
        'hero_subtitle': 'Connect all your tools',
        'content_title': 'Seamless Integrations',
        'content': 'Connect CloudFlow with the apps you already use. From CRM to marketing tools, we integrate with everything.',
        'feature1': 'One-click connect',
        'feature2': 'Custom integrations',
        'feature3': 'API access',
        'feature4': 'Webhook support'
    },
    'analytics.html': {
        'title': 'Analytics',
        'description': 'Analytics and reporting features',
        'hero_title': 'Advanced Analytics',
        'hero_subtitle': 'Insights that drive decisions',
        'content_title': 'Powerful Analytics',
        'content': 'Get real-time insights into your workflows with customizable dashboards and detailed reports.',
        'feature1': 'Real-time dashboards',
        'feature2': 'Custom reports',
        'feature3': 'Data export',
        'feature4': 'Performance metrics'
    },
    'collaboration.html': {
        'title': 'Collaboration',
        'description': 'Team collaboration features',
        'hero_title': 'Team Collaboration',
        'hero_subtitle': 'Work together seamlessly',
        'content_title': 'Better Together',
        'content': 'Collaborate on workflows with your team. Share, comment, and iterate in real-time.',
        'feature1': 'Shared workflows',
        'feature2': 'Real-time updates',
        'feature3': 'Team permissions',
        'feature4': 'Activity logs'
    },
    'security.html': {
        'title': 'Security',
        'description': 'Security and compliance information',
        'hero_title': 'Enterprise Security',
        'hero_subtitle': 'Your data is safe with us',
        'content_title': 'Bank-Grade Security',
        'content': 'We take security seriously. SOC 2 certified, GDPR compliant, and built with enterprise-grade security.',
        'feature1': 'SOC 2 Type II',
        'feature2': 'End-to-end encryption',
        'feature3': 'SSO support',
        'feature4': 'Audit logs'
    }
}

# Generate product pages
for filename, data in product_pages.items():
    filepath = f'pages/product/{filename}'
    content = base_template.format(**data)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created product/{filename}')

print('\nAll product pages created successfully!')
