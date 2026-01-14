document.addEventListener('DOMContentLoaded', function() {
  initNavigation();
  initScrollAnimations();
  initCounters();
  initAccordion();
  initForms();
  initNewsletter();
});

function initNavigation() {
  const header = document.querySelector('.header');
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', function() {
    if (window.scrollY > 100) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  if (hamburger) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navMenu.classList.toggle('active');
      document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    });
  }

  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      if (hamburger) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });

  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

function initScrollAnimations() {
  const fadeElements = document.querySelectorAll('.fade-in');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });
  
  fadeElements.forEach(el => observer.observe(el));
}

function initCounters() {
  const counters = document.querySelectorAll('.counter');
  
  if (!counters.length) return;
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counter = entry.target;
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
          current += step;
          if (current < target) {
            counter.textContent = Math.floor(current).toLocaleString();
            requestAnimationFrame(updateCounter);
          } else {
            counter.textContent = target.toLocaleString() + '+';
          }
        };
        
        updateCounter();
        observer.unobserve(counter);
      }
    });
  }, { threshold: 0.5 });
  
  counters.forEach(counter => observer.observe(counter));
}

function initAccordion() {
  const accordionItems = document.querySelectorAll('.accordion-item');
  
  accordionItems.forEach(item => {
    const header = item.querySelector('.accordion-header');
    
    if (header) {
      header.addEventListener('click', function() {
        const isActive = item.classList.contains('active');
        
        accordionItems.forEach(i => i.classList.remove('active'));
        
        if (!isActive) {
          item.classList.add('active');
        }
      });
    }
  });
}

function initForms() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      let isValid = true;
      const formGroups = form.querySelectorAll('.form-group');
      
      formGroups.forEach(group => {
        const input = group.querySelector('input, textarea, select');
        const small = group.querySelector('small');
        
        if (!input) return;
        
        group.classList.remove('error', 'success');
        if (small) small.textContent = '';
        
        if (input.hasAttribute('required') && !input.value.trim()) {
          group.classList.add('error');
          if (small) small.textContent = 'This field is required';
          isValid = false;
        } else if (input.type === 'email' && input.value.trim()) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(input.value.trim())) {
            group.classList.add('error');
            if (small) small.textContent = 'Please enter a valid email';
            isValid = false;
          } else {
            group.classList.add('success');
          }
        } else if (input.value.trim()) {
          group.classList.add('success');
        }
      });
      
      if (isValid) {
        const formData = new FormData(form);
        console.log('Form submitted:', Object.fromEntries(formData));
        
        if (form.id === 'contact-form') {
          alert('Thank you for your message! We will get back to you soon.');
          form.reset();
          formGroups.forEach(group => group.classList.remove('success'));
        }
      }
    });
  });
}

function initNewsletter() {
  const form = document.getElementById('newsletter-form');
  
  if (!form) return;
  
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = form.querySelector('input[type="email"]').value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (emailRegex.test(email)) {
      alert('Thank you for subscribing! Check your inbox for confirmation.');
      form.reset();
    } else {
      alert('Please enter a valid email address.');
    }
  });
}

function formatPrice(price) {
  return '$' + price.toFixed(2);
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}