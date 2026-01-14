// Form Handler JavaScript
// Handles contact form validation and submission

document.addEventListener('DOMContentLoaded', function() {
    initContactForm();
});

// Contact form validation
function initContactForm() {
    const form = document.getElementById('contactForm');

    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Clear previous errors
        clearErrors();

        // Get form values
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const subject = document.getElementById('subject').value;
        const message = document.getElementById('message').value.trim();

        // Validate
        let isValid = true;

        if (name === '') {
            showError('nameError', 'Please enter your name');
            isValid = false;
        }

        if (email === '') {
            showError('emailError', 'Please enter your email');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('emailError', 'Please enter a valid email address');
            isValid = false;
        }

        if (subject === '') {
            showError('subjectError', 'Please select a subject');
            isValid = false;
        }

        if (message === '') {
            showError('messageError', 'Please enter your message');
            isValid = false;
        } else if (message.length < 10) {
            showError('messageError', 'Message must be at least 10 characters');
            isValid = false;
        }

        if (isValid) {
            submitForm(form);
        }
    });
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

// Clear all errors
function clearErrors() {
    const errorElements = document.querySelectorAll('.form-error');
    errorElements.forEach(el => {
        el.textContent = '';
    });
}

// Submit form
function submitForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    // Show loading state
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        // Hide form
        form.style.display = 'none';

        // Show success message
        const successMessage = document.getElementById('formSuccess');
        if (successMessage) {
            successMessage.style.display = 'block';
        }

        // Reset form
        form.reset();
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }, 1500);
}
