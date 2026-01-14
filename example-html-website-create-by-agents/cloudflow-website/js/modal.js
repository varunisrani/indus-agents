export class Modal {
  constructor(element) {
    this.modal = element;
    this.openButton = document.querySelector(`[data-modal="${this.modal.id}"]`);
    this.closeButton = this.modal.querySelector('.modal-close');
    this.overlay = this.modal.querySelector('.modal-overlay');
    this.init();
  }
  
  init() {
    if (this.openButton) {
      this.openButton.addEventListener('click', () => this.open());
    }
    
    if (this.closeButton) {
      this.closeButton.addEventListener('click', () => this.close());
    }
    
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.close());
    }
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
  }
  
  open() {
    this.modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    setTimeout(() => {
      this.modal.classList.add('active');
    }, 10);
  }
  
  close() {
    this.modal.classList.remove('active');
    setTimeout(() => {
      this.modal.style.display = 'none';
      document.body.style.overflow = '';
    }, 300);
  }
  
  isOpen() {
    return this.modal.classList.contains('active');
  }
}

export function initModals() {
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => new Modal(modal));
}
