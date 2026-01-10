document.addEventListener('DOMContentLoaded', function() {
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  const animatedElements = document.querySelectorAll('.card, .feature-card, .product-card, .testimonial-card, .section-title');
  
  animatedElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
  });

  const style = document.createElement('style');
  style.textContent = `
    .animate-in {
      opacity: 1 !important;
      transform: translateY(0) !important;
    }
  `;
  document.head.appendChild(style);

  const statNumbers = document.querySelectorAll('.stat-number');
  
  const statObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateNumber(entry.target);
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(stat => statObserver.observe(stat));

  function animateNumber(element) {
    const text = element.textContent;
    const match = text.match(/[\d.]+/);
    
    if (match) {
      const target = parseFloat(match[0]);
      const suffix = text.replace(/[\d.]+/, '');
      const duration = 2000;
      const startTime = performance.now();
      
      function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const current = target * easeProgress;
        
        if (target % 1 !== 0) {
          element.textContent = current.toFixed(1) + suffix;
        } else {
          element.textContent = Math.floor(current) + suffix;
        }
        
        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          element.textContent = text;
        }
      }
      
      requestAnimationFrame(update);
    }
  }

  const tabs = document.querySelectorAll('.tab-btn');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const tabContainer = this.closest('.tabs');
      const allTabs = tabContainer.querySelectorAll('.tab-btn');
      const targetCategory = this.getAttribute('data-tab');
      
      allTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      const products = document.querySelectorAll('.product-card');
      
      products.forEach(product => {
        if (targetCategory === 'all' || product.getAttribute('data-category') === targetCategory) {
          product.classList.remove('hidden');
          product.style.animation = 'fadeIn 0.3s ease-out';
        } else {
          product.classList.add('hidden');
        }
      });
    });
  });

  const fadeStyle = document.createElement('style');
  fadeStyle.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `;
  document.head.appendChild(fadeStyle);

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    animatedElements.forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  }
});
