document.addEventListener('DOMContentLoaded', function() {
  initModelCards();
  renderPerformanceChart();
});

const modelData = {
  'glm-tiny': {
    params: '7B',
    context: '32K',
    speed: '150+ tok/s',
    inputPrice: '$0.50/1M',
    outputPrice: '$1.50/1M'
  },
  'glm-base': {
    params: '13B',
    context: '128K',
    speed: '100+ tok/s',
    inputPrice: '$1.50/1M',
    outputPrice: '$5.00/1M'
  },
  'glm-pro': {
    params: '70B',
    context: '200K',
    speed: '50+ tok/s',
    inputPrice: '$3.00/1M',
    outputPrice: '$15.00/1M'
  },
  'glm-ultra': {
    params: '175B',
    context: '200K',
    speed: '30+ tok/s',
    inputPrice: '$8.00/1M',
    outputPrice: '$25.00/1M'
  }
};

function initModelCards() {
  const modelCards = document.querySelectorAll('.model-card');

  modelCards.forEach(card => {
    card.addEventListener('click', function() {
      modelCards.forEach(c => c.classList.remove('selected'));
      this.classList.add('selected');

      const modelId = this.dataset.model;
      if (modelId) {
        highlightModelRow(modelId);
      }
    });
  });
}

function highlightModelRow(modelId) {
  const table = document.querySelector('.comparison-table');
  if (!table) return;

  const rows = table.querySelectorAll('tbody tr');
  rows.forEach(row => {
    row.style.background = '';
  });

  const modelIndex = Object.keys(modelData).indexOf(modelId);
  if (modelIndex >= 0 && modelIndex < rows.length) {
    rows[modelIndex].style.background = 'rgba(255, 107, 107, 0.1)';
  }
}

function renderPerformanceChart() {
  const chartContainer = document.getElementById('performance-chart');
  if (!chartContainer) return;

  const chartData = [
    { model: 'GLM-Tiny', score: 65 },
    { model: 'GLM-Base', score: 78 },
    { model: 'GLM-Pro', score: 89 },
    { model: 'GLM-Ultra', score: 96 }
  ];

  chartContainer.innerHTML = chartData.map(item => `
    <div class="chart-bar">
      <div class="bar-label">${item.model}</div>
      <div class="bar-fill" style="width: ${item.score}%"></div>
      <div class="bar-value">${item.score}%</div>
    </div>
  `).join('');

  animateChartBars();
}

function animateChartBars() {
  const bars = document.querySelectorAll('.chart-bar .bar-fill');

  bars.forEach((bar, index) => {
    const width = bar.style.width;
    bar.style.width = '0%';

    setTimeout(() => {
      bar.style.transition = 'width 1s ease-out';
      bar.style.width = width;
    }, index * 150);
  });
}
