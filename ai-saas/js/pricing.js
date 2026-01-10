class PricingToggle {
  constructor() {
    this.toggle = document.querySelector('.pricing-toggle');
    this.prices = document.querySelectorAll('.pricing-price');
    this.isAnnual = false;
    this.monthlyPrices = [];
    this.annualPrices = [];
    this.init();
  }

  init() {
    if (!this.toggle) return;

    this.extractPrices();
    this.bindEvents();
  }

  extractPrices() {
    this.prices.forEach(priceEl => {
      const monthly = parseFloat(priceEl.dataset.monthly);
      const annual = parseFloat(priceEl.dataset.annual);
      this.monthlyPrices.push(monthly);
      this.annualPrices.push(annual);
    });
  }

  bindEvents() {
    this.toggle.addEventListener('change', () => {
      this.isAnnual = this.toggle.checked;
      this.updatePrices();
      this.updatePeriods();
    });
  }

  updatePrices() {
    this.prices.forEach((priceEl, index) => {
      const price = this.isAnnual ? this.annualPrices[index] : this.monthlyPrices[index];
      this.animatePrice(priceEl, price);
    });
  }

  updatePeriods() {
    const periods = document.querySelectorAll('.pricing-period');
    periods.forEach(period => {
      period.textContent = this.isAnnual ? '/month (billed annually)' : '/month';
    });
  }

  animatePrice(element, targetPrice) {
    const currentPrice = parseFloat(element.textContent.replace(/[^0-9.]/g, ''));
    const duration = 300;
    const steps = 30;
    const increment = (targetPrice - currentPrice) / steps;
    let step = 0;

    const animate = () => {
      if (step < steps) {
        const price = currentPrice + (increment * step);
        element.textContent = '$' + price.toFixed(0);
        step++;
        requestAnimationFrame(animate);
      } else {
        element.textContent = '$' + targetPrice.toFixed(0);
      }
    };

    animate();
  }
}

class PricingCalculator {
  constructor() {
    this.init();
  }

  init() {
    this.initFeatureToggles();
    this.initUserCount();
  }

  initFeatureToggles() {
    const toggles = document.querySelectorAll('.feature-toggle');
    
    toggles.forEach(toggle => {
      toggle.addEventListener('change', () => {
        this.calculateTotal();
      });
    });
  }

  initUserCount() {
    const userCount = document.querySelector('.user-count');
    const userSlider = document.querySelector('.user-slider');
    
    if (userSlider) {
      userSlider.addEventListener('input', (e) => {
        if (userCount) {
          userCount.textContent = e.target.value;
        }
        this.calculateTotal();
      });
    }
  }

  calculateTotal() {
    const basePrice = 49;
    const userCount = parseInt(document.querySelector('.user-slider')?.value || 1);
    const featureToggles = document.querySelectorAll('.feature-toggle:checked');
    
    let featurePrice = 0;
    featureToggles.forEach(toggle => {
      featurePrice += parseInt(toggle.dataset.price || 0);
    });

    const total = (basePrice + featurePrice) * userCount;
    const totalElement = document.querySelector('.calculated-total');
    
    if (totalElement) {
      totalElement.textContent = '$' + total.toFixed(2);
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  new PricingToggle();
  new PricingCalculator();
});