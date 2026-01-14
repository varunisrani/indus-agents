// Samsung Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  initMobileMenu();
  initFAQ();
  initProductFilters();
  initFormValidation();
  initScrollEffects();
});

function initMobileMenu() {
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  const mobileNav = document.querySelector('.nav-mobile');
  const closeMenu = document.querySelector('.close-mobile-menu');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link');

  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', function() {
      mobileNav.classList.add('active');
      document.body.style.overflow = 'hidden';
    });

    if (closeMenu) {
      closeMenu.addEventListener('click', function() {
        mobileNav.classList.remove('active');
        document.body.style.overflow = '';
      });
    }

    mobileLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        mobileNav.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
  }
}

function initFAQ() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(function(item) {
    const question = item.querySelector('.faq-question');

    if (question) {
      question.addEventListener('click', function() {
        const isActive = item.classList.contains('active');

        faqItems.forEach(function(faq) {
          faq.classList.remove('active');
        });

        if (!isActive) {
          item.classList.add('active');
        }
      });
    }
  });
}

function initProductFilters() {
  const filterOptions = document.querySelectorAll('.filter-option');
  const productCards = document.querySelectorAll('.product-card');

  filterOptions.forEach(function(option) {
    option.addEventListener('click', function() {
      const checkbox = option.querySelector('input');
      if (checkbox) {
        checkbox.checked = !checkbox.checked;
        option.style.color = checkbox.checked ? 'var(--samsung-blue)' : 'var(--text-secondary)';
      }
      filterProducts();
    });
  });
}

function filterProducts() {
  const selectedFilters = [];

  document.querySelectorAll('.filter-option input:checked').forEach(function(checkbox) {
    selectedFilters.push(checkbox.value);
  });

  productCards.forEach(function(card) {
    const category = card.dataset.category;

    if (selectedFilters.length === 0 || selectedFilters.includes(category)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

function initFormValidation() {
  const forms = document.querySelectorAll('form');

  forms.forEach(function(form) {
    const inputs = form.querySelectorAll('.form-input, .form-textarea, .form-select');

    inputs.forEach(function(input) {
      input.addEventListener('blur', function() {
        validateField(input);
      });

      input.addEventListener('input', function() {
        clearFieldError(input);
      });
    });

    form.addEventListener('submit', function(e) {
      e.preventDefault();

      let isValid = true;

      inputs.forEach(function(input) {
        if (!validateField(input)) {
          isValid = false;
        }
      });

      if (isValid) {
        showFormSuccess(form);
      }
    });
  });
}

function validateField(field) {
  const value = field.value.trim();
  let isValid = true;
  let errorMessage = '';

  if (field.required && !value) {
    isValid = false;
    errorMessage = 'This field is required';
  } else if (field.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      isValid = false;
      errorMessage = 'Please enter a valid email address';
    }
  } else if (field.type === 'tel' && value) {
    const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
    if (!phoneRegex.test(value)) {
      isValid = false;
      errorMessage = 'Please enter a valid phone number';
    }
  }

  if (!isValid) {
    showFieldError(field, errorMessage);
  } else {
    clearFieldError(field);
  }

  return isValid;
}

function showFieldError(field, message) {
  const formGroup = field.closest('.form-group');
  let errorEl = formGroup.querySelector('.form-error');

  if (!errorEl) {
    errorEl = document.createElement('div');
    errorEl.className = 'form-error';
    formGroup.appendChild(errorEl);
  }

  errorEl.textContent = message;
  field.style.borderColor = 'var(--error)';
}

function clearFieldError(field) {
  const formGroup = field.closest('.form-group');
  const errorEl = formGroup.querySelector('.form-error');

  if (errorEl) {
    errorEl.remove();
  }

  field.style.borderColor = '';
}

function showFormSuccess(form) {
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;

  submitBtn.textContent = 'Sent Successfully!';
  submitBtn.style.background = 'var(--success)';

  setTimeout(function() {
    submitBtn.textContent = originalText;
    submitBtn.style.background = '';
    form.reset();
  }, 3000);
}

function initScrollEffects() {
  const header = document.querySelector('.header');
  let lastScroll = 0;

  window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  });
}

function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      func.apply(context, args);
    }, wait);
  };
}
