export class Carousel {
  constructor(element) {
    this.carousel = element;
    this.track = this.carousel.querySelector('.carousel-track');
    this.slides = this.carousel.querySelectorAll('.carousel-slide');
    this.prevButton = this.carousel.querySelector('.carousel-prev');
    this.nextButton = this.carousel.querySelector('.carousel-next');
    this.dots = this.carousel.querySelectorAll('.carousel-dot');
    
    this.currentIndex = 0;
    this.autoPlayInterval = null;
    
    this.init();
  }
  
  init() {
    if (this.prevButton) {
      this.prevButton.addEventListener('click', () => this.prev());
    }
    
    if (this.nextButton) {
      this.nextButton.addEventListener('click', () => this.next());
    }
    
    this.dots.forEach((dot, index) => {
      dot.addEventListener('click', () => this.goToSlide(index));
    });
    
    this.updateCarousel();
    this.startAutoPlay();
    
    this.carousel.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.carousel.addEventListener('mouseleave', () => this.startAutoPlay());
  }
  
  goToSlide(index) {
    this.currentIndex = index;
    this.updateCarousel();
  }
  
  next() {
    this.currentIndex = (this.currentIndex + 1) % this.slides.length;
    this.updateCarousel();
  }
  
  prev() {
    this.currentIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
    this.updateCarousel();
  }
  
  updateCarousel() {
    const translateX = -(this.currentIndex * 100);
    this.track.style.transform = `translateX(${translateX}%)`;
    this.track.style.transition = 'transform 0.5s ease-in-out';
    
    this.dots.forEach((dot, index) => {
      if (index === this.currentIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }
  
  startAutoPlay() {
    this.autoPlayInterval = setInterval(() => {
      this.next();
    }, 5000);
  }
  
  stopAutoPlay() {
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
    }
  }
}

export function initCarousels() {
  const carousels = document.querySelectorAll('.carousel');
  carousels.forEach(carousel => new Carousel(carousel));
}
