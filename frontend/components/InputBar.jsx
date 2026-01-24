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
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-2 sm:p-4">
      <div className="max-w-4xl mx-auto flex gap-1 sm:gap-3 items-end">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="btn-icon flex-shrink-0 hidden sm:flex"
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
          className={`btn-icon flex-shrink-0 transition-colors ${webSearchEnabled ? 'bg-blue-500 text-white hover:bg-blue-600' : 'text-gray-600 hover:text-gray-900 dark:text-gray-400'}`}
          disabled={loading}
          title={webSearchEnabled ? "Web search ON" : "Web search OFF (Auto for latest/news)"}
        >
          <Globe size={18} className="sm:w-5 sm:h-5" />
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Message MyDost..."
          rows={1}
          disabled={loading}
          className="flex-1 resize-none max-h-32 p-2 sm:p-3 text-sm sm:text-base border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:opacity-50"
          style={{ minHeight: '40px' }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary flex-shrink-0 flex items-center justify-center px-3 sm:px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="animate-spin">⏳</div>
          ) : (
            <Send size={18} className="sm:w-5 sm:h-5" />
          )}
        </button>
      </div>
    </form>
  );
}
