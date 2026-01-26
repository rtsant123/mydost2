import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Menu, Trophy, TrendingUp } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import LayoutShell from '@/components/LayoutShell';
import { chatAPI } from '@/utils/apiClient';
import axios from 'axios';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mydost2-production.up.railway.app';

export default function SportsPage() {
  const router = useRouter();
  const [userId, setUserId] = useState('');
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  // Auth check (reuse token if logged in)
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        const guestId = localStorage.getItem('guest_id') || `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('guest_id', guestId);
        setUserId(guestId);
        setUser(null);
        return;
      }
      try {
        const resp = await axios.get(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(resp.data.user);
        setUserId(resp.data.user.user_id);
      } catch (e) {
        console.error('Auth failed on sports page:', e);
        localStorage.removeItem('token');
        const guestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('guest_id', guestId);
        setUserId(guestId);
        setUser(null);
      }
    };
    checkAuth();
  }, []);

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(null);
  };

  const handleSendMessage = async (message, webSearchEnabled = false) => {
    if (!message || !message.trim()) return;
    
    const conversationId = currentConversationId || `sports_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    if (!currentConversationId) {
      setCurrentConversationId(conversationId);
    }

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatAPI.send({
        user_id: userId,
        message,
        conversation_id: conversationId,
        include_web_search: webSearchEnabled,
        language: 'english'
      });

      const assistantMessage = { 
        role: 'assistant', 
        content: response.data.response 
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Sorry, something went wrong. Please try again!' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    { icon: '🏏', text: 'India vs Australia prediction', query: 'Give me a detailed prediction for India vs Australia cricket match with current form, player stats, and win probability' },
    { icon: '⚽', text: 'Premier League predictions', query: 'Show me predictions and analysis for upcoming Premier League matches' },
    { icon: '📊', text: 'Virat Kohli stats', query: 'Get me comprehensive statistics and recent performance of Virat Kohli' },
    { icon: '🏆', text: 'IPL 2026 analysis', query: 'Analyze IPL 2026 teams, predictions, and key players to watch' },
    { icon: '⚖️', text: 'Messi vs Ronaldo', query: 'Compare Lionel Messi and Cristiano Ronaldo career stats and achievements' },
    { icon: '📅', text: 'Upcoming matches', query: 'Show me upcoming important cricket and football matches this week' }
  ];

  return (
    <LayoutShell
      sidebarProps={{
        isOpen: sidebarOpen,
        onClose: () => setSidebarOpen(false),
        conversations,
        onNewChat: handleNewChat,
        onSelectConversation: () => {},
        user,
      }}
    >
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-[#0f1115]">
        {/* Header */}
        <div className="border-b border-slate-800 bg-[#0f1115] p-3 sm:p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-slate-200"
            >
              <Menu size={24} />
            </button>
            <Trophy className="text-slate-200" size={28} />
            <div>
              <h1 className="text-xl sm:text-2xl font-semibold text-slate-100">Sports Predictions</h1>
              <p className="text-xs sm:text-sm text-slate-400 hidden sm:block">Cricket & Football Analysis</p>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="text-xs sm:text-sm bg-slate-100 text-slate-900 px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg font-medium hover:bg-white transition"
          >
            Home
          </button>
        </div>

        {/* Suggestion Chips (shown when no messages) */}
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
            <div className="max-w-3xl w-full">
              <div className="text-center mb-6 sm:mb-8">
                <Trophy className="mx-auto text-gray-700 dark:text-gray-300 mb-4" size={48} />
                <h2 className="text-2xl sm:text-3xl font-semibold text-gray-900 dark:text-white mb-2">
                  Sports Predictions
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                  Ask me anything about sports
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(suggestion.query, true)}
                    className="text-left p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl flex-shrink-0">{suggestion.icon}</span>
                      <div>
                        <p className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">
                          {suggestion.text}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <ChatWindow 
            messages={messages} 
            loading={loading} 
            onSendMessage={handleSendMessage}
            onNewChat={handleNewChat}
          />
        )}

        {/* Input Bar - Always visible */}
        <InputBar
          onSend={(msg, web) => handleSendMessage(msg, web ?? true)}
          loading={loading}
          placeholder="Ask about any sport prediction, stats, or analysis..."
        />
      </div>
    </LayoutShell>
  );
}
