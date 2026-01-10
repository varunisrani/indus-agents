/**
 * Storage Module
 * LocalStorage and SessionStorage management with encryption support
 */

import { getStorage, setStorage, removeStorage } from './utils.js';

// ================================
// Storage Keys
// ================================

const STORAGE_KEYS = {
    COMMAND_HISTORY: 'ai-cli-history',
    THEME: 'ai-cli-theme',
    SETTINGS: 'ai-cli-settings',
    SESSION: 'ai-cli-session',
    API_KEY: 'ai-cli-api-key', // Encrypted
    USER_PROFILE: 'ai-cli-profile',
    ALIASES: 'ai-cli-aliases',
    ENV_VARS: 'ai-cli-env'
};

// ================================
// Command History Storage
// ================================

/**
 * Save command to history
 * @param {string} command - Command to save
 * @param {number} maxHistory - Maximum history size (default: 1000)
 */
export function saveToHistory(command, maxHistory = 1000) {
    if (!command || !command.trim()) return;
    
    const history = getCommandHistory();
    
    // Add new command to beginning
    history.unshift({
        command: command.trim(),
        timestamp: Date.now(),
        id: generateUniqueId()
    });
    
    // Remove duplicates (keep latest)
    const uniqueHistory = history.filter((item, index, self) =>
        index === self.findIndex(t => t.command === item.command)
    );
    
    // Limit history size
    const limitedHistory = uniqueHistory.slice(0, maxHistory);
    
    setStorage(STORAGE_KEYS.COMMAND_HISTORY, limitedHistory);
}

/**
 * Get command history
 * @returns {Array}
 */
export function getCommandHistory() {
    return getStorage(STORAGE_KEYS.COMMAND_HISTORY, []);
}

/**
 * Clear command history
 * @returns {boolean}
 */
export function clearHistory() {
    removeStorage(STORAGE_KEYS.COMMAND_HISTORY);
    return true;
}

/**
 * Search command history
 * @param {string} query - Search query
 * @returns {Array}
 */
export function searchHistory(query) {
    const history = getCommandHistory();
    const lowerQuery = query.toLowerCase();
    
    return history.filter(item =>
        item.command.toLowerCase().includes(lowerQuery)
    );
}

// ================================
// Theme Storage
// ================================

/**
 * Save current theme
 * @param {string} theme - Theme name
 */
export function saveTheme(theme) {
    setStorage(STORAGE_KEYS.THEME, theme);
}

/**
 * Get saved theme
 * @returns {string}
 */
export function getTheme() {
    return getStorage(STORAGE_KEYS.THEME, 'classic-dark');
}

// ================================
// Settings Storage
// ================================

/**
 * Get user settings
 * @returns {object}
 */
export function getSettings() {
    return getStorage(STORAGE_KEYS.SETTINGS, {
        fontSize: 'medium',
        fontFamily: 'Fira Code',
        cursorBlink: true,
        soundEnabled: false,
        notificationsEnabled: true,
        autoSave: true,
        maxHistory: 1000
    });
}

/**
 * Save user settings
 * @param {object} settings - Settings object
 */
export function saveSettings(settings) {
    const currentSettings = getSettings();
    const mergedSettings = { ...currentSettings, ...settings };
    setStorage(STORAGE_KEYS.SETTINGS, mergedSettings);
}

/**
 * Update single setting
 * @param {string} key - Setting key
 * @param {*} value - Setting value
 */
export function updateSetting(key, value) {
    const settings = getSettings();
    settings[key] = value;
    saveSettings(settings);
}

// ================================
// Session Storage
// ================================

/**
 * Save session data
 * @param {object} session - Session data
 */
export function saveSession(session) {
    setStorage(STORAGE_KEYS.SESSION, {
        ...session,
        lastUpdated: Date.now()
    });
}

/**
 * Get session data
 * @returns {object}
 */
export function getSession() {
    return getStorage(STORAGE_KEYS.SESSION, {
        startTime: Date.now(),
        commandCount: 0,
        currentDirectory: '~'
    });
}

