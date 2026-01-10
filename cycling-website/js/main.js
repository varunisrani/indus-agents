document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    initBikeFilters();
    initModal();
    initCounters();
    initContactForm();
    initNewsletterForm();
    initAccordion();
});

function initScrollAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(el => observer.observe(el));
}

function initBikeFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const bikeCards = document.querySelectorAll('.bike-card');
    
    if (!filterBtns.length) return;
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            bikeCards.forEach(card => {
                const category = card.getAttribute('data-category');
                
                if (filter === 'all' || category === filter) {
                    card.classList.remove('hidden');
                    card.style.animation = 'fadeInUp 0.5s ease forwards';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

function initModal() {
    const modal = document.getElementById('bike-modal');
    const viewBtns = document.querySelectorAll('.view-details');
    const closeBtn = document.querySelector('.modal-close');
    
    if (!modal) return;
    
    const bikeData = {
        'pro-road': {
            image: 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800',
            title: 'Pro Road Series',
            description: 'The ultimate road machine for serious cyclists. Featuring a lightweight carbon frame, full Shimano Ultegra groupset, and carbon wheels designed for maximum speed and efficiency.',
            specs: ['Carbon Frame', 'Shimano Ultegra 22-speed', 'Carbon Wheels', ' hydraulic Disc Brakes'],
            price: '$2,499'
        },
        'trail-blazer': {
            image: 'https://images.unsplash.com/photo-1576435728678-38d01d52e38b?w=800',
            title: 'Trail Blazer MTB',
            description: 'Conquer any trail with this full-suspension mountain bike. Built for extreme terrain with 150mm travel, 29-inch wheels, and a rugged aluminum frame.',
            specs: ['Aluminum Frame', 'SRAM GX 12-speed', 'Full Suspension', '29-inch Wheels'],
            price: '$3,199'
        },
        'city-commuter': {
            image: 'https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=800',
            title: 'City Commuter',
            description: 'The perfect companion for urban riding. Comfortable upright position, reliable components, and practical features for daily commuting.',
            specs: ['Steel Frame', 'Shimano Claris 16-speed', 'Rear Rack', 'Fenders Included'],
            price: '$899'
        },
        'e-mountain': {
            image: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
            title: 'E-Mountain Pro',
            description: 'Experience the trails like never before with our premium electric mountain bike. Powerful 85Nm motor, 500Wh battery, and full suspension.',
            specs: ['Carbon Frame', 'Bosch Performance Motor', '500Wh Battery', 'Full Suspension'],
            price: '$5,499'
        },
        'endurance-road': {
            image: 'https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=800',
            title: 'Endurance Road',
            description: 'Designed for long-distance comfort without sacrificing performance. Vibration-damping technology and relaxed geometry for all-day riding.',
            specs: ['Aluminum Frame', 'Shimano 105 22-speed', 'Carbon Fork', '28mm Tires'],
            price: '$1,799'
        },
        'junior-mountain': {
            image: 'https://images.unsplash.com/photo-1555952517-2e8e729e0b44?w=800',
            title: 'Junior Mountain',
            description: 'The perfect first mountain bike for young riders. Lightweight, durable, and designed to help kids develop their off-road skills safely.',
            specs: ['Aluminum Frame', 'Shimano Tourney 7-speed', 'Front Suspension', '24-inch Wheels'],
            price: '$449'
        }
    };
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const bikeId = this.getAttribute('data-bike');
            const bike = bikeData[bikeId];
            
            if (bike) {
                document.getElementById('modal-image').src = bike.image;
                document.getElementById('modal-title').textContent = bike.title;
                document.getElementById('modal-description').textContent = bike.description;
                document.getElementById('modal-price').textContent = bike.price;
                
                const specsContainer = document.getElementById('modal-specs');
                specsContainer.innerHTML = bike.specs.map(spec => 
                    `<span style="display: inline-block; background: var(--light-bg); padding: 8px 15px; border-radius: 20px; margin: 5px; font-size: 0.9rem;"><i class="fas fa-check" style="color: var(--success); margin-right: 5px;"></i>${spec}</span>`
                ).join('');
                
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    closeBtn.addEventListener('click', function() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    });
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

function initCounters() {
    const counters = document.querySelectorAll('.counter');
    
    if (!counters.length) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;
                
                const updateCounter = () => {
                    current += step;
                    if (current < target) {
                        counter.textContent = Math.floor(current).toLocaleString();
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target.toLocaleString() + '+';
                    }
                };
                
                updateCounter();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

function initContactForm() {
    const form = document.getElementById('contact-form');
    
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        let isValid = true;
        const formData = {};
        
        const formGroups = form.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const input = group.querySelector('input, textarea, select');
            const small = group.querySelector('small');
            
            group.classList.remove('error', 'success');
            small.textContent = '';
            
            if (input.hasAttribute('required') && !input.value.trim()) {
                group.classList.add('error');
                small.textContent = 'This field is required';
                isValid = false;
            } else if (input.type === 'email' && input.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value.trim())) {
                    group.classList.add('error');
                    small.textContent = 'Please enter a valid email address';
                    isValid = false;
                } else {
                    group.classList.add('success');
                }
            } else if (input.value.trim()) {
                group.classList.add('success');
            }
            
            formData[input.name] = input.value.trim();
        });
        
        if (isValid) {
            alert('Thank you for your message! We will get back to you soon.');
            form.reset();
            formGroups.forEach(group => group.classList.remove('success'));
        }
    });
}

function initNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    const message = document.getElementById('newsletter-message');
    
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = form.querySelector('input[type="email"]').value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (emailRegex.test(email)) {
            message.textContent = 'Thank you for subscribing! Check your inbox for confirmation.';
            message.style.color = 'var(--success)';
            form.reset();
        } else {
            message.textContent = 'Please enter a valid email address.';
            message.style.color = 'var(--error)';
        }
        
        setTimeout(() => {
            message.textContent = '';
        }, 5000);
    });
}

function initAccordion() {
    const accordionItems = document.querySelectorAll('.accordion-item');
    
    if (!accordionItems.length) return;
    
    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        
        header.addEventListener('click', function() {
            const isActive = item.classList.contains('active');
            
            accordionItems.forEach(i => i.classList.remove('active'));
            
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}