// Main JavaScript - AI Machine

document.addEventListener('DOMContentLoaded', function() {
  initNavigation();
  initScrollAnimations();
  initForms();
  initProductGalleries();

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

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      mobileToggle.classList.toggle('active');
    });
  }

  if (navbar) {
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
  }

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
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  animatedElements.forEach(el => observer.observe(el));

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
    const images = gallery.querySelectorAll('.gallery-image');
    const thumbnails = gallery.querySelectorAll('.gallery-thumbnail');
    const prevBtn = gallery.querySelector('.gallery-prev');
    const nextBtn = gallery.querySelector('.gallery-next');

    let currentIndex = 0;

    const showImage = (index) => {
      images.forEach((img, i) => {
        img.classList.toggle('active', i === index);
      });
      thumbnails.forEach((thumb, i) => {
        thumb.classList.toggle('active', i === index);
      });
      currentIndex = index;
    };

    thumbnails.forEach((thumb, index) => {
      thumb.addEventListener('click', () => showImage(index));
    });

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        const newIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
        showImage(newIndex);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        const newIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
        showImage(newIndex);
      });
    }

    showImage(0);
  });
}
