import { getElement, getElements, addClass, removeClass, toggleClass } from './utils.js';

class Navigation {
  constructor() {
    this.header = getElement('header');
    this.mobileToggle = getElement('.mobile-toggle');
    this.mobileMenu = getElement('.mobile-menu');
    this.mobileOverlay = getElement('.mobile-overlay');
    this.navLinks = getElements('.nav-link');
    
    this.init();
  }
  
  init() {
    this.handleScroll();
    this.setupMobileMenu();
    this.setupActiveLinks();
  }
  
  handleScroll() {
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;
      
      if (currentScroll > 50) {
        addClass(this.header, 'scrolled');
      } else {
        removeClass(this.header, 'scrolled');
      }
      
      lastScroll = currentScroll;
    });
  }
  
  setupMobileMenu() {
    if (this.mobileToggle) {
      this.mobileToggle.addEventListener('click', () => {
        this.toggleMobileMenu();
      });
    }
    
    if (this.mobileOverlay) {
      this.mobileOverlay.addEventListener('click', () => {
        this.closeMobileMenu();
      });
    }
    
    const mobileLinks = getElements('.mobile-menu a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        this.closeMobileMenu();
      });
    });
  }
  
  toggleMobileMenu() {
    toggleClass(this.mobileMenu, 'active');
    toggleClass(this.mobileOverlay, 'active');
    document.body.style.overflow = this.mobileMenu.classList.contains('active') 
      ? 'hidden' 
      : '';
  }
  
  closeMobileMenu() {
    removeClass(this.mobileMenu, 'active');
    removeClass(this.mobileOverlay, 'active');
    document.body.style.overflow = '';
  }
  
  setupActiveLinks() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    this.navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPage || (currentPage === '' && href === 'index.html')) {
        addClass(link, 'active');
      }
    });
  }
}

export default Navigation;
