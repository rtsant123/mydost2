import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Menu, Trophy, TrendingUp } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import Sidebar from '@/components/Sidebar';
import { chatAPI } from '@/utils/apiClient';

export default function SportsPage() {
  const router = useRouter();
  const [userId, setUserId] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  useEffect(() => {
    const guestId = localStorage.getItem('guest_id') || `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('guest_id', guestId);
    setUserId(guestId);
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
        include_web_search: webSearchEnabled || true,
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
    <div className="h-screen flex bg-white dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        onNewChat={handleNewChat}
        onSelectConversation={() => {}}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-800 bg-gradient-to-r from-orange-500 to-red-500 p-3 sm:p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-white"
            >
              <Menu size={24} />
            </button>
            <Trophy className="text-white" size={28} />
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-white">Sports Predictions</h1>
              <p className="text-xs sm:text-sm text-orange-100 hidden sm:block">Cricket & Football Analysis</p>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="text-xs sm:text-sm bg-white text-orange-600 px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg font-medium hover:bg-orange-50 transition"
          >
            Home
          </button>
        </div>

        {/* Suggestion Chips (shown when no messages) */}
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
            <div className="max-w-3xl w-full">
              <div className="text-center mb-6 sm:mb-8">
                <Trophy className="mx-auto text-orange-500 mb-4" size={64} />
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  What sport prediction are you looking for?
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                  Choose from suggestions below or ask your own question
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(suggestion.query, true)}
                    className="text-left p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-orange-500 hover:bg-orange-50 dark:hover:bg-orange-900/10 transition-all group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl sm:text-3xl flex-shrink-0">{suggestion.icon}</span>
                      <div>
                        <p className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white group-hover:text-orange-600">
                          {suggestion.text}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 text-center">
                  <span className="font-semibold">✨ Smart Predictions:</span> Cached from expert sources
                </p>
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
          onSend={(msg) => handleSendMessage(msg, true)}
          loading={loading}
          placeholder="Ask about any sport prediction, stats, or analysis..."
        />
      </div>
    </div>
  );
}