/**
 * Clear session data
 */
export function clearSession() {
    removeStorage(STORAGE_KEYS.SESSION);
}

/**
 * Update session
 * @param {object} updates - Updates to apply
 */
export function updateSession(updates) {
    const session = getSession();
    saveSession({ ...session, ...updates });
}

// ================================
// API Key Storage (Encrypted)
// ================================

/**
 * Simple encryption for API key (NOT production-grade, use backend for real security)
 * @param {string} key - API key
 * @returns {string} Encrypted key
 */
function encryptApiKey(key) {
    // Simple XOR encryption with a fixed key (NOT SECURE, only for obfuscation)
    const encryptionKey = 'ai-cli-obfuscation-key';
    let encrypted = '';
    
    for (let i = 0; i < key.length; i++) {
        encrypted += String.fromCharCode(
            key.charCodeAt(i) ^ encryptionKey.charCodeAt(i % encryptionKey.length)
        );
    }
    
    return btoa(encrypted); // Base64 encode
}

/**
 * Simple decryption for API key
 * @param {string} encryptedKey - Encrypted API key
 * @returns {string} Decrypted key
 */
function decryptApiKey(encryptedKey) {
    try {
        const decoded = atob(encryptedKey); // Base64 decode
        const decryptionKey = 'ai-cli-obfuscation-key';
        let decrypted = '';
        
        for (let i = 0; i < decoded.length; i++) {
            decrypted += String.fromCharCode(
                decoded.charCodeAt(i) ^ decryptionKey.charCodeAt(i % decryptionKey.length)
            );
        }
        
        return decrypted;
    } catch {
        return '';
    }
}

/**
 * Save API key (encrypted)
 * @param {string} apiKey - API key to save
 * @returns {boolean}
 */
export function saveApiKey(apiKey) {
    if (!apiKey || typeof apiKey !== 'string') return false;
    
    const encrypted = encryptApiKey(apiKey);
    setStorage(STORAGE_KEYS.API_KEY, encrypted);
    return true;
}

/**
 * Get API key (decrypted)
 * @returns {string|null}
 */
export function getApiKey() {
    const encrypted = getStorage(STORAGE_KEYS.API_KEY);
    if (!encrypted) return null;
    
    return decryptApiKey(encrypted);
}

/**
 * Remove API key
 */
export function removeApiKey() {
    removeStorage(STORAGE_KEYS.API_KEY);
}

/**
 * Check if API key exists
 * @returns {boolean}
 */
export function hasApiKey() {
    return getStorage(STORAGE_KEYS.API_KEY) !== null;
}

// ================================
// User Profile Storage
// ================================

/**
 * Get user profile
 * @returns {object}
 */
export function getUserProfile() {
    return getStorage(STORAGE_KEYS.USER_PROFILE, {
        username: 'user',
        hostname: 'ai-cli',
        customPrompt: ''
    });
}

/**
 * Save user profile
 * @param {object} profile - Profile data
 */
export function saveUserProfile(profile) {
    setStorage(STORAGE_KEYS.USER_PROFILE, profile);
}

// ================================
// Aliases Storage
// ================================

/**
 * Get all aliases
 * @returns {object}
 */
export function getAliases() {
    return getStorage(STORAGE_KEYS.ALIASES, {
        ll: 'ls -la',
        la: 'ls -A',
        l: 'ls -CF',
        ..: 'cd ..'
    });
}

/**
 * Save alias
 * @param {string} name - Alias name
 * @param {string} command - Command to alias
 */
export function saveAlias(name, command) {
    const aliases = getAliases();
    aliases[name] = command;
    setStorage(STORAGE_KEYS.ALIASES, aliases);
}

/**
 * Remove alias
 * @param {string} name - Alias name
 */
export function removeAlias(name) {
    const aliases = getAliases();
    delete aliases[name];
    setStorage(STORAGE_KEYS.ALIASES, aliases);
}

/**
 * Resolve alias
 * @param {string} name - Alias name
 * @returns {string|null}
 */
