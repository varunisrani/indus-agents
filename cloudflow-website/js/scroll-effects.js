import { getElements, animateOnScroll } from './utils.js';

export function initScrollAnimations() {
  const fadeElements = getElements('.fade-in');
  const slideElements = getElements('.slide-up');
  
  animateOnScroll(fadeElements, (element) => {
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
  });
  
  animateOnScroll(slideElements, (element) => {
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
  });
}

export function initParallax() {
  const parallaxElements = getElements('.parallax');
  
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    
    parallaxElements.forEach(element => {
      const speed = element.dataset.speed || 0.5;
      const yPos = -(scrolled * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  });
}

export function setupLazyLoading() {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
}

export function initCounterAnimation() {
  const counters = getElements('.counter');
  
  const animateCounter = (element) => {
    const target = parseInt(element.dataset.target);
    const duration = parseInt(element.dataset.duration) || 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
      current += step;
      if (current < target) {
        element.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        element.textContent = target;
      }
    };
    
    updateCounter();
  };
  
  animateOnScroll(counters, animateCounter);
}
