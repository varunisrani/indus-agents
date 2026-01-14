document.addEventListener('DOMContentLoaded', function() {
  initBillingToggle();
  initUsageCalculator();
});

const pricingData = {
  monthly: {
    free: 0,
    pro: 20,
    enterprise: null
  },
  annual: {
    free: 0,
    pro: 16,
    enterprise: null
  }
};

let isAnnual = false;

function initBillingToggle() {
  const billingToggle = document.getElementById('billing-toggle');
  if (!billingToggle) return;

  billingToggle.addEventListener('click', function() {
    isAnnual = !isAnnual;
    this.classList.toggle('active', isAnnual);
    this.setAttribute('aria-checked', isAnnual);
    updatePrices();
  });

  billingToggle.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      this.click();
    }
  });
}

function updatePrices() {
  const period = isAnnual ? 'annual' : 'monthly';
  const pricingCards = document.querySelectorAll('.pricing-card');

  pricingCards.forEach(card => {
    const tier = card.dataset.tier;
    const price = pricingData[period][tier];
    const priceElement = card.querySelector('.price');
    const periodElement = card.querySelector('.price-period');

    if (price !== null && priceElement) {
      priceElement.textContent = isAnnual ? '/month (billed annually)' : '/month';
      if (priceElement.previousSibling) {
        priceElement.previousSibling.textContent = `$${price}`;
      }
    }
  });
}

function initUsageCalculator() {
  const inputSlider = document.getElementById('input-slider');
  const outputSlider = document.getElementById('output-slider');
  const inputValue = document.getElementById('input-value');
  const outputValue = document.getElementById('output-value');
  const inputCost = document.getElementById('input-cost');
  const outputCost = document.getElementById('output-cost');
  const totalCost = document.getElementById('total-cost');

  if (!inputSlider || !outputSlider) return;

  function updateCalculator() {
    const inputTokens = parseInt(inputSlider.value);
    const outputTokens = parseInt(outputSlider.value);

    if (inputValue) {
      inputValue.textContent = formatNumber(inputTokens);
    }
    if (outputValue) {
      outputValue.textContent = formatNumber(outputTokens);
    }

    const inputCostValue = (inputTokens / 1000000) * 3;
    const outputCostValue = (outputTokens / 1000000) * 15;
    const totalCostValue = inputCostValue + outputCostValue;

    if (inputCost) {
      inputCost.textContent = `$${inputCostValue.toFixed(2)}`;
    }
    if (outputCost) {
      outputCost.textContent = `$${outputCostValue.toFixed(2)}`;
    }
    if (totalCost) {
      totalCost.innerHTML = `<strong>$${totalCostValue.toFixed(2)}</strong>`;
    }
  }

  inputSlider.addEventListener('input', updateCalculator);
  outputSlider.addEventListener('input', updateCalculator);

  updateCalculator();
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K';
  }
  return num.toString();
}