export function resolveAlias(name) {
    const aliases = getAliases();
    return aliases[name] || null;
}

// ================================
// Environment Variables Storage
// ================================

/**
 * Get environment variables
 * @returns {object}
 */
export function getEnvVars() {
    return getStorage(STORAGE_KEYS.ENV_VARS, {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        HOME: '/home/user',
        USER: 'user',
        SHELL: '/bin/bash',
        EDITOR: 'vim',
        TERM: 'xterm-256color'
    });
}

/**
 * Set environment variable
 * @param {string} key - Variable name
 * @param {string} value - Variable value
 */
export function setEnvVar(key, value) {
    const env = getEnvVars();
    env[key] = value;
    setStorage(STORAGE_KEYS.ENV_VARS, env);
}

/**
 * Get environment variable
 * @param {string} key - Variable name
 * @returns {string|null}
 */
export function getEnvVar(key) {
    const env = getEnvVars();
    return env[key] || null;
}

/**
 * Unset environment variable
 * @param {string} key - Variable name
 */
export function unsetEnvVar(key) {
    const env = getEnvVars();
    delete env[key];
    setStorage(STORAGE_KEYS.ENV_VARS, env);
}

// ================================
// Export/Import Functions
// ================================

/**
 * Export all data
 * @returns {string} JSON string
 */
export function exportAllData() {
    const data = {
        version: '1.0',
        exportDate: new Date().toISOString(),
        history: getCommandHistory(),
        theme: getTheme(),
        settings: getSettings(),
        profile: getUserProfile(),
        aliases: getAliases(),
        env: getEnvVars()
        // API key is NOT exported for security
    };
    
    return JSON.stringify(data, null, 2);
}

/**
 * Import data
 * @param {string} jsonData - JSON data to import
 * @returns {boolean}
 */
export function importData(jsonData) {
    try {
        const data = JSON.parse(jsonData);
        
        if (data.history) setStorage(STORAGE_KEYS.COMMAND_HISTORY, data.history);
        if (data.theme) saveTheme(data.theme);
        if (data.settings) saveSettings(data.settings);
        if (data.profile) saveUserProfile(data.profile);
        if (data.aliases) setStorage(STORAGE_KEYS.ALIASES, data.aliases);
        if (data.env) setStorage(STORAGE_KEYS.ENV_VARS, data.env);
        
        return true;
    } catch (error) {
        console.error('Import failed:', error);
        return false;
    }
}

/**
 * Clear all data
 * @returns {boolean}
 */
export function clearAllData() {
    Object.values(STORAGE_KEYS).forEach(key => {
        removeStorage(key);
    });
    return true;
}

// ================================
// Utility Functions
// ================================

/**
 * Generate unique ID
 * @returns {string}
 */
function generateUniqueId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Get storage usage
 * @returns {object} Storage info
 */
export function getStorageInfo() {
    let totalSize = 0;
    const items = {};
    
    Object.values(STORAGE_KEYS).forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
            const size = new Blob([value]).size;
            totalSize += size;
            items[key] = {
                size: size,
                sizeFormatted: formatBytes(size)
            };
        }
    });
    
    return {
        totalSize,
        totalSizeFormatted: formatBytes(totalSize),
        items,
        itemCount: Object.keys(items).length
    };
}

/**
 * Format bytes to human readable
 * @param {number} bytes - Bytes to format
 * @returns {string}
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// ================================
// Export
// ================================

export default {
    saveToHistory,
    getCommandHistory,
    clearHistory,
    searchHistory,
    saveTheme,
    getTheme,
    getSettings,
    saveSettings,
    updateSetting,
    saveSession,
    getSession,
    clearSession,
    updateSession,
    saveApiKey,
    getApiKey,
    removeApiKey,
    hasApiKey,
    getUserProfile,
    saveUserProfile,
    getAliases,
    saveAlias,
    removeAlias,
    resolveAlias,
    getEnvVars,
    setEnvVar,
    getEnvVar,
    unsetEnvVar,
    exportAllData,
    importData,
    clearAllData,
    getStorageInfo
};