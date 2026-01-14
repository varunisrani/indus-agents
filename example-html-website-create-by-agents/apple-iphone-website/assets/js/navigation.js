// Apple iPhone Website - Navigation JavaScript

class MobileNavigation {
    constructor() {
        this.header = document.getElementById('header');
        this.navToggle = document.getElementById('nav-toggle');
        this.navLinks = document.querySelector('.nav-links');
        this.searchIcon = document.querySelector('.nav-search');
        this.bagIcon = document.querySelector('.nav-bag');
        
        this.isOpen = false;
        this.init();
    }
    
    init() {
        if (this.navToggle) {
            this.navToggle.addEventListener('click', () => this.toggleNavigation());
        }
        
        // Close navigation when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.header.contains(e.target)) {
                this.closeNavigation();
            }
        });
        
        // Close navigation when window is resized to desktop
        window.addEventListener('resize', this.debounce(() => {
            if (window.innerWidth > 1023) {
                this.closeNavigation();
            }
        }, 250));
    }
    
    toggleNavigation() {
        if (this.isOpen) {
            this.closeNavigation();
        } else {
            this.openNavigation();
        }
    }
    
    openNavigation() {
        this.header.classList.add('nav-open');
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
        this.animateToggle(true);
    }
    
    closeNavigation() {
        this.header.classList.remove('nav-open');
        this.isOpen = false;
        document.body.style.overflow = '';
        this.animateToggle(false);
    }
    
    animateToggle(isOpening) {
        if (!this.navToggle) return;
        
        const spans = this.navToggle.querySelectorAll('span');
        if (isOpening) {
            // Animate to X
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        } else {
            // Animate back to hamburger
            spans.forEach(span => span.style.transform = 'none');
            spans[1].style.opacity = '1';
        }
    }
    
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
    }
}

// Initialize mobile navigation
document.addEventListener('DOMContentLoaded', function() {
    new MobileNavigation();
});

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchIcon = document.querySelector('.nav-search');
    
    if (searchIcon) {
        searchIcon.addEventListener('click', function(e) {
            e.preventDefault();
            showSearchOverlay();
        });
    }
});

function showSearchOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    overlay.innerHTML = `
        <div class="search-container">
            <div class="search-header">
                <span>Search Products</span>
                <button class="close-search" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="search-body">
                <input type="text" class="search-input" placeholder="Search iPhone models, features..." autofocus>
                <div class="search-results"></div>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Handle search input
    const searchInput = overlay.querySelector('.search-input');
    const searchResults = overlay.querySelector('.search-results');
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length > 0) {
            // Simulate search results
            const results = [
                'iPhone 15 Pro Max',
                'iPhone 15 Pro',
                'iPhone 15',
                'iPhone SE',
                'iPhone Accessories'
            ].filter(item => item.toLowerCase().includes(query));
            
            searchResults.innerHTML = results.map(item => 
                `<div class="search-result-item">${item}</div>`
            ).join('');
            searchResults.style.display = 'block';
        } else {
            searchResults.style.display = 'none';
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            overlay.remove();
        }
    });
}

// Shopping bag functionality
document.addEventListener('DOMContentLoaded', function() {
    const bagIcon = document.querySelector('.nav-bag');
    
    if (bagIcon) {
        bagIcon.addEventListener('click', function(e) {
            e.preventDefault();
            showBagOverlay();
        });
    }
});

function showBagOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'bag-overlay';
    overlay.innerHTML = `
        <div class="bag-container">
            <div class="bag-header">
                <span>Your Bag</span>
                <button class="close-bag" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="bag-body">
                <div class="empty-bag">
                    <span style="font-size: 48px;">🛍️</span>
                    <p>Your bag is empty</p>
                    <a href="models.html" class="btn btn-primary">Shop iPhone</a>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            overlay.remove();
        }
    });
}

// Language switcher
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const currentLanguage = navigator.language || 'en-US';
    
    // Add language data attribute
    body.setAttribute('data-language', currentLanguage);
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        body.classList.remove('keyboard-navigation');
    });
});