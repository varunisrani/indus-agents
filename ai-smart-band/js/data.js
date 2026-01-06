const products = [
  {
    id: 1,
    name: 'AI Smart Band Pro',
    price: 299,
    description: 'Advanced AI-powered health and fitness tracking',
    features: ['AI Health Coach', 'ECG Monitoring', 'Blood Oxygen', 'Sleep Tracking'],
    colors: ['Black', 'Silver', 'Rose Gold'],
    image: '/assets/images/products/band-pro.jpg',
    badge: 'Best Seller'
  },
  {
    id: 2,
    name: 'AI Smart Band Lite',
    price: 199,
    description: 'Essential fitness tracking at an affordable price',
    features: ['Step Tracking', 'Heart Rate', 'Sleep Analysis', 'Smart Notifications'],
    colors: ['Black', 'Blue', 'Pink'],
    image: '/assets/images/products/band-lite.jpg',
    badge: 'Budget Friendly'
  },
  {
    id: 3,
    name: 'AI Smart Band Elite',
    price: 399,
    description: 'Premium features for serious athletes',
    features: ['Advanced AI Coaching', 'GPS Tracking', 'Water Resistant 5ATM', '14-Day Battery'],
    colors: ['Black', 'Titanium', 'Space Gray'],
    image: '/assets/images/products/band-elite.jpg',
    badge: 'Premium'
  }
];

const features = [
  {
    id: 1,
    icon: 'heart',
    title: 'Heart Rate Monitoring',
    description: '24/7 continuous heart rate tracking with advanced alerts',
    page: 'heart-rate.html'
  },
  {
    id: 2,
    icon: 'moon',
    title: 'Sleep Analysis',
    description: 'Detailed sleep stages analysis with personalized insights',
    page: 'sleep-monitoring.html'
  },
  {
    id: 3,
    icon: 'activity',
    title: 'Fitness Tracking',
    description: '100+ workout modes with real-time coaching',
    page: 'fitness-features.html'
  },
  {
    id: 4,
    icon: 'brain',
    title: 'AI Health Coach',
    description: 'Personalized recommendations powered by machine learning',
    page: 'smart-coaching.html'
  },
  {
    id: 5,
    icon: 'droplet',
    title: 'Blood Oxygen',
    description: 'SpO2 monitoring for respiratory health insights',
    page: 'blood-oxygen.html'
  },
  {
    id: 6,
    icon: 'zap',
    title: 'Stress Management',
    description: 'Track stress levels and get relaxation guidance',
    page: 'stress-management.html'
  }
];

const testimonials = [
  {
    id: 1,
    name: 'Sarah Johnson',
    role: 'Fitness Enthusiast',
    rating: 5,
    text: 'The AI Smart Band has completely transformed my fitness routine. The personalized coaching is incredible!',
    image: '/assets/images/testimonials/sarah.jpg'
  },
  {
    id: 2,
    name: 'Michael Chen',
    role: 'Marathon Runner',
    rating: 5,
    text: 'Best fitness tracker I\'ve ever used. The accuracy and battery life are unmatched.',
    image: '/assets/images/testimonials/michael.jpg'
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    role: 'Health Coach',
    rating: 5,
    text: 'I recommend this to all my clients. The health insights are professional-grade.',
    image: '/assets/images/testimonials/emily.jpg'
  }
];

const faqs = [
  {
    category: 'General',
    questions: [
      {
        q: 'What is the battery life of AI Smart Band?',
        a: 'The AI Smart Band Pro offers up to 7 days of battery life on a single charge. The Elite model extends this to 14 days, while the Lite version provides up to 5 days.'
      },
      {
        q: 'Is the band water-resistant?',
        a: 'Yes, all AI Smart Band models are water-resistant. The Pro and Elite models are rated 5ATM, suitable for swimming up to 50 meters. The Lite model is IP68 rated for everyday water exposure.'
      },
      {
        q: 'What smartphones are compatible?',
        a: 'AI Smart Band works with iOS 13+ and Android 8.0+. It\'s compatible with iPhone 6 and newer, and most Android phones including Samsung, Google Pixel, OnePlus, and more.'
      }
    ]
  },
  {
    category: 'Health & Fitness',
    questions: [
      {
        q: 'How accurate is the heart rate monitoring?',
        a: 'Our advanced optical heart rate sensor provides medical-grade accuracy with 98% precision compared to ECG machines. It continuously monitors your heart rate 24/7.'
      },
      {
        q: 'Can it track sleep stages?',
        a: 'Yes, the AI Smart Band tracks light sleep, deep sleep, and REM sleep stages. It also provides a sleep score and personalized recommendations for better rest.'
      },
      {
        q: 'Does it have built-in GPS?',
        a: 'The Elite model features built-in GPS for accurate tracking without your phone. The Pro and Lite models use connected GPS from your smartphone.'
      }
    ]
  },
  {
    category: 'Support',
    questions: [
      {
        q: 'What\'s included in the warranty?',
        a: 'All AI Smart Bands come with a 1-year limited warranty covering manufacturing defects. Extended warranty options are available for purchase.'
      },
      {
        q: 'How do I set up my device?',
        a: 'Download the AI Smart Band app, create an account, and follow the on-screen pairing instructions. Setup takes less than 5 minutes.'
      },
      {
        q: 'What if I need to return my device?',
        a: 'We offer a 30-day money-back guarantee. Contact our support team to initiate a return, and we\'ll provide a prepaid shipping label.'
      }
    ]
  }
];

