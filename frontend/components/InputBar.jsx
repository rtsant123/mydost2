import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Globe, Search } from 'lucide-react';
import apiClient from '../utils/apiClient';

export default function InputBar({ onSend, loading, onFileSelect }) {
  const [input, setInput] = useState('');
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (input.trim().length < 1) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      try {
        const response = await apiClient.get(`/api/autocomplete?q=${encodeURIComponent(input)}`);
        setSuggestions(response.data.suggestions || []);
        setShowSuggestions(true);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        setSuggestions([]);
        setShowSuggestions(false);
      }
    };

    const debounce = setTimeout(fetchSuggestions, 150);
    return () => clearTimeout(debounce);
  }, [input]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input, webSearchEnabled);
      setInput('');
      setSuggestions([]);
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        setInput(suggestions[selectedIndex]);
        setShowSuggestions(false);
        setSelectedIndex(-1);
      } else {
        handleSubmit(e);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    setShowSuggestions(false);
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="sticky bottom-0 z-30 border-t border-slate-200 bg-slate-50/95 backdrop-blur px-3 sm:px-4 pt-3 pb-4"
    >
      <div className="max-w-4xl mx-auto w-full relative">
        {showSuggestions && suggestions.length > 0 && (
          <div
            ref={suggestionsRef}
            className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-slate-200 rounded-2xl shadow-lg overflow-hidden z-50"
          >
            <div className="max-h-80 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={`px-4 py-3 cursor-pointer flex items-center gap-3 transition-colors ${
                    index === selectedIndex ? 'bg-slate-100 text-slate-900' : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <Search size={16} className="text-slate-400 flex-shrink-0" />
                  <span className="text-sm">{suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2 items-end bg-white rounded-2xl px-3 sm:px-4 py-2 sm:py-3 border border-slate-200 shadow-sm focus-within:border-slate-400 transition-colors">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="hidden sm:flex p-2 rounded-xl hover:bg-slate-100 text-slate-700 focus:outline-none"
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
            className={`flex-shrink-0 p-2 rounded-xl transition-colors ${
              webSearchEnabled ? 'bg-slate-900 text-white' : 'hover:bg-slate-100 text-slate-700'
            }`}
            disabled={loading}
            title={webSearchEnabled ? 'Web search on' : 'Web search (auto for news)'}
          >
            <Globe size={18} className="sm:w-5 sm:h-5" />
          </button>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask anything... Shift+Enter for a new line"
            rows={1}
            disabled={loading}
            className="flex-1 resize-none max-h-40 px-2 py-2 text-base bg-transparent border-0 focus:outline-none text-slate-900 placeholder-slate-500 leading-6"
            style={{ minHeight: '40px' }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex-shrink-0 flex items-center justify-center w-10 h-10 sm:w-11 sm:h-11 bg-slate-900 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:bg-slate-800"
          >
            {loading ? (
              <span className="relative flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-60" />
                <span className="relative inline-flex rounded-full h-4 w-4 bg-white" />
              </span>
            ) : (
              <Send size={18} className="sm:w-5 sm:h-5" />
            )}
          </button>
        </div>
        <div className="flex justify-between text-[11px] text-slate-500 mt-2 px-1">
          <span>Shift + Enter for line break</span>
          {webSearchEnabled && (
            <span className="inline-flex items-center gap-1 text-slate-700">
              <Globe size={12} />
              Web search on
            </span>
          )}
        </div>
      </div>
    </form>
  );
}
