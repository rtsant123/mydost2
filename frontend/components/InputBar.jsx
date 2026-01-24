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
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto flex gap-3">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="btn-icon"
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
          className={`btn-icon transition-colors ${webSearchEnabled ? 'bg-blue-500 text-white hover:bg-blue-600' : 'text-gray-600 hover:text-gray-900'}`}
          disabled={loading}
          title={webSearchEnabled ? "Web search ON - Latest info from web" : "Web search OFF - Auto-enabled for latest news"}
        >
          <Globe size={20} />
        </button>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Message MyDost... (Shift+Enter for new line)"
          rows={1}
          disabled={loading}
          className="flex-1 resize-none max-h-32 p-3 border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:opacity-50"
          style={{ minHeight: '44px' }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="animate-spin">⏳</div>
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>
    </form>
  );
}
