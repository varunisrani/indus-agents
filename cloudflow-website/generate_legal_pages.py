import os

# Base template for legal pages
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
        <a href="../product/overview.html" class="nav-link">Product</a>
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
      <a href="../product/overview.html" class="nav-link">Product</a>
      <a href="../industries/healthcare.html" class="nav-link">Industries</a>
      <a href="../resources.html" class="nav-link">Resources</a>
      <a href="../contact.html" class="nav-cta">Get Started</a>
      </div>
  </header>

  <main>
    <section class="section" style="background: linear-gradient(135deg, var(--gray-800) 0%, var(--gray-900) 100%); color: white; padding: var(--space-20) 0;">
      <div class="container text-center">
        <h1 style="color: white; margin-bottom: var(--space-4);">{hero_title}</h1>
        <p style="font-size: var(--text-xl); max-width: 700px; margin: 0 auto; opacity: 0.9;">{hero_subtitle}</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="card">
          <h2 style="margin-bottom: var(--space-4);">{content_title}</h2>
          <div style="color: var(--gray-600); line-height: 1.8;">
            <p style="margin-bottom: var(--space-4);">{content}</p>
            <p style="margin-bottom: var(--space-4);">Last updated: January 2024</p>
            <p>For questions about these policies, please contact us at legal@cloudflow.com</p>
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
            <li><a href="../product/overview.html">Overview</a></li>
            <li><a href="../product/automation.html">Automation</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>Legal</h4>
          <ul class="footer-links">
            <li><a href="privacy.html">Privacy Policy</a></li>
            <li><a href="terms.html">Terms of Service</a></li>
            <li><a href="security.html">Security</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>Company</h4>
          <ul class="footer-links">
            <li><a href="../about.html">About Us</a></li>
            <li><a href="../contact.html">Contact</a></li>
          </ul>
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

# Legal pages to generate
legal_pages = {
    'privacy.html': {
        'title': 'Privacy Policy',
        'description': 'CloudFlow privacy policy',
        'hero_title': 'Privacy Policy',
        'hero_subtitle': 'How we collect, use, and protect your data',
        'content_title': 'Our Commitment to Privacy',
        'content': 'At CloudFlow, we take your privacy seriously. This policy explains how we collect, use, and protect your personal information. We collect information you provide directly, such as when you create an account or contact us. We also collect information automatically as you use our service. We use this information to provide, improve, and personalize our services. We never sell your personal data to third parties. We implement industry-standard security measures to protect your information. You have the right to access, update, or delete your personal data at any time.'
    },
    'terms.html': {
        'title': 'Terms of Service',
        'description': 'CloudFlow terms of service',
        'hero_title': 'Terms of Service',
        'hero_subtitle': 'Rules and regulations for using CloudFlow',
        'content_title': 'Terms and Conditions',
        'content': 'By using CloudFlow, you agree to these terms. You must be at least 18 years old to use our service. You are responsible for maintaining the security of your account. You agree to notify us immediately of any unauthorized use. You retain ownership of any content you submit to CloudFlow. We grant you a limited, non-exclusive, non-transferable license to use our service. We may terminate your account if you violate these terms. We provide our service "as is" without warranties of any kind. We are not liable for any damages arising from your use of our service.'
    },
    'security.html': {
        'title': 'Security',
        'description': 'CloudFlow security and compliance information',
        'hero_title': 'Security & Compliance',
        'hero_subtitle': 'How we protect your data',
        'content_title': 'Enterprise-Grade Security',
        'content': 'Security is our top priority at CloudFlow. We are SOC 2 Type II certified and GDPR compliant. We use end-to-end encryption for all data in transit and at rest. We conduct regular security audits and penetration testing. We offer single sign-on (SSO) and multi-factor authentication (MFA) for enterprise customers. We maintain detailed audit logs for compliance. We have a dedicated security team monitoring our systems 24/7. We never store sensitive payment information on our servers.'
    }
}

# Generate legal pages
for filename, data in legal_pages.items():
    filepath = f'pages/legal/{filename}'
    content = base_template.format(**data)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created legal/{filename}')

print('\nAll legal pages created successfully!')
