class ScrollAnimations {
  constructor() {
    this.animatedElements = document.querySelectorAll('.animate-on-scroll');
    this.parallaxElements = document.querySelectorAll('.parallax');
    this.counters = document.querySelectorAll('.counter');
    this.progressBars = document.querySelectorAll('.progress-bar-fill');
    
    this.init();
  }
  
  init() {
    this.initIntersectionObserver();
    this.initParallax();
    this.initCounters();
    this.initProgressBars();
  }
  
  initIntersectionObserver() {
    const options = {
      root: null,
      rootMargin: '0px 0px -100px 0px',
      threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateElement(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, options);
    
    this.animatedElements.forEach(el => observer.observe(el));
  }
  
  animateElement(element) {
    element.classList.add('is-visible');
    
    const animationType = element.dataset.animation || 'fade-in-up';
    element.style.animationName = animationType;
    element.style.animationDuration = element.dataset.duration || '0.6s';
    element.style.animationDelay = element.dataset.delay || '0s';
    element.style.animationFillMode = 'both';
  }
  
  initParallax() {
    if (this.parallaxElements.length === 0) return;
    
    let ticking = false;
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          this.updateParallax();
          ticking = false;
        });
        ticking = true;
      }
    });
  }
  
  updateParallax() {
    const scrolled = window.pageYOffset;
    
    this.parallaxElements.forEach(el => {
      const rate = el.dataset.rate || 0.5;
      const offset = scrolled * rate;
      el.style.transform = `translateY(${offset}px)`;
    });
  }
  
  initCounters() {
    if (this.counters.length === 0) return;
    
    const observerOptions = {
      root: null,
      rootMargin: '0px',
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
    const target = parseInt(counter.dataset.target);
    const duration = parseInt(counter.dataset.duration) || 2000;
    const startTime = performance.now();
    
    const updateCounter = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(easeOut * target);
      
      counter.textContent = current.toLocaleString();
      
      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target.toLocaleString();
      }
    };
    
    requestAnimationFrame(updateCounter);
  }
  
  initProgressBars() {
    if (this.progressBars.length === 0) return;
    
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateProgressBar(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    this.progressBars.forEach(bar => observer.observe(bar));
  }
  
  animateProgressBar(bar) {
    const target = parseInt(bar.dataset.target) || 100;
    bar.style.width = `${target}%`;
  }
}

class ScrollReveal {
  constructor(options = {}) {
    this.defaults = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px',
      delay: 0,
      duration: 600,
      distance: '30px'
    };
    
    this.options = { ...this.defaults, ...options };
    this.elements = document.querySelectorAll('[data-reveal]');
    
    this.init();
  }
  
  init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.reveal(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: this.options.threshold,
      rootMargin: this.options.rootMargin
    });
    
    this.elements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = `translateY(${this.options.distance})`;
      el.style.transition = `opacity ${this.options.duration}ms ease, transform ${this.options.duration}ms ease`;
      observer.observe(el);
    });
  }
  
  reveal(element) {
    const delay = element.dataset.delay || this.options.delay;
    
    setTimeout(() => {
      element.style.opacity = '1';
      element.style.transform = 'translateY(0)';
    }, delay);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new ScrollAnimations();
  
  window.ScrollReveal = ScrollReveal;
});
