// Form Validation Module - AI Machine

export function initForms() {
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
  const minLength = field.dataset.minLength;
  const maxLength = field.dataset.maxLength;
  const pattern = field.dataset.pattern;

  clearError(field);

  if (required && !value) {
    showError(field, 'This field is required');
    return false;
  }

  if (minLength && value.length < parseInt(minLength)) {
    showError(field, `Minimum length is ${minLength} characters`);
    return false;
  }

  if (maxLength && value.length > parseInt(maxLength)) {
    showError(field, `Maximum length is ${maxLength} characters`);
    return false;
  }

  if (type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showError(field, 'Please enter a valid email address');
      return false;
    }
  }

  if (type === 'tel' && value) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    if (!phoneRegex.test(value)) {
      showError(field, 'Please enter a valid phone number');
      return false;
    }
  }

  if (pattern && value) {
    const regex = new RegExp(pattern);
    if (!regex.test(value)) {
      showError(field, field.dataset.patternError || 'Invalid format');
      return false;
    }
  }

  return true;
}

function showError(field, message) {
  field.classList.add('error');

  let errorMsg = field.parentNode.querySelector('.error-message');
  if (!errorMsg) {
    errorMsg = document.createElement('span');
    errorMsg.className = 'error-message';
    field.parentNode.appendChild(errorMsg);
  }

  errorMsg.textContent = message;
}

function clearError(field) {
  field.classList.remove('error');
  const errorMsg = field.parentNode.querySelector('.error-message');
  if (errorMsg) {
    errorMsg.remove();
  }
}

function submitForm(form) {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = 'Sending...';
  submitBtn.disabled = true;

  console.log('Form submitted:', data);

  setTimeout(() => {
    submitBtn.textContent = 'Sent!';
    form.reset();

    const successMsg = document.createElement('div');
    successMsg.className = 'success-message';
    successMsg.textContent = 'Thank you! Your message has been sent successfully.';
    form.insertBefore(successMsg, form.firstChild);

    setTimeout(() => {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
      successMsg.remove();
    }, 3000);
  }, 1500);
}
