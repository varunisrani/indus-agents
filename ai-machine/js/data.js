const productsData = {
  aiServer: {
    name: 'AI Server Pro X1',
    category: 'AI Servers',
    price: 'Contact Sales',
    features: [
      '8x NVIDIA A100 GPUs',
      '2TB High-Speed Memory',
      '100Gbps Networking',
      'Enterprise Support',
      '99.9% Uptime SLA'
    ],
    specs: {
      processors: 'Dual AMD EPYC 7763',
      memory: '2TB DDR4 ECC',
      storage: '30TB NVMe SSD',
      networking: '100Gbps InfiniBand',
      power: '3000W PSU',
      cooling: 'Liquid Cooling Ready'
    }
  },
  edgeDevice: {
    name: 'Edge AI Module',
    category: 'Edge Computing',
    price: 'Contact Sales',
    features: [
      'Compact Form Factor',
      'Low Power Consumption',
      'Real-time Inference',
      'Industrial Grade',
      'Easy Deployment'
    ],
    specs: {
      processor: 'Custom Neural Processor',
      memory: '32GB LPDDR5',
      storage: '512GB NVMe',
      power: '15W TDP',
      operatingTemp: '-40°C to 85°C',
      certifications: 'IP67 Rated'
    }
  },
  neuralChip: {
    name: 'NeuralCore N1',
    category: 'Neural Chips',
    price: 'Contact Sales',
    features: [
      'Custom Architecture',
      'High Performance',
      'Energy Efficient',
      'Scalable Design',
      'Developer Support'
    ],
    specs: {
      architecture: 'Custom Neural Engine',
      performance: '500 TOPS',
      power: '75W TDP',
      memory: '256GB HBM3',
      interface: 'PCIe 5.0',
      manufacturing: '5nm Process'
    }
  }
};

const caseStudiesData = [
  {
    company: 'TechCorp Global',
    industry: 'Financial Services',
    title: 'Reducing Fraud Detection Time by 90%',
    summary: 'How TechCorp implemented our AI infrastructure to process millions of transactions in real-time.',
    results: [
      '90% faster fraud detection',
      '99.5% accuracy rate',
      '50% cost reduction',
      '24/7 monitoring capability'
    ],
    metrics: {
      performance: '10x',
      accuracy: '99.5%',
      cost: '-50%',
      uptime: '99.99%'
    }
  },
  {
    company: 'HealthTech Solutions',
    industry: 'Healthcare',
    title: 'AI-Powered Medical Imaging Analysis',
    summary: 'Deploying edge AI devices for real-time medical image analysis in hospitals.',
    results: [
      '85% faster diagnosis',
      'Improved patient outcomes',
      'Reduced specialist workload',
      'HIPAA compliant'
    ],
    metrics: {
      speed: '85%',
      accuracy: '97%',
      patients: '+40%',
      compliance: '100%'
    }
  },
  {
    company: 'AutoDrive Inc',
    industry: 'Automotive',
    title: 'Autonomous Vehicle Training Infrastructure',
    summary: 'Building scalable AI infrastructure for autonomous vehicle development.',
    results: [
      '1000+ models trained',
      'Reduced training time by 70%',
      'Improved model accuracy',
      'Scalable architecture'
    ],
    metrics: {
      models: '1000+',
      trainingTime: '-70%',
      accuracy: '+15%',
      scalability: 'Unlimited'
    }
  }
];

const pricingData = {
  standard: {
    name: 'Standard',
    price: '$2,999',
    period: '/month',
    features: [
      '1 AI Server Unit',
      'Basic Support',
      '99.5% Uptime SLA',
      'Standard APIs',
      'Community Access'
    ],
    cta: 'Get Started'
  },
  professional: {
    name: 'Professional',
    price: '$9,999',
    period: '/month',
    features: [
      '4 AI Server Units',
      'Priority Support',
      '99.9% Uptime SLA',
      'Advanced APIs',
      'Developer Tools',
      'Training Resources'
    ],
    cta: 'Contact Sales',
    featured: true
  },
  enterprise: {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    features: [
      'Unlimited AI Servers',
      '24/7 Dedicated Support',
      '99.99% Uptime SLA',
      'Custom Solutions',
      'On-premise Deployment',
      'Professional Services',
      'SLA Guarantees'
    ],
    cta: 'Contact Sales'
  }
};

