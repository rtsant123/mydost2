import React, { useState } from 'react';
import { X, BookOpen, GraduationCap, School } from 'lucide-react';

export default function EducationModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    class: '',
    board: '',
    subject: '',
    topic: '',
    helpType: 'homework',
    language: 'hinglish'
  });

  const classes = [
    '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', 'College', 'Other'
  ];

  const boards = [
    'CBSE', 'ICSE', 'State Board', 'IB', 'Cambridge', 'Other'
  ];

  const subjects = [
    'Mathematics', 'Science', 'Physics', 'Chemistry', 'Biology',
    'English', 'Hindi', 'History', 'Geography', 'Civics',
    'Economics', 'Computer Science', 'Accounts', 'Business Studies', 'Other'
  ];

  const helpTypes = [
    { value: 'homework', label: '📝 Homework Help', description: 'Get help with assignments' },
    { value: 'concept', label: '💡 Concept Learning', description: 'Understand topics clearly' },
    { value: 'exam', label: '📚 Exam Preparation', description: 'Practice & preparation' },
    { value: 'doubt', label: '❓ Doubt Solving', description: 'Clear your doubts' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Detect if young student (class 1-5)
    const classNum = parseInt(formData.class);
    const isYoungStudent = !isNaN(classNum) && classNum <= 5;
    
    // Build query with language and age-appropriate instructions
    let query = `🎓 EDUCATION REQUEST\n`;
    query += `Language: ${formData.language}\n`;
    if (isYoungStudent) {
      query += `IMPORTANT: Student is in class ${formData.class} (young learner). Use VERY SIMPLE language, short sentences, examples, and emojis. Explain like talking to a child.\n\n`;
    }
    
    query += `I need help with ${formData.subject || 'my studies'}`;
    if (formData.class) query += ` for class ${formData.class}`;
    if (formData.board) query += ` (${formData.board} board)`;
    if (formData.topic) query += `. Topic: ${formData.topic}`;
    
    const helpTypeLabel = helpTypes.find(h => h.value === formData.helpType)?.label || '';
    query += `. ${helpTypeLabel.replace(/[^\w\s]/gi, '')}`;
    
    if (formData.language === 'hinglish') {
      query += `\nPlease explain in Hinglish (mix Hindi and English words).`;
    } else if (formData.language === 'hindi') {
      query += `\nकृपया हिंदी में समझाएं।`;
    }

    onSubmit(query);
    onClose();
    
    // Reset form
    setFormData({
      class: '',
      board: '',
      subject: '',
      topic: '',
      helpType: 'homework'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-500 to-cyan-500 p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <GraduationCap size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Education Help</h2>
              <p className="text-blue-100 text-sm">Tell us what you need help with</p>
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
          {/* Language Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              📢 In which language do you want help? *
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'hinglish', label: '🇮🇳 Hinglish', desc: 'Hindi + English mix' },
                { value: 'hindi', label: '🇮🇳 Hindi', desc: 'हिंदी में' },
                { value: 'english', label: '🇬🇧 English', desc: 'Full English' }
              ].map((lang) => (
                <button
                  key={lang.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, language: lang.value })}
                  className={`p-3 rounded-xl border-2 transition-all ${
                    formData.language === lang.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-sm text-gray-900 dark:text-gray-100 mb-1">
                    {lang.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {lang.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Help Type Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              What do you need? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {helpTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, helpType: type.value })}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    formData.helpType === type.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
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

          {/* Class */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              <School size={16} className="inline mr-2" />
              Class/Grade *
            </label>
            <select
              value={formData.class}
              onChange={(e) => setFormData({ ...formData, class: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:outline-none"
              required
            >
              <option value="">Select your class</option>
              {classes.map((cls) => (
                <option key={cls} value={cls}>{cls}</option>
              ))}
            </select>
          </div>

          {/* Board */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Board
            </label>
            <select
              value={formData.board}
              onChange={(e) => setFormData({ ...formData, board: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:outline-none"
            >
              <option value="">Select board (optional)</option>
              {boards.map((board) => (
                <option key={board} value={board}>{board}</option>
              ))}
            </select>
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              <BookOpen size={16} className="inline mr-2" />
              Subject *
            </label>
            <select
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:outline-none"
              required
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
              Topic/Chapter (Optional)
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              placeholder="e.g., Quadratic Equations, Photosynthesis, etc."
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:border-blue-500 focus:outline-none placeholder-gray-400"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold rounded-xl transition-all transform hover:scale-[1.02] shadow-lg"
          >
            Start Learning 🚀
          </button>
        </form>
      </div>
    </div>
  );
}
