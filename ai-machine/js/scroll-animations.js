// Scroll Animations Module - AI Machine

export function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  animatedElements.forEach(el => observer.observe(el));

  initParallax();
  initCounters();
  initProgressBars();
}

function initParallax() {
  const parallaxElements = document.querySelectorAll('.parallax');

  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;

    parallaxElements.forEach(el => {
      const rate = el.dataset.rate || 0.5;
      el.style.transform = `translateY(${scrolled * rate}px)`;
    });
  });
}

function initCounters() {
  const counters = document.querySelectorAll('.counter');

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counter = entry.target;
        const target = parseInt(counter.dataset.target);
        const duration = parseInt(counter.dataset.duration) || 2000;
        const increment = target / (duration / 16);

        let current = 0;
        const updateCounter = () => {
          current += increment;
          if (current < target) {
            counter.textContent = Math.ceil(current);
            requestAnimationFrame(updateCounter);
          } else {
            counter.textContent = target;
          }
        };

        updateCounter();
        counterObserver.unobserve(counter);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => counterObserver.observe(counter));
}

function initProgressBars() {
  const progressBars = document.querySelectorAll('.progress-bar-fill');

  const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const target = bar.dataset.progress || bar.style.width;
        bar.style.width = target;
        progressObserver.unobserve(bar);
      }
    });
  }, { threshold: 0.5 });

  progressBars.forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0';
    bar.dataset.progress = target;
    progressObserver.observe(bar);
  });
}
