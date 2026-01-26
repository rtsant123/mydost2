import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { GraduationCap, BookOpen, Brain, HelpCircle, ArrowLeft } from 'lucide-react';

export default function EducationPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    class: '',
    subject: '',
    topic: '',
    helpType: 'homework',
    language: 'hinglish'
  });
  const [loading, setLoading] = useState(false);

  const languages = [
    { value: 'english', label: '🇬🇧 English', name: 'English' },
    { value: 'hinglish', label: '🇮🇳 Hinglish', name: 'Hindi + English' },
    { value: 'hindi', label: '🇮🇳 हिंदी', name: 'Hindi' },
    { value: 'assamese', label: '🇮🇳 অসমীয়া', name: 'Assamese' }
  ];

  const classes = [
    '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', 'College', 'Other'
  ];

  const subjects = [
    'Mathematics', 'Science', 'Physics', 'Chemistry', 'Biology',
    'English', 'Hindi', 'Assamese', 'History', 'Geography',
    'Economics', 'Computer Science', 'Accounts', 'Other'
  ];

  const helpTypes = [
    { value: 'homework', label: 'Homework Help', icon: BookOpen, desc: 'Get help with assignments' },
    { value: 'concept', label: 'Concept Learning', icon: Brain, desc: 'Understand topics clearly' },
    { value: 'exam', label: 'Exam Preparation', icon: GraduationCap, desc: 'Practice & preparation' },
    { value: 'doubt', label: 'Doubt Solving', icon: HelpCircle, desc: 'Clear your doubts' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    // Detect young student
    const classNum = parseInt(formData.class);
    const isYoungStudent = !isNaN(classNum) && classNum <= 5;
    
    // Build query
    let query = `🎓 EDUCATION REQUEST\n`;
    query += `Language: ${formData.language}\n`;
    
    if (isYoungStudent) {
      query += `IMPORTANT: Student is in class ${formData.class} (young learner). Use VERY SIMPLE language, short sentences, examples, and emojis. Explain like talking to a child.\n\n`;
    }
    
    query += `I need help with ${formData.subject || 'my studies'}`;
    if (formData.class) query += ` for class ${formData.class}`;
    if (formData.topic) query += `. Topic: ${formData.topic}`;
    
    const helpTypeLabel = helpTypes.find(h => h.value === formData.helpType)?.label || '';
    query += `. ${helpTypeLabel}`;
    
    if (formData.language === 'hinglish') {
      query += `\nPlease explain in Hinglish (mix Hindi and English words).`;
    } else if (formData.language === 'hindi') {
      query += `\nकृपया हिंदी में समझाएं।`;
    } else if (formData.language === 'assamese') {
      query += `\nঅসমীয়া ভাষাত ব্যাখ্যা কৰক।`;
    }

    // Navigate to chat - hide technical query from user
    router.push({
      pathname: '/',
      query: { message: query, hideQuery: 'true' }
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 mb-4 text-blue-100 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Back to Home</span>
          </button>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <GraduationCap size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Education Help</h1>
              <p className="text-blue-100 mt-1">Multi-language support: English, Hinglish, Hindi, Assamese</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-6">
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 space-y-6">
          {/* Language Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              📢 In which language do you want help? *
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {languages.map((lang) => (
                <button
                  key={lang.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, language: lang.value })}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    formData.language === lang.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                      : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{lang.label.split(' ')[0]}</div>
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {lang.name}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Help Type */}
          <div>
            <label className="block text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              What do you need? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {helpTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, helpType: type.value })}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      formData.helpType === type.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                        : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                    }`}
                  >
                    <Icon size={24} className={`mb-2 ${formData.helpType === type.value ? 'text-blue-600' : 'text-gray-600'}`} />
                    <div className="font-bold text-gray-900 dark:text-gray-100">{type.label}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{type.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Class Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Class *
            </label>
            <select
              value={formData.class}
              onChange={(e) => setFormData({ ...formData, class: e.target.value })}
              required
              className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-blue-500 focus:outline-none dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="">Select your class</option>
              {classes.map((cls) => (
                <option key={cls} value={cls}>{cls}</option>
              ))}
            </select>
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Subject *
            </label>
            <select
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              required
              className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-blue-500 focus:outline-none dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="">Select subject</option>
              {subjects.map((subject) => (
                <option key={subject} value={subject}>{subject}</option>
              ))}
            </select>
          </div>

          {/* Topic */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Topic or Question
            </label>
            <textarea
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              placeholder="e.g., Explain photosynthesis in simple words"
              rows={3}
              className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:border-blue-500 focus:outline-none dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !formData.class || !formData.subject}
            className="w-full py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-cyan-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : '📚 Get Help Now'}
          </button>

          {/* Info Box */}
          <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-200 dark:border-green-800">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold">✨ Smart Learning:</span> For Class 1-5 students, explanations are automatically simplified with easy words and emojis!
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
