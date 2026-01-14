export class Accordion {
  constructor(element) {
    this.accordion = element;
    this.items = this.accordion.querySelectorAll('.accordion-item');
    this.init();
  }
  
  init() {
    this.items.forEach(item => {
      const header = item.querySelector('.accordion-header');
      const content = item.querySelector('.accordion-content');
      
      if (content) {
        content.style.maxHeight = '0';
        content.style.overflow = 'hidden';
        content.style.transition = 'max-height 0.3s ease-out';
      }
      
      header.addEventListener('click', () => {
        this.toggleItem(item);
      });
    });
  }
  
  toggleItem(item) {
    const content = item.querySelector('.accordion-content');
    const isOpen = item.classList.contains('active');
    
    this.items.forEach(otherItem => {
      if (otherItem !== item) {
        otherItem.classList.remove('active');
        const otherContent = otherItem.querySelector('.accordion-content');
        if (otherContent) {
          otherContent.style.maxHeight = '0';
        }
      }
    });
    
    if (!isOpen) {
      item.classList.add('active');
      content.style.maxHeight = content.scrollHeight + 'px';
    } else {
      item.classList.remove('active');
      content.style.maxHeight = '0';
    }
  }
}

export function initAccordions() {
  const accordions = document.querySelectorAll('.accordion');
  accordions.forEach(accordion => new Accordion(accordion));
}
