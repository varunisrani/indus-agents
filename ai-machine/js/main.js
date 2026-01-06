document.addEventListener('DOMContentLoaded', function() {
  initNavigation();
  initScrollAnimations();
  initForms();
  initProductGalleries();
  initAccordions();
  initTabs();
  initCodeBlocks();

  const currentYearElements = document.querySelectorAll('.current-year');
  currentYearElements.forEach(element => {
    element.textContent = new Date().getFullYear();
  });
});

const utils = {
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
};

function initNavigation() {
  const navbar = document.querySelector('.navbar');
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      mobileToggle.classList.toggle('active');
    });
  }

  let lastScroll = 0;
  window.addEventListener('scroll', utils.throttle(() => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  }, 100));

  document.addEventListener('click', (e) => {
    if (navbar && !navbar.contains(e.target) && navMenu && navMenu.classList.contains('active')) {
      navMenu.classList.remove('active');
      if (mobileToggle) mobileToggle.classList.remove('active');
    }
  });
}

function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
  });

  window.addEventListener('scroll', utils.throttle(() => {
    const scrolled = window.pageYOffset;
    document.querySelectorAll('.parallax').forEach(el => {
      const rate = el.dataset.rate || 0.5;
      el.style.transform = `translateY(${scrolled * rate}px)`;
    });
  }, 16));
}

function initForms() {
  const forms = document.querySelectorAll('form[data-validate]');

  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
      input.addEventListener('blur', () => validateField(input));
      input.addEventListener('input', () => {
        if (input.classList.contains('error')) {
          validateField(input);
        }
      });
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      let isValid = true;
      inputs.forEach(input => {
        if (!validateField(input)) {
          isValid = false;
        }
      });

      if (isValid) {
        submitForm(form);
      }
    });
  });
}

function validateField(field) {
  const value = field.value.trim();
  const type = field.type;
  const required = field.hasAttribute('required');

  field.classList.remove('error');
  const errorMsg = field.parentNode.querySelector('.error-message');
  if (errorMsg) errorMsg.remove();

  if (required && !value) {
    showError(field, 'This field is required');
    return false;
  }

  if (type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showError(field, 'Please enter a valid email address');
      return false;
    }
  }

  return true;
}

function showError(field, message) {
  field.classList.add('error');
  const error = document.createElement('span');
  error.className = 'error-message';
  error.textContent = message;
  field.parentNode.appendChild(error);
}

function submitForm(form) {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = 'Sending...';
  submitBtn.disabled = true;

  setTimeout(() => {
    submitBtn.textContent = 'Sent!';
    form.reset();

    setTimeout(() => {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }, 2000);
  }, 1500);
}

function initProductGalleries() {
  const galleries = document.querySelectorAll('.product-gallery');

  galleries.forEach(gallery => {
    const mainImage = gallery.querySelector('.main-image img');
    const thumbnails = gallery.querySelectorAll('.thumbnail img');

    thumbnails.forEach(thumb => {
      thumb.addEventListener('click', () => {
        const newSrc = thumb.dataset.full || thumb.src;
        mainImage.src = newSrc;

        thumbnails.forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');
      });
    });
  });
}

function initAccordions() {
  const accordions = document.querySelectorAll('.accordion');

  accordions.forEach(accordion => {
    const items = accordion.querySelectorAll('.accordion-item');

    items.forEach(item => {
      const header = item.querySelector('.accordion-header');

      header.addEventListener('click', () => {
        const isOpen = item.classList.contains('active');

        items.forEach(i => i.classList.remove('active'));

        if (!isOpen) {
          item.classList.add('active');
        }
      });
    });
  });
}

function initTabs() {
  const tabContainers = document.querySelectorAll('.tabs');

  tabContainers.forEach(container => {
    const tabButtons = container.querySelectorAll('.tab-button');
    const tabPanels = container.querySelectorAll('.tab-panel');

    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        const targetId = button.dataset.tab;

        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabPanels.forEach(panel => panel.classList.remove('active'));

        button.classList.add('active');
        document.getElementById(targetId).classList.add('active');
      });
    });
  });
}

function initCodeBlocks() {
  const codeBlocks = document.querySelectorAll('.code-block');

  codeBlocks.forEach(block => {
    block.addEventListener('click', () => {
      const code = block.textContent;
      navigator.clipboard.writeText(code).then(() => {
        const originalText = block.textContent;
        block.textContent = 'Copied to clipboard!';
        setTimeout(() => {
          block.textContent = originalText;
        }, 2000);
      });
    });
  });
}

function smoothScroll(target) {
  const element = document.querySelector(target);
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  }
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href !== '#') {
      e.preventDefault();
      smoothScroll(href);
    }
  });
});
