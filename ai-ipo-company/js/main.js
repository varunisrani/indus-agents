// ===== Mobile Navigation =====
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a nav link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// ===== Back to Top Button =====
const backToTopButton = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

if (backToTopButton) {
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ===== Animated Statistics Counter =====
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

// Intersection Observer for statistics animation
const statNumbers = document.querySelectorAll('.stat-number[data-target]');
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = parseInt(entry.target.getAttribute('data-target'));
            animateCounter(entry.target, target);
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

statNumbers.forEach(stat => statsObserver.observe(stat));

// ===== Testimonial Slider =====
const testimonialCards = document.querySelectorAll('.testimonial-card');
const dots = document.querySelectorAll('.dot');
let currentTestimonial = 0;

function showTestimonial(index) {
    testimonialCards.forEach(card => card.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    testimonialCards[index].classList.add('active');
    dots[index].classList.add('active');
    currentTestimonial = index;
}

function nextTestimonial() {
    currentTestimonial = (currentTestimonial + 1) % testimonialCards.length;
    showTestimonial(currentTestimonial);
}

dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        showTestimonial(index);
    });
});

// Auto-advance testimonials
if (testimonialCards.length > 0) {
    setInterval(nextTestimonial, 5000);
}

// ===== FAQ Accordion =====
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    
    if (question) {
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                otherItem.classList.remove('active');
            });
            
            // Toggle current item
            if (!isActive) {
                item.classList.add('active');
            }
        });
    }
});

// ===== Contact Form Handling =====
const contactForm = document.getElementById('contactForm');
const formSuccess = document.getElementById('formSuccess');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Simulate form submission
        const submitButton = contactForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        submitButton.textContent = 'Sending...';
        submitButton.disabled = true;
        
        setTimeout(() => {
            contactForm.style.display = 'none';
            formSuccess.style.display = 'block';
            
            // Reset form
            contactForm.reset();
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }, 1500);
    });
}

// ===== Newsletter Form =====
const newsletterForm = document.getElementById('newsletterForm');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const input = newsletterForm.querySelector('input[type="email"]');
        const button = newsletterForm.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        button.textContent = 'Subscribing...';
        button.disabled = true;
        
        setTimeout(() => {
            button.textContent = '✓ Subscribed!';
            button.style.backgroundColor = '#28a745';
            input.value = '';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.backgroundColor = '';
                button.disabled = false;
            }, 3000);
        }, 1500);
    });
}

// ===== Smooth Scroll for Anchor Links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        if (href !== '#' && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        }
    });
});

// ===== Scroll Animations =====
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.service-card, .value-card, .team-card, .pipeline-card, .success-card, .sector-card');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Initialize scroll animations
const animatedElements = document.querySelectorAll('.service-card, .value-card, .team-card, .pipeline-card, .success-card, .sector-card');
animatedElements.forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
});

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);

// ===== Active Navigation Highlight =====
const sections = document.querySelectorAll('section');
const navLinksArray = Array.from(navLinks);

window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    navLinksArray.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// ===== Form Validation =====
const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

const validatePhone = (phone) => {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone);
};

// Add validation to contact form
if (contactForm) {
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            if (emailInput.value && !validateEmail(emailInput.value)) {
                emailInput.style.borderColor = '#dc3545';
            } else {
                emailInput.style.borderColor = '';
            }
        });
    }
    
    if (phoneInput) {
        phoneInput.addEventListener('blur', () => {
            if (phoneInput.value && !validatePhone(phoneInput.value)) {
                phoneInput.style.borderColor = '#dc3545';
            } else {
                phoneInput.style.borderColor = '';
            }
        });
    }
}

// ===== Loading Animation =====
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// ===== Console Welcome Message =====
console.log('%c🚀 AI IPO Website', 'font-size: 24px; font-weight: bold; color: #0A2463;');
console.log('%cTransforming AI Innovation into Public Success', 'font-size: 14px; color: #3E92CC;');
console.log('%cBuilt with HTML, CSS, and JavaScript', 'font-size: 12px; color: #666;');

// ===== Performance Optimization: Debounce Function =====
function debounce(func, wait = 20) {
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

// Apply debounce to scroll events
const debouncedAnimateOnScroll = debounce(animateOnScroll, 20);
window.removeEventListener('scroll', animateOnScroll);
window.addEventListener('scroll', debouncedAnimateOnScroll);

// ===== Local Storage for Form Data =====
if (contactForm) {
    const formInputs = contactForm.querySelectorAll('input, select, textarea');
    
    // Load saved data
    formInputs.forEach(input => {
        const savedValue = localStorage.getItem(`ai-ipo-${input.name}`);
        if (savedValue && input.type !== 'checkbox') {
            input.value = savedValue;
        }
    });
    
    // Save data on input
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.type !== 'checkbox') {
                localStorage.setItem(`ai-ipo-${input.name}`, input.value);
            }
        });
    });
    
    // Clear saved data on form submit
    contactForm.addEventListener('submit', () => {
        formInputs.forEach(input => {
            localStorage.removeItem(`ai-ipo-${input.name}`);
        });
    });
}

// ===== Dynamic Year in Footer =====
const footerYear = document.querySelector('.footer-bottom p');
if (footerYear) {
    const currentYear = new Date().getFullYear();
    footerYear.textContent = footerYear.textContent.replace('2025', currentYear);
}

// ===== Service Cards Hover Effect Enhancement =====
const serviceCards = document.querySelectorAll('.service-card');
serviceCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// ===== Pipeline Status Color Coding =====
const pipelineStatuses = document.querySelectorAll('.pipeline-status');
pipelineStatuses.forEach(status => {
    if (status.classList.contains('status-roadshow')) {
        status.style.animation = 'pulse 2s infinite';
    }
});

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
`;
document.head.appendChild(style);

// ===== Initialize on DOM Ready =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ AI IPO Website loaded successfully');
    
    // Check if all critical elements are present
    const criticalElements = [
        '.header',
        '.hero',
        '.footer'
    ];
    
    criticalElements.forEach(selector => {
        const element = document.querySelector(selector);
        if (!element) {
            console.warn(`⚠️ Missing critical element: ${selector}`);
        }
    });
});

// ===== Export functions for potential external use =====
window.AIIPO = {
    animateCounter,
    showTestimonial,
    validateEmail,
    validatePhone
};
