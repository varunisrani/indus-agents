export class FormValidator {
  constructor(formElement) {
    this.form = formElement;
    this.inputs = this.form.querySelectorAll('input, textarea, select');
    this.rules = {};
    this.init();
  }
  
  init() {
    this.inputs.forEach(input => {
      input.addEventListener('blur', () => this.validateField(input));
      input.addEventListener('input', () => this.clearError(input));
    });
    
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  addRule(fieldName, rule) {
    this.rules[fieldName] = { ...this.rules[fieldName], ...rule };
  }
  
  validateField(input) {
    const name = input.name;
    const value = input.value.trim();
    const rules = this.rules[name];
    
    if (!rules) return true;
    
    if (rules.required && !value) {
      this.showError(input, rules.errorMessage || 'This field is required');
      return false;
    }
    
    if (rules.email && value && !this.isValidEmail(value)) {
      this.showError(input, 'Please enter a valid email address');
      return false;
    }
    
    if (rules.minLength && value.length < rules.minLength) {
      this.showError(input, `Minimum length is ${rules.minLength} characters`);
      return false;
    }
    
    if (rules.pattern && !rules.pattern.test(value)) {
      this.showError(input, rules.errorMessage || 'Invalid format');
      return false;
    }
    
    this.clearError(input);
    return true;
  }
  
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
  
  showError(input, message) {
    const formGroup = input.closest('.form-group');
    const errorElement = formGroup.querySelector('.error-message') || 
                        document.createElement('span');
    
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    errorElement.style.color = 'var(--error)';
    errorElement.style.fontSize = 'var(--text-sm)';
    errorElement.style.marginTop = 'var(--space-2)';
    errorElement.style.display = 'block';
    
    if (!formGroup.querySelector('.error-message')) {
      formGroup.appendChild(errorElement);
    }
    
    input.style.borderColor = 'var(--error)';
  }
  
  clearError(input) {
    const formGroup = input.closest('.form-group');
    const errorElement = formGroup.querySelector('.error-message');
    
    if (errorElement) {
      errorElement.remove();
    }
    
    input.style.borderColor = '';
  }
  
  handleSubmit(e) {
    e.preventDefault();
    let isValid = true;
    
    this.inputs.forEach(input => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });
    
    if (isValid) {
      const formData = new FormData(this.form);
      const data = Object.fromEntries(formData.entries());
      
      const submitEvent = new CustomEvent('formValid', { detail: data });
      this.form.dispatchEvent(submitEvent);
    }
  }
}

export function setupContactForm() {
  const contactForm = document.getElementById('contact-form');
  if (!contactForm) return;
  
  const validator = new FormValidator(contactForm);
  
  validator.addRule('name', {
    required: true,
    minLength: 2,
    errorMessage: 'Please enter your name'
  });
  
  validator.addRule('email', {
    required: true,
    email: true,
    errorMessage: 'Please enter a valid email address'
  });
  
  validator.addRule('subject', {
    required: true,
    errorMessage: 'Please select a subject'
  });
  
  validator.addRule('message', {
    required: true,
    minLength: 10,
    errorMessage: 'Please enter a message (at least 10 characters)'
  });
  
  contactForm.addEventListener('formValid', (e) => {
    const data = e.detail;
    console.log('Form submitted:', data);
    
    alert('Thank you for your message! We will get back to you soon.');
    contactForm.reset();
  });
}
