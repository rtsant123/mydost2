import React from 'react';
import { useRouter } from 'next/router';
import { X, Trophy, Target, Newspaper, Heart, TrendingUp, Globe, Brain, Music, Film } from 'lucide-react';

export default function MoreDomainsModal({ isOpen, onClose, onSelectDomain }) {
  const router = useRouter();
  const domains = [
    { 
      icon: '📄', 
      name: 'PDF Tools', 
      description: 'Upload, summarize & chat with PDFs',
      color: 'red',
      action: () => router.push('/tools/pdf')
    },
    { 
      icon: '🔍', 
      name: 'OCR - Text Extract', 
      description: 'Extract text from images (4 languages)',
      color: 'blue',
      action: () => router.push('/tools/ocr')
    },
    { 
      icon: '🧪', 
      name: 'Test Web Search', 
      description: 'Test sports predictions & web search',
      color: 'green',
      action: () => router.push('/tools/test-search')
    },
    { 
      icon: '🎯', 
      name: 'Teer Results', 
      description: 'Shillong Teer results & predictions',
      color: 'green',
      query: 'Show me today\'s Teer results'
    },
    { 
      icon: '📰', 
      name: 'News & Updates', 
      description: 'Latest news from around the world',
      color: 'blue',
      query: 'Show me today\'s top news headlines'
    },
    { 
      icon: '💊', 
      name: 'Health & Wellness', 
      description: 'Health tips, diet & fitness advice',
      color: 'pink',
      query: 'I need health and wellness advice'
    },
    { 
      icon: '📈', 
      name: 'Stock Market', 
      description: 'Stock prices & market analysis',
      color: 'teal',
      query: 'Show me stock market updates'
    },
    { 
      icon: '🌍', 
      name: 'Weather', 
      description: 'Weather forecasts & updates',
      color: 'sky',
      query: 'What\'s the weather today?'
    },
    { 
      icon: '🧠', 
      name: 'General Knowledge', 
      description: 'Facts, trivia & information',
      color: 'purple',
      query: 'I want to learn general knowledge'
    },
    { 
      icon: '🎵', 
      name: 'Entertainment', 
      description: 'Movies, music & celebrities',
      color: 'red',
      query: 'Tell me about latest entertainment news'
    },
    { 
      icon: '💼', 
      name: 'Career & Jobs', 
      description: 'Job search & career guidance',
      color: 'indigo',
      query: 'I need career advice'
    },
    { 
      icon: '🍳', 
      name: 'Recipes & Cooking', 
      description: 'Food recipes & cooking tips',
      color: 'amber',
      query: 'Show me some easy recipes'
    },
    { 
      icon: '✈️', 
      name: 'Travel', 
      description: 'Travel tips & destinations',
      color: 'cyan',
      query: 'I want travel recommendations'
    },
    { 
      icon: '💰', 
      name: 'Finance', 
      description: 'Personal finance & investment tips',
      color: 'emerald',
      query: 'I need personal finance advice'
    }
  ];

  const colorClasses = {
    orange: 'border-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/20',
    green: 'border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20',
    blue: 'border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20',
    pink: 'border-pink-500 hover:bg-pink-50 dark:hover:bg-pink-900/20',
    teal: 'border-teal-500 hover:bg-teal-50 dark:hover:bg-teal-900/20',
    sky: 'border-sky-500 hover:bg-sky-50 dark:hover:bg-sky-900/20',
    purple: 'border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20',
    red: 'border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20',
    indigo: 'border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20',
    amber: 'border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/20',
    cyan: 'border-cyan-500 hover:bg-cyan-50 dark:hover:bg-cyan-900/20',
    emerald: 'border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/20'
  };

  const handleDomainClick = (domain) => {
    if (domain.action) {
      // Navigate to page
      domain.action();
      onClose();
    } else {
      // Send query to chat
      onSelectDomain(domain.query);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span className="text-3xl">🔮</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">All Domains</h2>
              <p className="text-white/80 text-sm">Choose what you need help with</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Domains Grid */}
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {domains.map((domain, index) => (
              <button
                key={index}
                onClick={() => handleDomainClick(domain)}
                className={`group p-4 bg-white dark:bg-gray-800 rounded-xl border-2 ${colorClasses[domain.color]} transition-all hover:shadow-lg hover:-translate-y-1 text-left`}
              >
                <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
                  {domain.icon}
                </div>
                <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {domain.name}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {domain.description}
                </p>
              </button>
            ))}
          </div>

          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl">
            <p className="text-sm text-gray-700 dark:text-gray-300 text-center">
              💡 <strong>Tip:</strong> You can also just type what you need - I&apos;ll understand!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
