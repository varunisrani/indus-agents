# AI Chatbot Website Application

A modern, responsive AI chatbot web application built with vanilla HTML, CSS, and JavaScript. Features a beautiful chat interface, AI integration capabilities, and local storage for chat history.

## Features

- **Modern Chat Interface**: Clean, intuitive design with smooth animations
- **AI Integration**: Connect to OpenAI API or similar services
- **Demo Mode**: Works out of the box with demo responses
- **Chat History**: Automatically saves conversations to local storage
- **Responsive Design**: Fully responsive across all devices
- **Settings Panel**: Configure API endpoint, key, model, and parameters
- **Quick Prompts**: Pre-defined conversation starters
- **Dark Theme**: Beautiful dark color scheme with gradient accents

## Quick Start

1. **Open the Application**
   ```bash
   cd ai-chatbot-app
   ```

2. **Open in Browser**
   - Simply open `index.html` in any modern web browser
   - Or use a local server:
     ```bash
     # Python 3
     python -m http.server 8000
     
     # Node.js
     npx serve
     ```

3. **Use Demo Mode**
   - Start chatting immediately with demo responses
   - Try quick prompts like "Tell me a joke" or "Help me write code"

## Configuration

To connect to a real AI service:

1. Click the settings icon (⚙️) in the header
2. Enter your API details:
   - **API Endpoint**: Your AI service endpoint (e.g., `https://api.openai.com/v1/chat/completions`)
   - **API Key**: Your API key
   - **Model**: Choose from GPT-3.5, GPT-4, or Claude-3
   - **Temperature**: Adjust response randomness (0.0 - 2.0)
   - **Max Tokens**: Set maximum response length

3. Click "Save Settings"

## Supported AI Services

- **OpenAI** (GPT-3.5, GPT-4)
- **Anthropic** (Claude-3)
- Any compatible OpenAI-style API endpoint

## File Structure

```
ai-chatbot-app/
├── index.html          # Main HTML structure
├── styles.css          # Complete styling with responsive design
├── script.js           # Chat functionality and AI integration
└── README.md           # This file
```

## Features in Detail

### Chat Interface
- User and bot avatars
- Message timestamps
- Typing indicator
- Auto-scroll to latest messages
- Markdown-style formatting (bold, italic, code, links)

### Settings Management
- Persistent storage using localStorage
- Configurable model parameters
- Secure API key handling

### Chat History
- Automatic saving of conversations
- Clear chat option
- History persists across sessions

### Responsive Design
- Desktop: Full-featured interface
- Tablet: Optimized layout
- Mobile: Compact, touch-friendly design

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Security Notes

- API keys are stored in localStorage (browser-specific)
- For production, implement server-side API proxy
- Never commit API keys to version control
- Use environment variables for deployment

## Customization

### Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #ec4899;
    /* ... more variables */
}
```

### Demo Responses
Modify `getDemoResponse()` in `script.js` to add custom demo responses.

### AI Integration
The app uses standard OpenAI API format. Modify `getAIResponse()` for custom integrations.

## Performance

- Fast load time (no frameworks)
- Minimal dependencies (only Font Awesome icons)
- Efficient DOM manipulation
- Smooth animations with CSS

## Future Enhancements

Potential features to add:
- Voice input/output
- File upload support
- Multiple chat sessions
- Export chat history
- User authentication
- Streaming responses
- Image generation support

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues or questions:
1. Check browser console for errors
2. Verify API settings
3. Ensure API key has sufficient credits
4. Check CORS settings if using custom endpoint

---

**Enjoy your AI Chatbot Application!** 🤖✨