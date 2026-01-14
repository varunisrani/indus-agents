import Navigation from './navigation.js';
import { setupContactForm } from './form-validation.js';
import { initScrollAnimations, initParallax, setupLazyLoading, initCounterAnimation } from './scroll-effects.js';
import { initAccordions } from './accordion.js';
import { initTabs } from './tabs.js';
import { initModals } from './modal.js';
import { initCarousels } from './carousel.js';

document.addEventListener('DOMContentLoaded', () => {
  new Navigation();
  
  setupContactForm();
  
  initScrollAnimations();
  initParallax();
  setupLazyLoading();
  initCounterAnimation();
  
  initAccordions();
  initTabs();
  initModals();
  initCarousels();
  
  console.log('CloudFlow website initialized');
});
