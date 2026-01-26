import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Sparkles, Heart, Star, TrendingUp, ArrowLeft, Send } from 'lucide-react';
import { chatAPI } from '@/utils/apiClient';

export default function HoroscopePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    zodiacSign: '',
    queryType: 'daily',
    partnerSign: ''
  });
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userId, setUserId] = useState('');
  const [showForm, setShowForm] = useState(true);

  // Generate user ID on mount
  React.useEffect(() => {
    const guestId = localStorage.getItem('guest_id') || `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('guest_id', guestId);
    setUserId(guestId);
  }, []);

  const zodiacSigns = [
    { value: 'aries', label: 'Aries', emoji: '♈', dates: 'Mar 21 - Apr 19' },
    { value: 'taurus', label: 'Taurus', emoji: '♉', dates: 'Apr 20 - May 20' },
    { value: 'gemini', label: 'Gemini', emoji: '♊', dates: 'May 21 - Jun 20' },
    { value: 'cancer', label: 'Cancer', emoji: '♋', dates: 'Jun 21 - Jul 22' },
    { value: 'leo', label: 'Leo', emoji: '♌', dates: 'Jul 23 - Aug 22' },
    { value: 'virgo', label: 'Virgo', emoji: '♍', dates: 'Aug 23 - Sep 22' },
    { value: 'libra', label: 'Libra', emoji: '♎', dates: 'Sep 23 - Oct 22' },
    { value: 'scorpio', label: 'Scorpio', emoji: '♏', dates: 'Oct 23 - Nov 21' },
    { value: 'sagittarius', label: 'Sagittarius', emoji: '♐', dates: 'Nov 22 - Dec 21' },
    { value: 'capricorn', label: 'Capricorn', emoji: '♑', dates: 'Dec 22 - Jan 19' },
    { value: 'aquarius', label: 'Aquarius', emoji: '♒', dates: 'Jan 20 - Feb 18' },
    { value: 'pisces', label: 'Pisces', emoji: '♓', dates: 'Feb 19 - Mar 20' }
  ];

  const queryTypes = [
    { value: 'daily', label: 'Daily Horoscope', icon: Star, desc: 'Today\'s prediction' },
    { value: 'weekly', label: 'Weekly Horoscope', icon: TrendingUp, desc: 'This week\'s forecast' },
    { value: 'monthly', label: 'Monthly Horoscope', icon: Sparkles, desc: 'This month\'s overview' },
    { value: 'love', label: 'Love & Relationships', icon: Heart, desc: 'Romantic forecast' },
    { value: 'compatibility', label: 'Compatibility', icon: Heart, desc: 'Match with partner sign' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.zodiacSign || !userId) return;
    
    setLoading(true);

    try {
      const selectedSign = zodiacSigns.find(s => s.value === formData.zodiacSign);
      
      // Build friendly display message
      const queryTypeLabel = queryTypes.find(t => t.value === formData.queryType)?.label || '';
      const displayMsg = formData.queryType === 'compatibility' 
        ? `${selectedSign?.emoji} ${selectedSign?.label} ❤️ ${zodiacSigns.find(s => s.value === formData.partnerSign)?.label} - Compatibility`
        : `${selectedSign?.emoji} ${selectedSign?.label} - ${queryTypeLabel}`;
      
      // Add user message
      setMessages(prev => [...prev, { role: 'user', content: displayMsg }]);
      
      // Build detailed query
      let query = `✨ HOROSCOPE REQUEST\n`;
      query += `Zodiac Sign: ${selectedSign?.label} ${selectedSign?.emoji}\n`;
      query += `Type: ${formData.queryType}\n\n`;
      
      if (formData.queryType === 'daily') {
        query += `Give me today's horoscope for ${selectedSign?.label}. Include predictions for love, career, health, and lucky numbers.`;
      } else if (formData.queryType === 'weekly') {
        query += `Provide this week's horoscope for ${selectedSign?.label}. Include major themes, opportunities, and challenges.`;
      } else if (formData.queryType === 'monthly') {
        query += `Give me this month's detailed horoscope for ${selectedSign?.label}. Cover career, love, health, and finances.`;
      } else if (formData.queryType === 'love') {
        query += `Tell me about love and relationship prospects for ${selectedSign?.label}. Include dating advice and relationship insights.`;
      } else if (formData.queryType === 'compatibility') {
        const partnerSign = zodiacSigns.find(s => s.value === formData.partnerSign);
        query += `Analyze compatibility between ${selectedSign?.label} and ${partnerSign?.label}. Include love compatibility, friendship potential, and relationship advice.`;
      }

      query += `\n\nIMPORTANT: Use horoscope API if available, otherwise provide general astrological insights.`;

      // Call API directly - NO REDIRECT
      const response = await chatAPI.send({
        user_id: userId,
        message: query,
        conversation_id: `horoscope_${Date.now()}`,
        include_web_search: false,
        language: 'english'
      });

      // Add AI response
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
      
      // Hide form after successful submission
      setShowForm(false);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Sorry, something went wrong. Please try again!' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 mb-4 text-purple-100 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </button>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <Sparkles size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Horoscope & Astrology</h1>
              <p className="text-purple-100 mt-1">Daily predictions, compatibility, and cosmic insights</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-6">
        {/* Show form only if showForm is true */}
        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 space-y-6">
          {/* Zodiac Sign Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Select Your Zodiac Sign *
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {zodiacSigns.map((sign) => (
                <button
                  key={sign.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, zodiacSign: sign.value })}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    formData.zodiacSign === sign.value
                      ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                  }`}
                >
                  <div className="text-3xl mb-2">{sign.emoji}</div>
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {sign.label}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {sign.dates}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Query Type */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              What would you like to know? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {queryTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, queryType: type.value })}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      formData.queryType === type.value
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-lg'
                        : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                    }`}
                  >
                    <Icon size={24} className={`mb-2 ${formData.queryType === type.value ? 'text-purple-600' : 'text-gray-600'}`} />
                    <div className="font-bold text-gray-900 dark:text-gray-100">{type.label}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{type.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Partner Sign (for compatibility) */}
          {formData.queryType === 'compatibility' && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Partner's Zodiac Sign *
              </label>
              <select
                value={formData.partnerSign}
                onChange={(e) => setFormData({ ...formData, partnerSign: e.target.value })}
                required={formData.queryType === 'compatibility'}
                className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-purple-500 focus:outline-none dark:bg-gray-700 dark:text-gray-100"
              >
                <option value="">Select partner's sign</option>
                {zodiacSigns.map((sign) => (
                  <option key={sign.value} value={sign.value}>
                    {sign.emoji} {sign.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !formData.zodiacSign || (formData.queryType === 'compatibility' && !formData.partnerSign) || !userId}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold text-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Reading Stars...
              </>
            ) : (
              <>
                <Send size={20} />
                Get My Horoscope
              </>
            )}
          </button>

          {/* Info Box */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold">🌟 Cosmic Insights:</span> Our horoscopes combine traditional astrology with modern AI analysis for personalized predictions.
            </p>
          </div>
        </form>
        )}

        {/* Chat Messages - EMBEDDED ON PAGE */}
        {messages.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 space-y-4">
            {/* New Query Button */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                <Sparkles size={24} className="text-purple-500" />
                Your Horoscope
              </h2>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg font-semibold hover:bg-purple-600 transition-colors flex items-center gap-2"
              >
                <Star size={16} />
                New Reading
              </button>
            </div>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-purple-50 dark:bg-purple-900/20 ml-auto max-w-[80%]'
                    : 'bg-gray-50 dark:bg-gray-700 mr-auto max-w-[95%]'
                }`}
              >
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">
                  {msg.role === 'user' ? '👤 You' : '🔮 MyDost'}
                </div>
                <div className="text-gray-800 dark:text-gray-200 prose prose-sm max-w-none whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            ))}
            
            {/* Loading State */}
            {loading && (
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-4 rounded-xl">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Consulting the stars...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
