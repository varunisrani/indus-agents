import { getDueTasksCount } from '../utils/dateFormatter.js';

export class DashboardView {
    constructor() {
        this.statTotal = document.getElementById('statTotal');
        this.statActive = document.getElementById('statActive');
        this.statCompleted = document.getElementById('statCompleted');
        this.statDue = document.getElementById('statDue');
        this.taskSummary = document.getElementById('taskSummary');
    }
    
    updateStats(tasks) {
        const total = tasks.length;
        const completed = tasks.filter(t => t.completed).length;
        const active = total - completed;
        const due = getDueTasksCount(tasks);
        
        this.animateNumber(this.statTotal, total);
        this.animateNumber(this.statActive, active);
        this.animateNumber(this.statCompleted, completed);
        this.animateNumber(this.statDue, due);
        
        this.taskSummary.textContent = `${total} task${total !== 1 ? 's' : ''}`;
    }
    
    animateNumber(element, target) {
        if (!element) return;
        
        const current = parseInt(element.textContent) || 0;
        const duration = 300;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const value = Math.round(current + (target - current) * easeOut);
            
            element.textContent = value;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
}