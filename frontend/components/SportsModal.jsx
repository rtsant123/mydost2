import React, { useState } from 'react';
import { X, Trophy } from 'lucide-react';

export default function SportsModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    sport: 'cricket',
    queryType: 'live',
    team: '',
    match: ''
  });

  const sports = [
    { value: 'cricket', label: '🏏 Cricket', emoji: '🏏' },
    { value: 'football', label: '⚽ Football', emoji: '⚽' },
    { value: 'tennis', label: '🎾 Tennis', emoji: '🎾' },
    { value: 'badminton', label: '🏸 Badminton', emoji: '🏸' },
    { value: 'hockey', label: '🏑 Hockey', emoji: '🏑' },
    { value: 'kabaddi', label: '🤼 Kabaddi', emoji: '🤼' }
  ];

  const queryTypes = [
    { value: 'live', label: '🔴 Live Scores', description: 'Current match scores' },
    { value: 'upcoming', label: '📅 Upcoming Matches', description: 'Schedule & fixtures' },
    { value: 'results', label: '🏆 Recent Results', description: 'Latest match results' },
    { value: 'prediction', label: '🔮 Match Prediction', description: 'Analysis & predictions' },
    { value: 'stats', label: '📊 Player/Team Stats', description: 'Statistics & records' },
    { value: 'news', label: '📰 Sports News', description: 'Latest updates' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const sportEmoji = sports.find(s => s.value === formData.sport)?.emoji || '🏆';
    const queryLabel = queryTypes.find(q => q.value === formData.queryType)?.label || '';
    
    let query = `${sportEmoji} SPORTS QUERY - Use cached data if available\n`;
    query += `Sport: ${formData.sport.toUpperCase()}\n`;
    query += `Request: ${queryLabel}\n\n`;
    
    if (formData.queryType === 'live') {
      query += `Show me live ${formData.sport} scores`;
      if (formData.match) query += ` for ${formData.match}`;
    } else if (formData.queryType === 'upcoming') {
      query += `Show upcoming ${formData.sport} matches`;
      if (formData.team) query += ` for ${formData.team}`;
    } else if (formData.queryType === 'results') {
      query += `Show recent ${formData.sport} results`;
      if (formData.match) query += ` for ${formData.match}`;
    } else if (formData.queryType === 'prediction') {
      query += `Give match prediction for ${formData.sport}`;
      if (formData.match) query += ` - ${formData.match}`;
      query += `. Use database records and web search for latest form.`;
    } else if (formData.queryType === 'stats') {
      query += `Show ${formData.sport} statistics`;
      if (formData.team) query += ` for ${formData.team}`;
    } else if (formData.queryType === 'news') {
      query += `Show latest ${formData.sport} news`;
    }

    onSubmit(query);
    onClose();
    
    // Reset form
    setFormData({
      sport: 'cricket',
      queryType: 'live',
      team: '',
      match: ''
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-orange-500 to-red-500 p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Trophy size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Sports Updates</h2>
              <p className="text-orange-100 text-sm">Get live scores, predictions & more</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Sport Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Select Sport *
            </label>
            <div className="grid grid-cols-3 gap-3">
              {sports.map((sport) => (
                <button
                  key={sport.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, sport: sport.value })}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    formData.sport === sport.value
                      ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-orange-300'
                  }`}
                >
                  <div className="text-3xl mb-2">{sport.emoji}</div>
                  <div className="font-semibold text-xs text-gray-900 dark:text-gray-100">
                    {sport.label.replace(/[^\w\s]/gi, '')}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Query Type Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              What do you want? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {queryTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, queryType: type.value })}
                  className={`p-3 rounded-xl border-2 transition-all text-left ${
                    formData.queryType === type.value
                      ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-orange-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                    {type.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {type.description}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Optional Filters */}
          {(formData.queryType === 'upcoming' || formData.queryType === 'stats') && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Team Name (Optional)
              </label>
              <input
                type="text"
                value={formData.team}
                onChange={(e) => setFormData({ ...formData, team: e.target.value })}
                placeholder="e.g., India, Mumbai Indians, etc."
                className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-orange-500 focus:outline-none placeholder-gray-400"
              />
            </div>
          )}

          {(formData.queryType === 'live' || formData.queryType === 'results' || formData.queryType === 'prediction') && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Specific Match (Optional)
              </label>
              <input
                type="text"
                value={formData.match}
                onChange={(e) => setFormData({ ...formData, match: e.target.value })}
                placeholder="e.g., India vs Australia, MI vs CSK, etc."
                className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-orange-500 focus:outline-none placeholder-gray-400"
              />
            </div>
          )}

          {/* Info Box */}
          <div className="p-4 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              💡 <strong>Tip:</strong> We cache sports data to save API costs. If data is cached, you'll get instant results!
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] shadow-lg"
          >
            Get Sports Info 🏆
          </button>
        </form>
      </div>
    </div>
  );
}
