import React, { useState, useRef } from 'react';
import { Send, Paperclip, Globe } from 'lucide-react';

export default function InputBar({ onSend, loading, onFileSelect }) {
  const [input, setInput] = useState('');
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input, webSearchEnabled);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-3 sm:p-4 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-2 items-end bg-gray-50 dark:bg-gray-800 rounded-2xl p-2 border-2 border-gray-200 dark:border-gray-700 focus-within:border-cyan-500 dark:focus-within:border-cyan-500 transition-colors">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="btn-icon flex-shrink-0 hidden sm:flex p-2 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700"
            disabled={loading}
            title="Attach file (image, PDF)"
          >
            <Paperclip size={20} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            className="hidden"
            accept="image/*,.pdf"
          />
          <button
            type="button"
            onClick={() => setWebSearchEnabled(!webSearchEnabled)}
            className={`btn-icon flex-shrink-0 p-2 rounded-xl transition-all ${webSearchEnabled ? 'bg-blue-500 text-white shadow-md' : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'}`}
            disabled={loading}
            title={webSearchEnabled ? "🌐 Web search ON" : "🌐 Web search (Auto for news)"}
          >
            <Globe size={18} className="sm:w-5 sm:h-5" />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            rows={1}
            disabled={loading}
            className="flex-1 resize-none max-h-32 p-2 text-sm sm:text-base bg-transparent border-0 focus:outline-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
            style={{ minHeight: '40px' }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex-shrink-0 flex items-center justify-center px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
          >
            {loading ? (
              <div className="animate-spin">⏳</div>
            ) : (
              <Send size={18} className="sm:w-5 sm:h-5" />
            )}
          </button>
        </div>
        {webSearchEnabled && (
          <div className="mt-2 text-xs text-center text-blue-600 dark:text-blue-400 flex items-center justify-center gap-1">
            <Globe size={12} />
            <span>Web search enabled - Getting latest information</span>
          </div>
        )}
      </div>
    </form>
  );
}
