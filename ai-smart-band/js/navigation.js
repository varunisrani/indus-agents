class Navigation {
  constructor() {
    this.navbar = document.querySelector('.navbar');
    this.mobileToggle = document.querySelector('.menu-toggle');
    this.mobileMenu = document.querySelector('.mobile-menu');
    this.dropdowns = document.querySelectorAll('.dropdown');
    this.isOpen = false;
    
    this.init();
  }
  
  init() {
    this.initMobileMenu();
    this.initDropdowns();
    this.initActiveLink();
    this.initKeyboardNav();
  }
  
  initMobileMenu() {
    if (!this.mobileToggle || !this.mobileMenu) return;
    
    this.mobileToggle.addEventListener('click', () => this.toggleMobileMenu());
    
    const closeBtn = this.mobileMenu.querySelector('.mobile-menu-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeMobileMenu());
    }
    
    const overlay = document.querySelector('.mobile-menu-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this.closeMobileMenu());
    }
    
    const mobileLinks = this.mobileMenu.querySelectorAll('.mobile-nav-link');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => this.closeMobileMenu());
    });
  }
  
  toggleMobileMenu() {
    this.isOpen = !this.isOpen;
    
    if (this.isOpen) {
      this.openMobileMenu();
    } else {
      this.closeMobileMenu();
    }
  }
  
  openMobileMenu() {
    this.mobileMenu.classList.add('open');
    document.body.style.overflow = 'hidden';
    this.isOpen = true;
  }
  
  closeMobileMenu() {
    this.mobileMenu.classList.remove('open');
    document.body.style.overflow = '';
    this.isOpen = false;
  }
  
  initDropdowns() {
    this.dropdowns.forEach(dropdown => {
      const trigger = dropdown.querySelector('.dropdown-trigger');
      const menu = dropdown.querySelector('.dropdown-menu');
      
      if (!trigger || !menu) return;
      
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleDropdown(dropdown);
      });
      
      trigger.addEventListener('mouseenter', () => {
        if (window.innerWidth > 768) {
          this.openDropdown(dropdown);
        }
      });
      
      dropdown.addEventListener('mouseleave', () => {
        if (window.innerWidth > 768) {
          this.closeDropdown(dropdown);
        }
      });
    });
    
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.dropdown')) {
        this.closeAllDropdowns();
      }
    });
  }
  
  toggleDropdown(dropdown) {
    const isOpen = dropdown.classList.contains('open');
    
    if (isOpen) {
      this.closeDropdown(dropdown);
    } else {
      this.openDropdown(dropdown);
    }
  }
  
  openDropdown(dropdown) {
    this.closeAllDropdowns();
    dropdown.classList.add('open');
  }
  
  closeDropdown(dropdown) {
    dropdown.classList.remove('open');
  }
  
  closeAllDropdowns() {
    this.dropdowns.forEach(dropdown => {
      dropdown.classList.remove('open');
    });
  }
  
  initActiveLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-link, .mobile-nav-link');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      
      if (href === currentPath || 
          (href === '/' && currentPath.includes('index.html')) ||
          (href !== '/' && currentPath.includes(href))) {
        link.classList.add('active');
      }
    });
  }
  
  initKeyboardNav() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeMobileMenu();
        this.closeAllDropdowns();
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new Navigation();
});
