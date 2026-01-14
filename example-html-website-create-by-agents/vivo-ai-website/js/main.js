document.addEventListener('DOMContentLoaded', function() {
  console.log('Vivo AI website loaded successfully');

  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const data = {};
      formData.forEach((value, key) => {
        data[key] = value;
      });
      
      console.log('Form submitted:', data);
      
      const successMessage = document.getElementById('formSuccess');
      if (successMessage) {
        successMessage.style.display = 'block';
        successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
          successMessage.style.display = 'none';
        }, 5000);
      }
      
      this.reset();
    });
  });

  const inputs = document.querySelectorAll('input, textarea, select');
  
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('focused');
      
      if (this.hasAttribute('required') && !this.value.trim()) {
        this.style.borderColor = 'var(--error)';
      } else {
        this.style.borderColor = 'var(--border-color)';
      }
    });
    
    input.addEventListener('input', function() {
      if (this.style.borderColor === 'var(--error)') {
        this.style.borderColor = 'var(--border-color)';
      }
    });
  });

  const emailInputs = document.querySelectorAll('input[type="email"]');
  
  emailInputs.forEach(input => {
    input.addEventListener('blur', function() {
      const email = this.value;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      if (email && !emailRegex.test(email)) {
        this.style.borderColor = 'var(--error)';
      }
    });
  });

  let scrollTimeout;
  window.addEventListener('scroll', function() {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    
    scrollTimeout = setTimeout(function() {
      const scrollPosition = window.pageYOffset;
      sessionStorage.setItem('scrollPosition', scrollPosition);
    }, 100);
  });

  const savedScrollPosition = sessionStorage.getItem('scrollPosition');
  if (savedScrollPosition) {
    window.scrollTo(0, parseInt(savedScrollPosition));
    sessionStorage.removeItem('scrollPosition');
  }

  const cards = document.querySelectorAll('.card');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });

  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.classList.add('loaded');
          imageObserver.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
  }

  const dateElements = document.querySelectorAll('[data-date]');
  
  dateElements.forEach(el => {
    const date = new Date(el.getAttribute('data-date'));
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    el.textContent = date.toLocaleDateString('en-US', options);
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const mobileMenu = document.querySelector('.nav-menu.active');
      const mobileToggle = document.querySelector('.mobile-toggle.active');
      
      if (mobileMenu) {
        mobileMenu.classList.remove('active');
      }
      
      if (mobileToggle) {
        mobileToggle.classList.remove('active');
        mobileToggle.setAttribute('aria-expanded', 'false');
      }
    }
  });

  window.addEventListener('beforeunload', function() {
    document.body.classList.add('page-leaving');
  });

  const leavingStyle = document.createElement('style');
  leavingStyle.textContent = `
    .page-leaving {
      opacity: 0;
      transition: opacity 0.3s ease-out;
    }
  `;
  document.head.appendChild(leavingStyle);

  const externalLinks = document.querySelectorAll('a[href^="http"]');
  
  externalLinks.forEach(link => {
    if (!link.hostname.includes(window.location.hostname)) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
});
