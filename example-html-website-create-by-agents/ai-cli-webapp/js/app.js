/**
 * Main Application Entry Point
 * Initializes all modules and sets up the application
 */

import { getTheme, saveTheme } from './storage.js';
import { getSettings } from './storage.js';
import { log } from './utils.js';

// ================================
// Application State
// ================================

const AppState = {
    initialized: false,
    currentTheme: 'classic-dark',
    commandCount: 0,
    startTime: Date.now()
};

// ================================
// Initialization
// ================================

/**
 * Initialize the application
 */
export function initApp() {
    if (AppState.initialized) {
        log('Application already initialized');
        return;
    }
    
    try {
        log('Initializing AI CLI v1.0...');
        
        // Initialize theme
        initTheme();
        
        // Initialize keyboard handlers
        initKeyboardHandlers();
        
        // Initialize terminal
        initTerminal();
        
        // Update status bar
        updateStatusBar();
        
        // Set initialized flag
        AppState.initialized = true;
        
        log('Application initialized successfully');
        
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
}

/**
 * Initialize theme
 */
function initTheme() {
    const theme = getTheme();
    AppState.currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    log(`Theme set to: ${theme}`);
}

/**
 * Initialize keyboard handlers
 */
function initKeyboardHandlers() {
    const input = document.getElementById('terminalInput');
    if (!input) return;
    
    // Handle keyboard events
    input.addEventListener('keydown', handleKeyDown);
    input.addEventListener('keyup', handleKeyUp);
    
    // Focus input on page load
    input.focus();
    
    // Focus input on terminal click
    const terminal = document.getElementById('terminalWindow');
    if (terminal) {
        terminal.addEventListener('click', () => {
            input.focus();
        });
    }
}

/**
 * Initialize terminal
 */
function initTerminal() {
    const input = document.getElementById('terminalInput');
    if (!input) return;
    
    // Handle command submission
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            executeCommand(input.value);
            input.value = '';
        }
    });
}

/**
 * Update status bar
 */
function updateStatusBar() {
    const statusTheme = document.getElementById('statusTheme');
    if (statusTheme) {
        const themeText = statusTheme.querySelector('.status-text');
        if (themeText) {
            themeText.textContent = toTitleCase(AppState.currentTheme.replace('-', ' '));
        }
    }
}

// ================================
// Command Execution
// ================================

/**
 * Execute a command
 * @param {string} command - Command to execute
 */
export function executeCommand(command) {
    if (!command || !command.trim()) {
        return;
    }
    
    AppState.commandCount++;
    
    // Save to history
    import('./storage.js').then(module => {
        module.saveToHistory(command);
    });
    
    // Parse command
    const parts = command.trim().split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    // Display command in output
    appendCommandToOutput(command);
    
    // Execute command
    processCommand(cmd, args);
    
    // Update command count
    updateCommandCount();
}

/**
 * Process command
 * @param {string} cmd - Command name
 * @param {Array} args - Command arguments
 */
function processCommand(cmd, args) {
    const commands = {
        'help': cmdHelp,
        'clear': cmdClear,
        'cls': cmdClear,
        'echo': cmdEcho,
        'date': cmdDate,
        'whoami': cmdWhoami,
        'history': cmdHistory,
        'theme': cmdTheme,
        'about': cmdAbout,
        'ai': cmdAI,
        'explain': cmdExplain,
        'suggest': cmdSuggest
    };
    
    if (commands[cmd]) {
        commands[cmd](args);
    } else {
        appendOutput(`Command not found: ${cmd}. Type 'help' for available commands.`, 'error');
    }
}

// ================================
// Command Implementations
// ================================

function cmdHelp() {
    const helpText = `
<div class="help-output">
  <div class="help-category">
    <div class="help-category-header">Basic Commands</div>
    <div class="help-category-content">
      <div class="help-command">
        <span class="help-command-name">help</span>
      </div>
      <div class="help-command">
        <span class="help-command-name">clear</span>
      </div>
      <div class="help-command">
        <span class="help-command-name">echo &lt;text&gt;</span>
      </div>
      <div class="help-command">
        <span class="help-command-name">date</span>
      </div>
    </div>
  </div>
  <div class="help-category">
    <div class="help-category-header">Theme Commands</div>
    <div class="help-category-content">
      <div class="help-command">
        <span class="help-command-name">theme &lt;name&gt;</span>
      </div>
    </div>
  </div>
  <div class="help-category">
    <div class="help-category-header">AI Commands</div>
    <div class="help-category-content">
      <div class="help-command">
        <span class="help-command-name">ai &lt;prompt&gt;</span>
      </div>
      <div class="help-command">
        <span class="help-command-name">explain &lt;command&gt;</span>
      </div>
    </div>
  </div>
</div>
<p>Available themes: classic-dark, classic-light, cyberpunk, monokai, solarized-dark, solarized-light, dracula, nord</p>
`;
    appendOutput(helpText);
}

function cmdClear() {
    const output = document.getElementById('terminalOutput');
    if (output) {
        output.innerHTML = '';
    }
}

function cmdEcho(args) {
    const text = args.join(' ');
    appendOutput(escapeHtml(text));
}

function cmdDate() {
    const now = new Date();
    appendOutput(now.toString());
}

function cmdWhoami() {
    appendOutput('user');
}

