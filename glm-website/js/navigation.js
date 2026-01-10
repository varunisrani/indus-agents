document.addEventListener('DOMContentLoaded', function() {
  initMobileMenu();
  initStickyHeader();
  initSmoothScroll();
});

function initMobileMenu() {
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('nav');
  const navLinks = document.querySelectorAll('nav a');

  if (!menuToggle || !navMenu) return;

  menuToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    toggleMenu();
  });

  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      closeMenu();
    });
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('header')) {
      closeMenu();
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMenu();
    }
  });
}

function toggleMenu() {
  const navMenu = document.querySelector('nav');
  const menuToggle = document.querySelector('.menu-toggle');

  if (!navMenu || !menuToggle) return;

  navMenu.classList.toggle('active');

  const isOpen = navMenu.classList.contains('active');
  menuToggle.textContent = isOpen ? '✕' : '☰';
  menuToggle.setAttribute('aria-expanded', isOpen);

  document.body.style.overflow = isOpen ? 'hidden' : '';
}

function closeMenu() {
  const navMenu = document.querySelector('nav');
  const menuToggle = document.querySelector('.menu-toggle');

  if (!navMenu || !menuToggle) return;

  navMenu.classList.remove('active');
  menuToggle.textContent = '☰';
  menuToggle.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

function initStickyHeader() {
  const header = document.querySelector('header');
  if (!header) return;

  let lastScroll = 0;
  const scrollThreshold = 50;

  window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;

    if (currentScroll > scrollThreshold) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  });
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');

      if (href === '#' || href === '#top') {
        e.preventDefault();
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
        return;
      }

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();

        const header = document.querySelector('header');
        const headerHeight = header ? header.offsetHeight : 80;

        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerHeight;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        target.focus({ preventScroll: true });
      }
    });
  });
}

function handleResize() {
  const navMenu = document.querySelector('nav');
  const menuToggle = document.querySelector('.menu-toggle');

  if (window.innerWidth > 768 && navMenu) {
    navMenu.classList.remove('active');
    if (menuToggle) {
      menuToggle.textContent = '☰';
      menuToggle.setAttribute('aria-expanded', 'false');
    }
    document.body.style.overflow = '';
  }
}

let resizeTimer;
window.addEventListener('resize', function() {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(handleResize, 250);
});
