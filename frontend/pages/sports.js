import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Trophy, TrendingUp, Users, Calendar, ArrowLeft, Send } from 'lucide-react';
import { chatAPI } from '@/utils/apiClient';

export default function SportsPage() {
  const router = useRouter();
  const [selectedSport, setSelectedSport] = useState('cricket');
  const [queryType, setQueryType] = useState('prediction');
  const [matchDetails, setMatchDetails] = useState('');
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

  const sports = [
    { value: 'cricket', label: 'Cricket', emoji: '🏏' },
    { value: 'football', label: 'Football', emoji: '⚽' }
  ];

  const queryTypes = [
    { value: 'prediction', label: 'Match Prediction', icon: TrendingUp, desc: 'AI-powered win probability' },
    { value: 'stats', label: 'Player Stats', icon: Users, desc: 'Performance analysis' },
    { value: 'comparison', label: 'Player Comparison', icon: Users, desc: 'Head-to-head stats' },
    { value: 'team_analysis', label: 'Team Analysis', icon: Trophy, desc: 'Form & strengths' },
    { value: 'upcoming', label: 'Upcoming Matches', icon: Calendar, desc: 'Schedule & predictions' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!matchDetails.trim() || !userId) return;
    
    setLoading(true);

    try {
      // Build friendly display message for user
      const sportEmoji = sports.find(s => s.value === selectedSport)?.emoji || '🏏';
      const displayMsg = `${sportEmoji} ${selectedSport.charAt(0).toUpperCase() + selectedSport.slice(1)} ${queryType === 'prediction' ? 'prediction' : queryType} for ${matchDetails}`;
      
      // Add user message to chat
      setMessages(prev => [...prev, { role: 'user', content: displayMsg }]);
      
      // Build detailed query for backend
      let query = `🏏 **${selectedSport.toUpperCase()} ${queryType.toUpperCase()}**\n\n`;
      
      if (queryType === 'prediction') {
        query += `🎯 **Match Prediction**\nMatch: ${matchDetails}\n\nAnalyze and predict:\n• Current team form\n• Player stats\n• Head-to-head\n• Win probability`;
      } else if (queryType === 'stats') {
        query += `📊 **Statistics**\nTeam/Player: ${matchDetails}\n\nShow comprehensive stats`;
      } else if (queryType === 'comparison') {
        query += `⚖️ **Player Comparison**\nPlayers: ${matchDetails}\n\nCompare stats and performance`;
      } else if (queryType === 'team_analysis') {
        query += `🔍 **Team Analysis**\nTeam: ${matchDetails}\n\nAnalyze strengths, weaknesses, form`;
      } else if (queryType === 'upcoming') {
        query += `📅 **Upcoming Matches**\nTeam: ${matchDetails}\n\nShow schedule and predictions`;
      }

      // Call API directly - NO REDIRECT
      const response = await chatAPI.send({
        user_id: userId,
        message: query,
        conversation_id: `sports_${Date.now()}`,
        include_web_search: true,
        language: 'english'
      });

      // Add AI response to chat
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
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 mb-4 text-orange-100 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </button>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <Trophy size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Sports Predictions & Analysis</h1>
              <p className="text-orange-100 mt-1">Cricket & Football predictions, stats, and team analysis</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-6">
        {/* Show form only if showForm is true */}
        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 space-y-6">
          {/* Sport Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Select Sport *
            </label>
            <div className="grid grid-cols-2 gap-4">
              {sports.map((sport) => (
                <button
                  key={sport.value}
                  type="button"
                  onClick={() => setSelectedSport(sport.value)}
                  className={`p-6 rounded-xl border-2 transition-all ${
                    selectedSport === sport.value
                      ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-orange-300'
                  }`}
                >
                  <div className="text-5xl mb-3">{sport.emoji}</div>
                  <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {sport.label}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Query Type Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              What do you need? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {queryTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setQueryType(type.value)}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      queryType === type.value
                        ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20 shadow-lg'
                        : 'border-gray-200 dark:border-gray-700 hover:border-orange-300'
                    }`}
                  >
                    <Icon size={24} className={`mb-2 ${queryType === type.value ? 'text-orange-600' : 'text-gray-600'}`} />
                    <div className="font-bold text-gray-900 dark:text-gray-100">{type.label}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{type.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Match/Team Details */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Match or Team Details (Optional)
            </label>
            <input
              type="text"
              value={matchDetails}
              onChange={(e) => setMatchDetails(e.target.value)}
              placeholder={
                queryType === 'prediction' ? 'e.g., India vs Australia' :
                queryType === 'comparison' ? 'e.g., Virat Kohli vs Steve Smith' :
                queryType === 'stats' ? 'e.g., Virat Kohli' :
                'e.g., Team name or player name'
              }
              className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-orange-500 focus:outline-none dark:bg-gray-700 dark:text-gray-100"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              💡 Tip: Be specific for better predictions (e.g., "India vs Australia ODI 2026")
            </p>
          </div>

          {/* Popular Queries */}
          <div className="bg-orange-50 dark:bg-orange-900/10 rounded-xl p-4">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              🔥 Popular Queries:
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                'IPL 2026 predictions',
                'Virat Kohli stats',
                'India vs Pakistan prediction',
                'Premier League analysis',
                'Messi vs Ronaldo',
                'Champions League predictions'
              ].map((query) => (
                <button
                  key={query}
                  type="button"
                  onClick={() => setMatchDetails(query)}
                  className="px-3 py-1.5 bg-white dark:bg-gray-700 text-sm rounded-lg border border-orange-200 dark:border-orange-800 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !userId}
            className="w-full py-4 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl font-bold text-lg hover:from-orange-700 hover:to-red-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                <Send size={20} />
                Get Analysis
              </>
            )}
          </button>

          {/* Info Box */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold">✨ Smart Caching:</span> Predictions are cached and shared with all users for efficiency. 
              Premium users get priority access to fresh predictions.
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
                <Trophy size={24} className="text-orange-500" />
                Analysis & Chat
              </h2>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg font-semibold hover:bg-orange-600 transition-colors flex items-center gap-2"
              >
                <TrendingUp size={16} />
                New Query
              </button>
            </div>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-orange-50 dark:bg-orange-900/20 ml-auto max-w-[80%]'
                    : 'bg-gray-50 dark:bg-gray-700 mr-auto max-w-[95%]'
                }`}
              >
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">
                  {msg.role === 'user' ? '👤 You' : '🤖 MyDost'}
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
                Analyzing expert sources...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
