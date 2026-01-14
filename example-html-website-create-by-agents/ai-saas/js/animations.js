class ScrollAnimations {
  constructor() {
    this.init();
  }

  init() {
    this.initFadeInAnimations();
    this.initParallaxEffects();
    this.initTextReveal();
  }

  initFadeInAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);
    
    fadeElements.forEach(el => observer.observe(el));
  }

  initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      
      parallaxElements.forEach(el => {
        const speed = el.dataset.parallax || 0.5;
        const yPos = -(scrolled * speed);
        el.style.transform = `translateY(${yPos}px)`;
      });
    });
  }

  initTextReveal() {
    const revealElements = document.querySelectorAll('[data-reveal]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
        }
      });
    }, { threshold: 0.5 });
    
    revealElements.forEach(el => observer.observe(el));
  }
}

class CounterAnimation {
  constructor() {
    this.counters = document.querySelectorAll('.counter');
    this.init();
  }

  init() {
    const observerOptions = {
      threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    this.counters.forEach(counter => observer.observe(counter));
  }

  animateCounter(counter) {
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
  }
}

class Carousel {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      autoplay: options.autoplay || false,
      interval: options.interval || 5000,
      showDots: options.showDots !== false,
      showArrows: options.showArrows !== false
    };
    this.currentSlide = 0;
    this.slides = container.querySelectorAll('.slide');
    this.init();
  }

  init() {
    if (this.slides.length === 0) return;

    this.createControls();
    this.showSlide(0);
    
    if (this.options.autoplay) {
      this.startAutoplay();
    }
  }

  createControls() {
    if (this.options.showArrows) {
      const prevBtn = document.createElement('button');
      prevBtn.className = 'carousel-prev';
      prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
      prevBtn.addEventListener('click', () => this.prev());
      
      const nextBtn = document.createElement('button');
      nextBtn.className = 'carousel-next';
      nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
      nextBtn.addEventListener('click', () => this.next());
      
      this.container.appendChild(prevBtn);
      this.container.appendChild(nextBtn);
    }

    if (this.options.showDots) {
      const dotsContainer = document.createElement('div');
      dotsContainer.className = 'carousel-dots';
      
      this.slides.forEach((_, index) => {
        const dot = document.createElement('button');
        dot.className = 'carousel-dot';
        dot.addEventListener('click', () => this.goTo(index));
        dotsContainer.appendChild(dot);
      });
      
      this.container.appendChild(dotsContainer);
      this.dots = dotsContainer.querySelectorAll('.carousel-dot');
    }
  }

  showSlide(index) {
    this.slides.forEach((slide, i) => {
      slide.style.display = i === index ? 'block' : 'none';
    });
    
    if (this.dots) {
      this.dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
    }
    
    this.currentSlide = index;
  }

  next() {
    const next = (this.currentSlide + 1) % this.slides.length;
    this.showSlide(next);
  }

  prev() {
    const prev = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
    this.showSlide(prev);
  }

  goTo(index) {
    this.showSlide(index);
  }

  startAutoplay() {
    this.autoplayInterval = setInterval(() => this.next(), this.options.interval);
  }

  stopAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  new ScrollAnimations();
  new CounterAnimation();
  
  const carousels = document.querySelectorAll('.carousel');
  carousels.forEach(carousel => {
    new Carousel(carousel, { autoplay: true });
  });
});