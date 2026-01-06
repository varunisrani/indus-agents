class FormValidator {
  constructor(form) {
    this.form = form;
    this.fields = this.form.querySelectorAll('input, textarea, select');
    this.rules = {};
    this.messages = {};
    
    this.init();
  }
  
  init() {
    this.loadRules();
    this.bindEvents();
  }
  
  loadRules() {
    this.fields.forEach(field => {
      const name = field.name;
      
      this.rules[name] = {
        required: field.hasAttribute('required'),
        email: field.type === 'email',
        minLength: field.getAttribute('minlength'),
        maxLength: field.getAttribute('maxlength'),
        pattern: field.getAttribute('pattern')
      };
      
      this.messages[name] = field.dataset.error || '';
    });
  }
  
  bindEvents() {
    this.fields.forEach(field => {
      field.addEventListener('blur', () => this.validateField(field));
      field.addEventListener('input', () => {
        if (field.classList.contains('error')) {
          this.validateField(field);
        }
      });
    });
    
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  validateField(field) {
    const name = field.name;
    const value = field.value.trim();
    const rule = this.rules[name];
    
    let isValid = true;
    let errorMessage = '';
    
    if (rule.required && !value) {
      isValid = false;
      errorMessage = this.messages[name] || `${name} is required`;
    }
    
    if (isValid && rule.email && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }
    
    if (isValid && rule.minLength && value.length < parseInt(rule.minLength)) {
      isValid = false;
      errorMessage = `${name} must be at least ${rule.minLength} characters`;
    }
    
    if (isValid && rule.maxLength && value.length > parseInt(rule.maxLength)) {
      isValid = false;
      errorMessage = `${name} must not exceed ${rule.maxLength} characters`;
    }
    
    if (isValid && rule.pattern && value) {
      const pattern = new RegExp(rule.pattern);
      if (!pattern.test(value)) {
        isValid = false;
        errorMessage = this.messages[name] || 'Invalid format';
      }
    }
    
    this.updateFieldStatus(field, isValid, errorMessage);
    return isValid;
  }
  
  updateFieldStatus(field, isValid, errorMessage) {
    const parent = field.closest('.form-group');
    const errorElement = parent?.querySelector('.error-message');
    
    if (!isValid) {
      field.classList.add('error');
      if (errorElement) {
        errorElement.textContent = errorMessage;
        errorElement.style.display = 'block';
      }
    } else {
      field.classList.remove('error');
      field.classList.add('success');
      if (errorElement) {
        errorElement.style.display = 'none';
      }
    }
  }
  
  validateForm() {
    let isValid = true;
    
    this.fields.forEach(field => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });
    
    return isValid;
  }
  
  handleSubmit(e) {
    if (!this.validateForm()) {
      e.preventDefault();
      return false;
    }
    
    return true;
  }
}

class ContactForm {
  constructor(form) {
    this.form = form;
    this.submitBtn = this.form.querySelector('button[type="submit"]');
    this.originalBtnText = this.submitBtn?.textContent;
    
    this.init();
  }
  
  init() {
    this.validator = new FormValidator(this.form);
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  async handleSubmit(e) {
    e.preventDefault();
    
    if (!this.validator.validateForm()) {
      return;
    }
    
    this.setLoading(true);
    
    const formData = new FormData(this.form);
    const data = Object.fromEntries(formData.entries());
    
    try {
      await this.submitForm(data);
      this.showSuccess();
      this.form.reset();
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.setLoading(false);
    }
  }
  
  async submitForm(data) {
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log('Form submitted:', data);
        resolve({ success: true });
      }, 1500);
    });
  }
  
  setLoading(isLoading) {
    if (this.submitBtn) {
      this.submitBtn.disabled = isLoading;
      this.submitBtn.textContent = isLoading ? 'Sending...' : this.originalBtnText;
    }
  }
  
  showSuccess() {
    this.showMessage('Message sent successfully!', 'success');
  }
  
  showError(message) {
    this.showMessage(message || 'Something went wrong. Please try again.', 'error');
  }
  
  showMessage(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    if (form.classList.contains('contact-form')) {
      new ContactForm(form);
    } else {
      new FormValidator(form);
    }
  });
});