const specifications = {
  display: {
    'Screen Size': '1.47 inch AMOLED',
    'Resolution': '368 x 194 pixels',
    'Brightness': '1000 nits',
    'Glass': 'Corning Gorilla Glass 3'
  },
  sensors: {
    'Heart Rate': 'Optical Heart Rate Sensor',
    'Blood Oxygen': 'SpO2 Sensor',
    'ECG': 'Single-lead ECG',
    'Accelerometer': '6-axis',
    'Gyroscope': 'Yes',
    'Ambient Light': 'Yes'
  },
  connectivity: {
    'Bluetooth': 'Bluetooth 5.2',
    'GPS': 'Built-in (Elite model)',
    'NFC': 'Yes (Pro & Elite)',
    'USB': 'USB-C Charging'
  },
  battery: {
    'Capacity': '180 mAh',
    'Battery Life': '7-14 days',
    'Charging Time': '2 hours',
    'Charger': 'Magnetic wireless charger'
  },
  physical: {
    'Weight': '32g (without strap)',
    'Strap Material': 'Silicone',
    'Strap Sizes': 'S/M, M/L, L/XL',
    'Water Resistance': '5ATM / IP68'
  }
};

const comparisonData = [
  {
    feature: 'AI Health Coach',
    lite: false,
    pro: true,
    elite: true
  },
  {
    feature: 'ECG Monitoring',
    lite: false,
    pro: true,
    elite: true
  },
  {
    feature: 'Blood Oxygen',
    lite: true,
    pro: true,
    elite: true
  },
  {
    feature: 'Sleep Stages',
    lite: 'Basic',
    pro: 'Advanced',
    elite: 'Advanced'
  },
  {
    feature: 'Built-in GPS',
    lite: false,
    pro: false,
    elite: true
  },
  {
    feature: 'Water Resistance',
    lite: 'IP68',
    pro: '5ATM',
    elite: '5ATM'
  },
  {
    feature: 'Battery Life',
    lite: '5 days',
    pro: '7 days',
    elite: '14 days'
  },
  {
    feature: 'NFC Payments',
    lite: false,
    pro: true,
    elite: true
  },
  {
    feature: 'Always-on Display',
    lite: false,
    pro: true,
    elite: true
  }
];

const accessories = [
  {
    id: 1,
    name: 'Premium Leather Strap',
    price: 49,
    image: '/assets/images/accessories/leather-strap.jpg',
    category: 'Bands'
  },
  {
    id: 2,
    name: 'Sport Silicone Strap',
    price: 29,
    image: '/assets/images/accessories/sport-strap.jpg',
    category: 'Bands'
  },
  {
    id: 3,
    name: 'Magnetic Charging Dock',
    price: 39,
    image: '/assets/images/accessories/charging-dock.jpg',
    category: 'Chargers'
  },
  {
    id: 4,
    name: 'Screen Protector Pack',
    price: 19,
    image: '/assets/images/accessories/screen-protector.jpg',
    category: 'Protection'
  },
  {
    id: 5,
    name: 'Travel Case',
    price: 35,
    image: '/assets/images/accessories/travel-case.jpg',
    category: 'Cases'
  }
];

const blogPosts = [
  {
    id: 1,
    title: '10 Tips for Better Sleep Tracking',
    excerpt: 'Learn how to get the most accurate sleep data from your AI Smart Band.',
    date: '2024-01-15',
    category: 'Health',
    image: '/assets/images/blog/sleep-tips.jpg'
  },
  {
    id: 2,
    title: 'Maximize Your Workout with AI Coaching',
    excerpt: 'Discover how our AI-powered coaching can transform your fitness routine.',
    date: '2024-01-10',
    category: 'Fitness',
    image: '/assets/images/blog/ai-coaching.jpg'
  },
  {
    id: 3,
    title: 'Understanding Heart Rate Zones',
    excerpt: 'A comprehensive guide to training in the right heart rate zones.',
    date: '2024-01-05',
    category: 'Education',
    image: '/assets/images/blog/heart-rate.jpg'
  }
];

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    products,
    features,
    testimonials,
    faqs,
    specifications,
    comparisonData,
    accessories,
    blogPosts
  };
}
