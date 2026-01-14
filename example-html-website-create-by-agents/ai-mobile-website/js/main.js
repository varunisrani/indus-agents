// Main JavaScript File
// Initialize all functionality when DOM is ready

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Mobile website initialized');

    // Initialize smooth scroll
    initSmoothScroll();

    // Initialize header scroll effect
    initHeaderScroll();

    // Initialize tabs for solutions page
    initTabs();

    // Update current year in footer
    updateCurrentYear();
});

// Smooth scroll for anchor links
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Skip if it's just "#"
            if (href === '#' || href === '#!') return;

            const target = document.querySelector(href);

            if (target) {
                e.preventDefault();

                // Calculate header height
                const header = document.querySelector('.header');
                const headerHeight = header ? header.offsetHeight : 0;

                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Update focus for accessibility
                target.focus({ preventScroll: true });
            }
        });
    });
}

// Header scroll effect
function initHeaderScroll() {
    const header = document.querySelector('.header');

    if (!header) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });
}

// Utility: Debounce function
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

// Utility: Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Tab functionality for solutions page
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');

    if (tabButtons.length === 0) return;

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Remove active class from all buttons and panes
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('tab-btn--active');
            });
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('tab-pane--active');
            });

            // Add active class to clicked button
            this.classList.add('tab-btn--active');

            // Show corresponding tab pane
            const targetPane = document.getElementById(tabId);
            if (targetPane) {
                targetPane.classList.add('tab-pane--active');
            }
        });
    });
}

// Update current year in footer
function updateCurrentYear() {
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
}

// Export functions for use in other files
window.AIMobile = {
    debounce,
    throttle
};
