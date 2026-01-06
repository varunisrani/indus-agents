// Product Gallery Module - AI Machine

export function initProductGalleries() {
  const galleries = document.querySelectorAll('.product-gallery');

  galleries.forEach(gallery => {
    const images = gallery.querySelectorAll('.gallery-image');
    const thumbnails = gallery.querySelectorAll('.gallery-thumbnail');
    const prevBtn = gallery.querySelector('.gallery-prev');
    const nextBtn = gallery.querySelector('.gallery-next');
    const dotsContainer = gallery.querySelector('.gallery-dots');

    let currentIndex = 0;
    let autoplayInterval;

    const showImage = (index) => {
      images.forEach((img, i) => {
        img.classList.toggle('active', i === index);
        img.style.opacity = i === index ? '1' : '0';
      });
      thumbnails.forEach((thumb, i) => {
        thumb.classList.toggle('active', i === index);
      });

      if (dotsContainer) {
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((dot, i) => {
          dot.classList.toggle('active', i === index);
        });
      }

      currentIndex = index;
    };

    const nextImage = () => {
      const newIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
      showImage(newIndex);
    };

    const prevImage = () => {
      const newIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
      showImage(newIndex);
    };

    thumbnails.forEach((thumb, index) => {
      thumb.addEventListener('click', () => {
        showImage(index);
        resetAutoplay();
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        prevImage();
        resetAutoplay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        nextImage();
        resetAutoplay();
      });
    }

    const startAutoplay = () => {
      autoplayInterval = setInterval(nextImage, 5000);
    };

    const stopAutoplay = () => {
      clearInterval(autoplayInterval);
    };

    const resetAutoplay = () => {
      stopAutoplay();
      startAutoplay();
    };

    gallery.addEventListener('mouseenter', stopAutoplay);
    gallery.addEventListener('mouseleave', startAutoplay);

    gallery.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        prevImage();
        resetAutoplay();
      } else if (e.key === 'ArrowRight') {
        nextImage();
        resetAutoplay();
      }
    });

    showImage(0);
    startAutoplay();
  });

  initLightbox();
}

function initLightbox() {
  const lightboxLinks = document.querySelectorAll('[data-lightbox]');

  if (!lightboxLinks.length) return;

  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = `
    <button class="lightbox-close">&times;</button>
    <button class="lightbox-prev">&lsaquo;</button>
    <button class="lightbox-next">&rsaquo;</button>
    <div class="lightbox-content">
      <img src="" alt="">
    </div>
  `;
  document.body.appendChild(lightbox);

  const lightboxImg = lightbox.querySelector('img');
  const closeBtn = lightbox.querySelector('.lightbox-close');
  const prevBtn = lightbox.querySelector('.lightbox-prev');
  const nextBtn = lightbox.querySelector('.lightbox-next');

  let currentIndex = 0;
  const images = Array.from(lightboxLinks);

  const showImage = (index) => {
    currentIndex = index;
    lightboxImg.src = images[index].href;
    lightboxImg.alt = images[index].dataset.alt || '';
  };

  lightboxLinks.forEach((link, index) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      showImage(index);
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  closeBtn.addEventListener('click', () => {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  });

  prevBtn.addEventListener('click', () => {
    const newIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
    showImage(newIndex);
  });

  nextBtn.addEventListener('click', () => {
    const newIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
    showImage(newIndex);
  });

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;

    if (e.key === 'Escape') {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    } else if (e.key === 'ArrowLeft') {
      const newIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
      showImage(newIndex);
    } else if (e.key === 'ArrowRight') {
      const newIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
      showImage(newIndex);
    }
  });
}