function cmdHistory() {
    import('./storage.js').then(module => {
        const history = module.getCommandHistory();
        if (history.length === 0) {
            appendOutput('No commands in history.');
            return;
        }
        
        let output = '<div class="history-output">';
        history.slice(0, 20).forEach((item, index) => {
            const time = new Date(item.timestamp).toLocaleTimeString();
            output += `
<div class="history-item">
  <span class="history-number">${index + 1}</span>
  <span class="history-command">${escapeHtml(item.command)}</span>
  <span class="history-time">${time}</span>
</div>`;
        });
        output += '</div>';
        
        appendOutput(output);
    });
}

function cmdTheme(args) {
    if (args.length === 0) {
        appendOutput('Current theme: ' + AppState.currentTheme);
        appendOutput('Usage: theme <name>');
        return;
    }
    
    const theme = args[0].toLowerCase();
    const validThemes = ['classic-dark', 'classic-light', 'cyberpunk', 'monokai', 
                         'solarized-dark', 'solarized-light', 'dracula', 'nord'];
    
    if (!validThemes.includes(theme)) {
        appendOutput(`Invalid theme. Available: ${validThemes.join(', ')}`, 'error');
        return;
    }
    
    saveTheme(theme);
    AppState.currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    appendOutput(`Theme changed to: ${theme}`, 'success');
    updateStatusBar();
}

function cmdAbout() {
    const aboutText = `
<div class="output-line">
  <h3>AI CLI v1.0</h3>
  <p>A modern web-based command line interface with AI-powered assistance.</p>
  <p><strong>Features:</strong></p>
  <ul>
    <li>Command history and autocomplete</li>
    <li>7 built-in themes</li>
    <li>AI-powered command assistance</li>
    <li>Responsive design</li>
    <li>Security-first architecture</li>
  </ul>
  <p>Type 'help' to see available commands.</p>
</div>`;
    appendOutput(aboutText);
}

function cmdAI(args) {
    const prompt = args.join(' ');
    if (!prompt) {
        appendOutput('Usage: ai <prompt>', 'error');
        return;
    }
    
    appendOutput('<div class="loading-spinner"></div><p>Thinking...</p>', 'info');
    
    // Simulate AI response (in production, use backend proxy)
    setTimeout(() => {
        appendOutput(`<div class="ai-response">
  <div class="ai-response-header">🤖 AI Response</div>
  <div class="ai-response-content">
    <p>This is a demo response. In production, this would connect to the AI backend proxy.</p>
    <p>Your prompt: ${escapeHtml(prompt)}</p>
  </div>
</div>`);
    }, 1500);
}

function cmdExplain(args) {
    const command = args.join(' ');
    if (!command) {
        appendOutput('Usage: explain <command>', 'error');
        return;
    }
    
    appendOutput(`<div class="ai-response">
  <div class="ai-response-header">📖 Command Explanation</div>
  <div class="ai-response-content">
    <p><strong>Command:</strong> <code>${escapeHtml(command)}</code></p>
    <p><strong>Description:</strong> This would explain the command using AI.</p>
  </div>
</div>`);
}

function cmdSuggest(args) {
    const task = args.join(' ');
    if (!task) {
        appendOutput('Usage: suggest <task>', 'error');
        return;
    }
    
    appendOutput(`<div class="ai-response">
  <div class="ai-response-header">💡 Command Suggestion</div>
  <div class="ai-response-content">
    <p><strong>Task:</strong> ${escapeHtml(task)}</p>
    <p><strong>Suggested command:</strong> <code># AI would suggest a command here</code></p>
  </div>
</div>`);
}

// ================================
// Output Helpers
// ================================

/**
 * Append command to output
 * @param {string} command - Command string
 */
function appendCommandToOutput(command) {
    const output = document.getElementById('terminalOutput');
    if (!output) return;
    
    const div = document.createElement('div');
    div.className = 'output-line command-output';
    div.innerHTML = `<span class="prompt-symbol">$</span> <span class="command-text">${escapeHtml(command)}</span>`;
    output.appendChild(div);
    scrollToBottom();
}

/**
 * Append output to terminal
 * @param {string} html - HTML content
 * @param {string} type - Output type (info, success, error, warning)
 */
function appendOutput(html, type = '') {
    const output = document.getElementById('terminalOutput');
    if (!output) return;
    
    const div = document.createElement('div');
    div.className = 'output-line ' + type;
    div.innerHTML = html;
    output.appendChild(div);
    scrollToBottom();
}

/**
 * Scroll terminal to bottom
 */
function scrollToBottom() {
    const output = document.getElementById('terminalOutput');
    if (output) {
        output.scrollTop = output.scrollHeight;
    }
}

/**
 * Update command count in status bar
 */
function updateCommandCount() {
    const statusCommands = document.getElementById('statusCommands');
    if (statusCommands) {
        const countText = statusCommands.querySelector('.status-text');
        if (countText) {
            countText.textContent = AppState.commandCount;
        }
    }
}

// ================================
// Keyboard Handlers
// ================================

function handleKeyDown(e) {
    // History navigation (up/down arrows)
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        // TODO: Implement history navigation
    }
    
    // Tab completion
    if (e.key === 'Tab') {
        e.preventDefault();
        // TODO: Implement autocomplete
    }
}

function handleKeyUp(e) {
    // Handle keyup events if needed
}

// ================================
// Utility Functions
// ================================

/**
 * Escape HTML
 * @param {string} str - String to escape
 * @returns {string}
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Convert to title case
 * @param {string} str - String to convert
 * @returns {string}
 */
function toTitleCase(str) {
    return str.replace(/\w\S*/g, txt => 
        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
}

// ================================
// Auto-initialize
// ================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// Export for external use
export default {
    initApp,
    executeCommand,
    appendOutput
};