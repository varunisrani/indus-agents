export class Tabs {
  constructor(element) {
    this.tabsContainer = element;
    this.tabButtons = this.tabsContainer.querySelectorAll('.tab-button');
    this.tabPanels = this.tabsContainer.querySelectorAll('.tab-panel');
    this.init();
  }
  
  init() {
    this.tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        const targetTab = button.dataset.tab;
        this.switchTab(targetTab);
      });
    });
    
    this.tabPanels.forEach(panel => {
      panel.style.display = 'none';
    });
    
    const firstTab = this.tabButtons[0]?.dataset.tab;
    if (firstTab) {
      this.switchTab(firstTab);
    }
  }
  
  switchTab(tabId) {
    this.tabButtons.forEach(button => {
      if (button.dataset.tab === tabId) {
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');
      } else {
        button.classList.remove('active');
        button.setAttribute('aria-selected', 'false');
      }
    });
    
    this.tabPanels.forEach(panel => {
      if (panel.id === tabId) {
        panel.style.display = 'block';
        panel.classList.add('active');
      } else {
        panel.style.display = 'none';
        panel.classList.remove('active');
      }
    });
  }
}

export function initTabs() {
  const tabsContainers = document.querySelectorAll('.tabs');
  tabsContainers.forEach(container => new Tabs(container));
}
