const productsData = {
  smartBand: {
    name: 'AI Smart Band Pro',
    price: 299,
    features: [
      'Advanced AI Health Monitoring',
      '7-Day Battery Life',
      'Water Resistant (5ATM)',
      'AMOLED Display',
      'GPS Tracking',
      'Sleep Analysis'
    ],
    specs: {
      display: '1.47" AMOLED',
      battery: '180mAh',
      sensors: 'Heart Rate, SpO2, Accelerometer, Gyroscope',
      connectivity: 'Bluetooth 5.2, GPS',
      waterResistance: '5ATM (50 meters)',
      weight: '32g'
    }
  },
  smartBandLite: {
    name: 'AI Smart Band Lite',
    price: 199,
    features: [
      'Essential Health Tracking',
      '14-Day Battery Life',
      'Water Resistant (IP68)',
      'TFT Display',
      'Basic Activity Tracking'
    ],
    specs: {
      display: '1.1" TFT',
      battery: '150mAh',
      sensors: 'Heart Rate, Accelerometer',
      connectivity: 'Bluetooth 5.0',
      waterResistance: 'IP68',
      weight: '28g'
    }
  }
};

const featuresData = {
  healthTracking: {
    title: 'Comprehensive Health Tracking',
    items: [
      {
        icon: '❤️',
        title: 'Heart Rate Monitoring',
        description: '24/7 continuous heart rate tracking with instant alerts for abnormal readings'
      },
      {
        icon: '💤',
        title: 'Sleep Analysis',
        description: 'Detailed sleep stage analysis with personalized insights and improvement tips'
      },
      {
        icon: '🩸',
        title: 'Blood Oxygen',
        description: 'SpO2 monitoring for respiratory health and altitude tracking'
      },
      {
        icon: '😌',
        title: 'Stress Management',
        description: 'AI-powered stress detection with guided breathing exercises'
      }
    ]
  },
  fitnessFeatures: {
    title: 'Advanced Fitness Features',
    items: [
      {
        icon: '🏃',
        title: '100+ Workout Modes',
        description: 'Track running, cycling, swimming, yoga, and 97 more activities'
      },
      {
        icon: '🎯',
        title: 'Smart Coaching',
        description: 'AI-powered personalized training plans adapted to your goals'
      },
      {
        icon: '📊',
        title: 'Performance Analytics',
        description: 'In-depth analysis of your workouts with progress tracking'
      },
      {
        icon: '🏆',
        title: 'Goal Setting',
        description: 'Set and track custom fitness goals with smart reminders'
      }
    ]
  }
};

const testimonialsData = [
  {
    name: 'Sarah Johnson',
    title: 'Fitness Enthusiast',
    quote: 'The AI Smart Band has completely transformed how I track my health. The insights are incredibly accurate and actionable.',
    rating: 5
  },
  {
    name: 'Michael Chen',
    title: 'Marathon Runner',
    quote: 'Best fitness tracker I\'ve ever used. The smart coaching feature helped me improve my marathon time by 15 minutes!',
    rating: 5
  },
  {
    name: 'Emily Rodriguez',
    title: 'Health Coach',
    quote: 'I recommend the AI Smart Band to all my clients. The comprehensive health data is unmatched in the market.',
    rating: 5
  }
];

const faqData = {
  general: [
    {
      question: 'What is the battery life of the AI Smart Band?',
      answer: 'The AI Smart Band Pro offers up to 7 days of battery life on a single charge, while the Lite version provides up to 14 days. Actual battery life may vary based on usage patterns and settings.'
    },
    {
      question: 'Is the AI Smart Band water-resistant?',
      answer: 'Yes! The Pro model is water-resistant up to 5ATM (50 meters), making it suitable for swimming. The Lite model has an IP68 rating, which protects against dust and water splashes.'
    },
    {
      question: 'What smartphones are compatible?',
      answer: 'The AI Smart Band is compatible with both iOS (iPhone 8 and later) and Android (Android 8.0 and later) devices via our companion app.'
    }
  ],
  health: [
    {
      question: 'How accurate is the heart rate monitoring?',
      answer: 'Our advanced optical heart rate sensor provides medical-grade accuracy with 98% correlation to ECG measurements. It continuously monitors your heart rate 24/7.'
    },
    {
      question: 'Can it detect sleep apnea?',
      answer: 'While the AI Smart Band monitors sleep patterns and can detect irregular breathing, it is not a medical device and cannot diagnose sleep apnea. Consult a healthcare professional for diagnosis.'
    },
    {
      question: 'How does stress tracking work?',
      answer: 'The band uses Heart Rate Variability (HRV) analysis to detect stress levels. When elevated stress is detected, you\'ll receive notifications and guided breathing exercises to help you relax.'
    }
  ],
  technical: [
    {
      question: 'How do I sync my data?',
      answer: 'Data syncs automatically via Bluetooth 5.2 when your phone is within range. You can also manually sync by opening the companion app and pulling down to refresh.'
    },
    {
      question: 'Is my health data secure?',
      answer: 'Absolutely. All data is encrypted end-to-end and stored on secure servers compliant with HIPAA and GDPR regulations. You maintain full control over your data.'
    },
    {
      question: 'What is the warranty period?',
      answer: 'The AI Smart Band comes with a 1-year limited warranty covering manufacturing defects. Extended warranty options are available for purchase.'
    }
  ]
};

const accessoriesData = [
  {
    name: 'Premium Leather Band',
    price: 49,
    image: 'leather-band.jpg',
    description: 'Genuine leather replacement band for everyday elegance'
  },
  {
    name: 'Sport Silicone Band',
    price: 29,
    image: 'sport-band.jpg',
    description: 'Breathable silicone band perfect for workouts'
  },
  {
    name: 'Magnetic Charging Cable',
    price: 19,
    image: 'charging-cable.jpg',
    description: 'Spare magnetic charging cable for home or office'
  },
  {
    name: 'Screen Protection Pack',
    price: 15,
    image: 'screen-protector.jpg',
    description: '3-pack of tempered glass screen protectors'
  }
];

const blogData = [
  {
    title: '10 Tips to Improve Your Sleep Quality',
    excerpt: 'Discover how the AI Smart Band can help you understand and optimize your sleep patterns for better rest and recovery.',
    date: '2024-01-15',
    category: 'Health',
    image: 'sleep-tips.jpg'
  },
  {
    title: 'Maximize Your Workout Results',
    excerpt: 'Learn how to use smart coaching features to take your fitness to the next level with personalized training plans.',
    date: '2024-01-12',
    category: 'Fitness',
    image: 'workout-tips.jpg'
  },
  {
    title: 'Understanding Heart Rate Zones',
    excerpt: 'A comprehensive guide to training in different heart rate zones for optimal cardiovascular health.',
    date: '2024-01-10',
    category: 'Education',
    image: 'heart-rate-zones.jpg'
  }
];