const documentationData = {
  gettingStarted: [
    {
      title: 'Quick Start Guide',
      description: 'Get up and running with AI Machine in minutes',
      link: '#quick-start'
    },
    {
      title: 'Installation',
      description: 'Step-by-step installation instructions',
      link: '#installation'
    },
    {
      title: 'Configuration',
      description: 'Configure your AI infrastructure',
      link: '#configuration'
    }
  ],
  api: [
    {
      title: 'API Overview',
      description: 'Introduction to the AI Machine API',
      link: '#api-overview'
    },
    {
      title: 'Authentication',
      description: 'Secure authentication methods',
      link: '#authentication'
    },
    {
      title: 'Endpoints',
      description: 'Complete API endpoint reference',
      link: '#endpoints'
    }
  ],
  guides: [
    {
      title: 'Model Training',
      description: 'Train custom AI models',
      link: '#model-training'
    },
    {
      title: 'Deployment',
      description: 'Deploy models to production',
      link: '#deployment'
    },
    {
      title: 'Monitoring',
      description: 'Monitor your AI infrastructure',
      link: '#monitoring'
    }
  ]
};

const faqData = {
  general: [
    {
      question: 'What is AI Machine?',
      answer: 'AI Machine is a comprehensive AI infrastructure platform providing high-performance servers, edge computing devices, and custom neural chips for enterprise AI applications.'
    },
    {
      question: 'How do I get started?',
      answer: 'You can start with our Standard plan or contact our sales team for enterprise solutions. We offer free consultations to help you choose the right infrastructure for your needs.'
    },
    {
      question: 'What support options are available?',
      answer: 'We offer multiple support tiers including community support, standard business hours support, and 24/7 dedicated support for enterprise customers.'
    }
  ],
  technical: [
    {
      question: 'What programming languages are supported?',
      answer: 'AI Machine supports Python, TensorFlow, PyTorch, scikit-learn, and most popular AI/ML frameworks. Our APIs are RESTful and can be accessed from any language.'
    },
    {
      question: 'How do I scale my infrastructure?',
      answer: 'Our platform is designed for seamless scaling. You can add more server units, deploy edge devices, or upgrade to enterprise plans for unlimited scalability.'
    },
    {
      question: 'Is my data secure?',
      answer: 'Absolutely. We implement enterprise-grade security including encryption at rest and in transit, SOC 2 Type II compliance, and GDPR compliance. Data isolation is guaranteed.'
    }
  ],
  billing: [
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, wire transfers, and offer annual billing with discounts. Enterprise customers can set up custom billing arrangements.'
    },
    {
      question: 'Can I upgrade or downgrade my plan?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect at the start of your next billing cycle.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'We offer a 14-day free trial for our Standard plan. Contact sales for enterprise trial options.'
    }
  ]
};

const blogData = [
  {
    title: 'The Future of AI Infrastructure',
    excerpt: 'Exploring emerging trends in AI hardware and infrastructure design for enterprise applications.',
    date: '2024-01-15',
    category: 'Technology',
    author: 'Dr. Sarah Chen',
    image: 'ai-infrastructure.jpg'
  },
  {
    title: 'Optimizing Model Performance',
    excerpt: 'Best practices for getting the most out of your AI infrastructure and maximizing model efficiency.',
    date: '2024-01-12',
    category: 'Engineering',
    author: 'Mark Johnson',
    image: 'model-optimization.jpg'
  },
  {
    title: 'Edge AI: Computing at the Source',
    excerpt: 'Understanding the benefits and challenges of deploying AI models at the edge.',
    date: '2024-01-10',
    category: 'Innovation',
    author: 'Lisa Park',
    image: 'edge-ai.jpg'
  }
];
