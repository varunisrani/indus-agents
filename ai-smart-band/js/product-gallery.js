class ProductGallery {
  constructor(element) {
    this.gallery = element;
    this.mainImage = this.gallery.querySelector('.main-image img');
    this.thumbnails = this.gallery.querySelectorAll('.thumbnail');
    this.prevBtn = this.gallery.querySelector('.gallery-prev');
    this.nextBtn = this.gallery.querySelector('.gallery-next');
    this.currentIndex = 0;
    this.images = [];
    
    this.init();
  }
  
  init() {
    this.collectImages();
    this.initThumbnails();
    this.initNavigation();
    this.initKeyboard();
    this.initTouch();
  }
  
  collectImages() {
    this.thumbnails.forEach((thumb, index) => {
      this.images.push({
        src: thumb.dataset.src,
        thumb: thumb.querySelector('img').src
      });
    });
  }
  
  initThumbnails() {
    this.thumbnails.forEach((thumb, index) => {
      thumb.addEventListener('click', () => {
        this.goToSlide(index);
      });
    });
  }
  
  initNavigation() {
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => this.prevSlide());
    }
    
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', () => this.nextSlide());
    }
  }
  
  initKeyboard() {
    this.gallery.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        this.prevSlide();
      } else if (e.key === 'ArrowRight') {
        this.nextSlide();
      }
    });
  }
  
  initTouch() {
    let startX = 0;
    let endX = 0;
    
    this.gallery.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });
    
    this.gallery.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      this.handleSwipe();
    });
    
    const handleSwipe = () => {
      const diff = startX - endX;
      const threshold = 50;
      
      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          this.nextSlide();
        } else {
          this.prevSlide();
        }
      }
    };
  }
  
  goToSlide(index) {
    if (index < 0) index = this.images.length - 1;
    if (index >= this.images.length) index = 0;
    
    this.currentIndex = index;
    this.updateGallery();
  }
  
  prevSlide() {
    this.goToSlide(this.currentIndex - 1);
  }
  
  nextSlide() {
    this.goToSlide(this.currentIndex + 1);
  }
  
  updateGallery() {
    const imageData = this.images[this.currentIndex];
    
    this.mainImage.style.opacity = '0';
    
    setTimeout(() => {
      this.mainImage.src = imageData.src;
      this.mainImage.style.opacity = '1';
    }, 200);
    
    this.thumbnails.forEach((thumb, index) => {
      if (index === this.currentIndex) {
        thumb.classList.add('active');
      } else {
        thumb.classList.remove('active');
      }
    });
  }
}

class Lightbox {
  constructor() {
    this.lightbox = null;
    this.lightboxImg = null;
    this.closeBtn = null;
    this.images = [];
    this.currentIndex = 0;
    
    this.init();
  }
  
  init() {
    this.createLightbox();
    this.initTriggers();
  }
  
  createLightbox() {
    this.lightbox = document.createElement('div');
    this.lightbox.className = 'lightbox';
    this.lightbox.innerHTML = `
      <div class="lightbox-content">
        <button class="lightbox-close" aria-label="Close lightbox">&times;</button>
        <button class="lightbox-prev" aria-label="Previous image">&#8249;</button>
        <img class="lightbox-image" src="" alt="">
        <button class="lightbox-next" aria-label="Next image">&#8250;</button>
      </div>
    `;
    
    document.body.appendChild(this.lightbox);
    
    this.lightboxImg = this.lightbox.querySelector('.lightbox-image');
    this.closeBtn = this.lightbox.querySelector('.lightbox-close');
    const prevBtn = this.lightbox.querySelector('.lightbox-prev');
    const nextBtn = this.lightbox.querySelector('.lightbox-next');
    
    this.closeBtn.addEventListener('click', () => this.close());
    this.lightbox.addEventListener('click', (e) => {
      if (e.target === this.lightbox) this.close();
    });
    
    prevBtn.addEventListener('click', () => this.prev());
    nextBtn.addEventListener('click', () => this.next());
    
    document.addEventListener('keydown', (e) => {
      if (!this.lightbox.classList.contains('open')) return;
      
      if (e.key === 'Escape') this.close();
      if (e.key === 'ArrowLeft') this.prev();
      if (e.key === 'ArrowRight') this.next();
    });
  }
  
  initTriggers() {
    const triggers = document.querySelectorAll('[data-lightbox]');
    
    triggers.forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const src = trigger.dataset.lightbox || trigger.href;
        this.open(src);
      });
    });
  }
  
  open(src) {
    this.lightboxImg.src = src;
    this.lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  
  close() {
    this.lightbox.classList.remove('open');
    document.body.style.overflow = '';
  }
  
  prev() {
    this.lightboxImg.style.transform = 'translateX(-100%)';
    setTimeout(() => {
      this.lightboxImg.src = this.images[this.currentIndex - 1];
      this.lightboxImg.style.transform = 'translateX(100%)';
      setTimeout(() => {
        this.lightboxImg.style.transform = 'translateX(0)';
      }, 50);
    }, 300);
  }
  
  next() {
    this.lightboxImg.style.transform = 'translateX(100%)';
    setTimeout(() => {
      this.lightboxImg.src = this.images[this.currentIndex + 1];
      this.lightboxImg.style.transform = 'translateX(-100%)';
      setTimeout(() => {
        this.lightboxImg.style.transform = 'translateX(0)';
      }, 50);
    }, 300);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const galleries = document.querySelectorAll('.product-gallery');
  galleries.forEach(gallery => new ProductGallery(gallery));
  
  new Lightbox();
});
