import React, { useState } from 'react';
import { X } from 'lucide-react';

export default function AstrologyModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    dateOfBirth: '',
    timeOfBirth: '',
    placeOfBirth: '',
    queryType: 'daily' // daily, monthly, yearly, specific
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Build astrology query
    let query = `I want my astrology reading. `;
    query += `My name is ${formData.name}. `;
    query += `I was born on ${formData.dateOfBirth}`;
    if (formData.timeOfBirth) {
      query += ` at ${formData.timeOfBirth}`;
    }
    if (formData.placeOfBirth) {
      query += ` in ${formData.placeOfBirth}`;
    }
    query += `. `;
    
    if (formData.queryType === 'daily') {
      query += `What's my horoscope for today?`;
    } else if (formData.queryType === 'monthly') {
      query += `What's my horoscope for this month?`;
    } else if (formData.queryType === 'yearly') {
      query += `What's my horoscope for this year?`;
    }
    
    onSubmit(query);
    onClose();
    
    // Reset form
    setFormData({
      name: '',
      dateOfBirth: '',
      timeOfBirth: '',
      placeOfBirth: '',
      queryType: 'daily'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 relative shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X size={24} />
        </button>

        {/* Header */}
        <div className="mb-6">
          <div className="text-4xl mb-3">✨</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Astrology Reading
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Tell me about yourself for a personalized prediction
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Your name"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Date of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Date of Birth *
            </label>
            <input
              type="date"
              required
              value={formData.dateOfBirth}
              onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Time of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Time of Birth (Optional)
            </label>
            <input
              type="time"
              value={formData.timeOfBirth}
              onChange={(e) => setFormData({ ...formData, timeOfBirth: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Place of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Place of Birth (Optional)
            </label>
            <input
              type="text"
              value={formData.placeOfBirth}
              onChange={(e) => setFormData({ ...formData, placeOfBirth: e.target.value })}
              placeholder="City, Country"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Query Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              What would you like to know?
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['daily', 'monthly', 'yearly', 'specific'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFormData({ ...formData, queryType: type })}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    formData.queryType === type
                      ? 'bg-purple-500 text-white shadow-md'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg hover:shadow-xl"
          >
            Get My Reading ✨
          </button>
        </form>
      </div>
    </div>
  );
}
