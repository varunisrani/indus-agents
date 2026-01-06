// Product Data - AI Machine

export const products = {
  servers: [
    {
      id: 'ai-server-pro',
      name: 'AI Server Pro',
      category: 'servers',
      price: 24999,
      specs: {
        cpu: '64-Core AI Processor',
        gpu: '8x NVIDIA A100',
        memory: '2TB DDR5',
        storage: '30TB NVMe SSD',
        power: '3000W'
      },
      features: [
        'High-performance AI training',
        'Scalable architecture',
        'Liquid cooling system',
        'Enterprise support'
      ]
    },
    {
      id: 'ai-server-edge',
      name: 'AI Server Edge',
      category: 'servers',
      price: 12999,
      specs: {
        cpu: '32-Core AI Processor',
        gpu: '4x NVIDIA A40',
        memory: '1TB DDR5',
        storage: '10TB NVMe SSD',
        power: '1600W'
      },
      features: [
        'Edge computing optimized',
        'Compact form factor',
        'Low latency processing',
        'Industrial grade'
      ]
    }
  ],
  chips: [
    {
      id: 'neural-chip-x1',
      name: 'Neural Chip X1',
      category: 'chips',
      price: 2999,
      specs: {
        architecture: '7nm',
        cores: '256 AI Cores',
        tdp: '250W',
        memory: '64GB HBM2e',
        bandwidth: '2.4 TB/s'
      },
      features: [
        'Advanced neural processing',
        'Energy efficient',
        'High bandwidth memory',
        'PCIe 5.0 support'
      ]
    }
  ],
  solutions: [
    {
      id: 'enterprise-suite',
      name: 'Enterprise AI Suite',
      category: 'solutions',
      price: 99999,
      specs: {
        deployment: 'On-premise or Cloud',
        support: '24/7 Enterprise',
        sla: '99.99% Uptime',
        users: 'Unlimited'
      },
      features: [
        'Complete AI infrastructure',
        'Professional services',
        'Custom integration',
        'Training programs'
      ]
    }
  ]
};

export const caseStudies = [
  {
    id: 'tech-corp',
    company: 'Tech Corp',
    industry: 'Technology',
    title: 'Scaling AI Infrastructure',
    result: '300% faster training',
    metrics: {
      performance: '300%',
      cost: '-40%',
      time: '-60%'
    }
  },
  {
    id: 'finance-hub',
    company: 'Finance Hub',
    industry: 'Financial Services',
    title: 'Real-time Fraud Detection',
    result: '99.9% accuracy',
    metrics: {
      accuracy: '99.9%',
      latency: '<10ms',
      throughput: '1M+ transactions'
    }
  }
];

export const pricing = {
  standard: {
    name: 'Standard',
    price: 999,
    features: [
      'Basic AI servers',
      'Email support',
      '99.5% uptime SLA',
      'Standard documentation',
      'Community access'
    ]
  },
  professional: {
    name: 'Professional',
    price: 2499,
    features: [
      'Advanced AI servers',
      'Priority support',
      '99.9% uptime SLA',
      'Advanced documentation',
      'API access',
      'Custom integrations'
    ],
    featured: true
  },
  enterprise: {
    name: 'Enterprise',
    price: 'Custom',
    features: [
      'Dedicated infrastructure',
      '24/7 phone support',
      '99.99% uptime SLA',
      'On-site support',
      'Custom solutions',
      'Training programs',
      'Dedicated account manager'
    ]
  }
};

export const testimonials = [
  {
    name: 'John Smith',
    role: 'CTO',
    company: 'Tech Innovations Inc',
    content: 'AI Machine transformed our infrastructure. The performance gains are incredible.',
    avatar: '/assets/images/testimonials/john-smith.jpg'
  },
  {
    name: 'Sarah Johnson',
    role: 'VP Engineering',
    company: 'DataFlow Systems',
    content: 'Best AI hardware we\'ve used. Reliable, fast, and well-supported.',
    avatar: '/assets/images/testimonials/sarah-johnson.jpg'
  }
];

export const faqs = {
  general: [
    {
      question: 'What makes AI Machine different?',
      answer: 'AI Machine provides purpose-built AI infrastructure with optimized hardware, software integration, and enterprise-grade support.'
    },
    {
      question: 'Do you offer cloud solutions?',
      answer: 'Yes, we offer both on-premise and cloud deployment options to meet your specific needs.'
    }
  ],
  technical: [
    {
      question: 'What AI frameworks do you support?',
      answer: 'We support all major AI frameworks including TensorFlow, PyTorch, Keras, and more.'
    },
    {
      question: 'Can I upgrade my system later?',
      answer: 'Yes, our modular architecture allows for easy upgrades and expansion.'
    }
  ],
  pricing: [
    {
      question: 'Do you offer discounts for startups?',
      answer: 'Yes, we have a special startup program with significant discounts and additional benefits.'
    },
    {
      question: 'What payment options are available?',
      answer: 'We offer flexible payment options including monthly, annual, and custom enterprise contracts.'
    }
  ]
};
