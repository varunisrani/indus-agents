/**
 * Backend Proxy Server
 * Secure proxy for AI API calls - hides API keys from client
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// ================================
// Security Middleware
// ================================

// Helmet.js - Security headers
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "https://api.openai.com"]
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
}));

// CORS configuration
app.use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:8000',
    credentials: true,
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Body parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// ================================
// Rate Limiting
// ================================

// General rate limiter
const generalLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requests per windowMs
    message: { error: 'Too many requests, please try again later' },
    standardHeaders: true,
    legacyHeaders: false
});

// AI API rate limiter (stricter)
const aiLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 10, // 10 requests per minute
    message: { error: 'Too many AI requests, please try again later' },
    standardHeaders: true,
    legacyHeaders: false,
    skipSuccessfulRequests: false
});

// Apply rate limiters
app.use('/api/ai', aiLimiter);
app.use('/api/', generalLimiter);

// ================================
// Input Validation Middleware
// ================================

function validateInput(req, res, next) {
    const { prompt, command } = req.body;
    
    // Validate prompt length
    if (prompt && prompt.length > 1000) {
        return res.status(400).json({ 
            error: 'Prompt too long (max 1000 characters)' 
        });
    }
    
    // Check for blocked patterns
    const blockedPatterns = [
        /<script/i,
        /javascript:/i,
        /\.innerHTML/i,
        /eval\(/i
    ];
    
    const input = prompt || command || '';
    for (const pattern of blockedPatterns) {
        if (pattern.test(input)) {
            return res.status(400).json({ 
                error: 'Blocked pattern detected in input' 
            });
        }
    }
    
    next();
}

// ================================
// Logging Middleware
// ================================

function requestLogger(req, res, next) {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`);
    });
    
    next();
}

app.use(requestLogger);

// ================================
// Health Check
// ================================

app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// ================================
// AI API Proxy Endpoints
// ================================

/**
 * Chat Completions Endpoint
 * POST /api/ai/chat
 */
app.post('/api/ai/chat', validateInput, async (req, res) => {
    try {
        const { 
            messages, 
            model = 'gpt-3.5-turbo',
            temperature = 0.7,
            maxTokens = 1000
        } = req.body;
        
        if (!messages || !Array.isArray(messages)) {
            return res.status(400).json({ error: 'Invalid messages format' });
        }
        
        // Validate API key
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'API key not configured' });
        }
        
        // Call OpenAI API
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model,
                messages,
                temperature,
                max_tokens: maxTokens
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            return res.status(response.status).json({ 
                error: error.error?.message || 'API request failed' 
            });
        }
        
        const data = await response.json();
        
        // Log usage (without sensitive data)
        console.log(`[AI Request] Model: ${model}, Tokens: ${data.usage?.total_tokens || 'N/A'}`);
        
        res.json(data);
        
    } catch (error) {
        console.error('AI API Error:', error);
        res.status(500).json({ 
            error: 'Internal server error' 
        });
    }
});

/**
 * Explain Command Endpoint
 * POST /api/ai/explain
 */
app.post('/api/ai/explain', validateInput, async (req, res) => {
    try {
        const { command } = req.body;
        
        if (!command) {
            return res.status(400).json({ error: 'Command is required' });
        }
        
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'API key not configured' });
        }
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a CLI expert. Explain shell commands clearly and concisely. Format your response with a brief description, then break down each part of the command, and finally provide a practical example.'
                    },
                    {
                        role: 'user',
                        content: `Explain this command: ${command}`
                    }
                ],
                temperature: 0.5,
                max_tokens: 500
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            return res.status(response.status).json({ 
                error: error.error?.message || 'API request failed' 
            });
        }
        
        const data = await response.json();
        res.json(data);
        
    } catch (error) {
        console.error('Explain API Error:', error);
        res.status(500).json({ 
            error: 'Internal server error' 
        });
    }
});

/**
 * Suggest Command Endpoint
 * POST /api/ai/suggest
 */
app.post('/api/ai/suggest', validateInput, async (req, res) => {
    try {
        const { task } = req.body;
        
        if (!task) {
            return res.status(400).json({ error: 'Task description is required' });
        }
        
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'API key not configured' });
        }
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a CLI expert. Suggest appropriate shell commands for user tasks. Provide the command, then explain what it does. Keep it simple and practical.'
                    },
                    {
                        role: 'user',
                        content: `Suggest a command for: ${task}`
                    }
                ],
                temperature: 0.7,
                max_tokens: 300
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            return res.status(response.status).json({ 
                error: error.error?.message || 'API request failed' 
            });
        }
        
        const data = await response.json();
        res.json(data);
        
    } catch (error) {
        console.error('Suggest API Error:', error);
        res.status(500).json({ 
            error: 'Internal server error' 
        });
    }
});

// ================================
// Error Handling
// ================================

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Global error handler
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// ================================
// Server Startup
// ================================

app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   AI CLI Backend Proxy Server                             ║
║                                                           ║
║   Status: Running                                         ║
║   Port: ${PORT.toString().padEnd(48)}║
║   Environment: ${process.env.NODE_ENV || 'development'.padEnd(39)}║
║                                                           ║
║   Endpoints:                                              ║
║   - POST /api/ai/chat                                     ║
║   - POST /api/ai/explain                                  ║
║   - POST /api/ai/suggest                                  ║
║   - GET  /api/health                                      ║
║                                                           ║
║   Security:                                               ║
║   ✓ Helmet.js enabled                                     ║
║   ✓ Rate limiting enabled                                 ║
║   ✓ CORS configured                                       ║
║   ✓ Input validation enabled                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('\nSIGINT received, shutting down...');
    process.exit(0);
});