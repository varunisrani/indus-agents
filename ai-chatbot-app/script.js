class ChatBot {
    constructor() {
        this.messages = [];
        this.settings = {
            apiEndpoint: '',
            apiKey: '',
            model: 'gpt-3.5-turbo',
            temperature: 0.7,
            maxTokens: 2000
        };
        this.init();
    }

    init() {
        this.cacheElements();
        this.attachEventListeners();
        this.loadSettings();
        this.loadChatHistory();
    }

    cacheElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettingsBtn = document.getElementById('closeSettings');
        this.saveSettingsBtn = document.getElementById('saveSettings');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickPrompts = document.querySelectorAll('.quick-prompt');
    }

    attachEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.clearChatBtn.addEventListener('click', () => this.clearChat());

        this.quickPrompts.forEach(prompt => {
            prompt.addEventListener('click', () => {
                this.messageInput.value = prompt.textContent;
                this.sendMessage();
            });
        });

        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });

        document.getElementById('temperature').addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
        });
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.removeWelcomeMessage();
        this.addMessage(message, 'user');
        this.messageInput.value = '';

        this.showTypingIndicator();

        try {
            const response = await this.getAIResponse(message);
            this.hideTypingIndicator();
            this.addMessage(response, 'bot');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('I apologize, but I encountered an error. Please check your settings and try again.', 'bot');
            console.error('Error:', error);
        }

        this.saveChatHistory();
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'bot' 
            ? '<i class="fas fa-robot"></i>' 
            : '<i class="fas fa-user"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.innerHTML = this.formatMessage(content);

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();

        messageContent.appendChild(messageBubble);
        messageContent.appendChild(messageTime);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatMessages.appendChild(messageDiv);
        this.messages.push({ content, type, timestamp: Date.now() });
        this.scrollToBottom();
    }

    formatMessage(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    removeWelcomeMessage() {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }

    showTypingIndicator() {
        this.typingIndicator.classList.add('active');
        this.chatMessages.appendChild(this.typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.classList.remove('active');
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async getAIResponse(message) {
        if (!this.settings.apiKey) {
            return this.getDemoResponse(message);
        }

        try {
            const response = await fetch(this.settings.apiEndpoint || 'https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.settings.apiKey}`
                },
                body: JSON.stringify({
                    model: this.settings.model,
                    messages: [
                        { role: 'system', content: 'You are a helpful AI assistant. Provide clear, concise, and accurate responses.' },
                        ...this.getRecentMessages(),
                        { role: 'user', content: message }
                    ],
                    temperature: parseFloat(this.settings.temperature),
                    max_tokens: parseInt(this.settings.maxTokens)
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            return data.choices[0].message.content;
        } catch (error) {
            console.error('API Error:', error);
            return this.getDemoResponse(message);
        }
    }

    getRecentMessages() {
        return this.messages.slice(-10).map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
        }));
    }

    getDemoResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
            return "Hello! I'm your AI assistant. How can I help you today?";
        }
        
        if (lowerMessage.includes('how are you')) {
            return "I'm doing great, thank you for asking! I'm here to help you with any questions or tasks you might have.";
        }
        
        if (lowerMessage.includes('joke')) {
            const jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                "Why did the AI go to therapy? It had too many deep learning issues! 🤖",
                "What's a robot's favorite snack? Computer chips! 💻",
                "Why was the JavaScript developer sad? Because he didn't Node how to Express himself! 😄"
            ];
            return jokes[Math.floor(Math.random() * jokes.length)];
        }
        
        if (lowerMessage.includes('help')) {
            return "I can help you with:\n\n• **Writing code** - Just describe what you need\n• **Answering questions** - Ask me anything\n• **Brainstorming ideas** - I'm great at creative thinking\n• **Explaining concepts** - Complex topics made simple\n• **Drafting content** - Emails, articles, and more\n\nWhat would you like to work on?";
        }
        
        if (lowerMessage.includes('code') || lowerMessage.includes('programming')) {
            return "I'd be happy to help you with coding! Please tell me:\n\n• What programming language are you using?\n• What problem are you trying to solve?\n• Any specific requirements or constraints?\n\nOnce you provide these details, I can write, explain, or debug code for you!";
        }
        
        if (lowerMessage.includes('thank')) {
            return "You're welcome! Is there anything else I can help you with?";
        }
        
        if (lowerMessage.includes('bye') || lowerMessage.includes('goodbye')) {
            return "Goodbye! Feel free to come back anytime you need assistance. Take care! 👋";
        }

        const generalResponses = [
            "That's an interesting point! Could you tell me more about what you're looking for?",
            "I'd be happy to help with that. Can you provide more details?",
            "Great question! Let me think about this... Could you clarify what specific aspect you're interested in?",
            "I understand you're asking about " + message + ". While I'm in demo mode, I can still have a basic conversation with you. To get full AI responses, please configure an API key in the settings."
        ];
        
        return generalResponses[Math.floor(Math.random() * generalResponses.length)];
    }

    openSettings() {
        this.settingsModal.classList.add('active');
        document.getElementById('apiEndpoint').value = this.settings.apiEndpoint;
        document.getElementById('apiKey').value = this.settings.apiKey;
        document.getElementById('modelName').value = this.settings.model;
        document.getElementById('temperature').value = this.settings.temperature;
        document.getElementById('tempValue').textContent = this.settings.temperature;
        document.getElementById('maxTokens').value = this.settings.maxTokens;
    }

    closeSettings() {
        this.settingsModal.classList.remove('active');
    }

    saveSettings() {
        this.settings = {
            apiEndpoint: document.getElementById('apiEndpoint').value,
            apiKey: document.getElementById('apiKey').value,
            model: document.getElementById('modelName').value,
            temperature: parseFloat(document.getElementById('temperature').value),
            maxTokens: parseInt(document.getElementById('maxTokens').value)
        };
        
        localStorage.setItem('chatbotSettings', JSON.stringify(this.settings));
        this.closeSettings();
        this.showNotification('Settings saved successfully!');
    }

    loadSettings() {
        const saved = localStorage.getItem('chatbotSettings');
        if (saved) {
            this.settings = JSON.parse(saved);
        }
    }

    loadChatHistory() {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            this.messages = JSON.parse(saved);
            if (this.messages.length > 0) {
                this.removeWelcomeMessage();
                this.messages.forEach(msg => {
                    this.addMessageToDOM(msg.content, msg.type, msg.timestamp);
                });
            }
        }
    }

    addMessageToDOM(content, type, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'bot' 
            ? '<i class="fas fa-robot"></i>' 
            : '<i class="fas fa-user"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.innerHTML = this.formatMessage(content);

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date(timestamp).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageContent.appendChild(messageBubble);
        messageContent.appendChild(messageTime);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatMessages.appendChild(messageDiv);
    }

    saveChatHistory() {
        localStorage.setItem('chatHistory', JSON.stringify(this.messages));
    }

    clearChat() {
        if (confirm('Are you sure you want to clear all chat history?')) {
            this.messages = [];
            localStorage.removeItem('chatHistory');
            this.chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="bot-avatar large">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h2>Welcome to AI Chat Assistant!</h2>
                    <p>I'm here to help you with any questions or tasks. How can I assist you today?</p>
                    <div class="quick-prompts">
                        <button class="quick-prompt">What can you help me with?</button>
                        <button class="quick-prompt">Tell me a joke</button>
                        <button class="quick-prompt">Help me write code</button>
                        <button class="quick-prompt">Explain a concept</button>
                    </div>
                </div>
            `;
            this.attachEventListeners();
        }
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});