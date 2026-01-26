import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Menu, Sparkles, Star } from 'lucide-react';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import Sidebar from '@/components/Sidebar';
import { chatAPI } from '@/utils/apiClient';

export default function HoroscopePage() {
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
    
    const conversationId = currentConversationId || `horoscope_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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
        include_web_search: false,
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
    { icon: '♈', text: 'Aries daily horoscope', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Aries ♈\nType: daily\n\nGive me today\'s horoscope for Aries. Include predictions for love, career, health, and lucky numbers.' },
    { icon: '♉', text: 'Taurus weekly forecast', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Taurus ♉\nType: weekly\n\nProvide this week\'s horoscope for Taurus. Include major themes, opportunities, and challenges.' },
    { icon: '♊', text: 'Gemini love & relationships', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Gemini ♊\nType: love\n\nTell me about love and relationship prospects for Gemini. Include dating advice and relationship insights.' },
    { icon: '♋', text: 'Cancer monthly overview', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Cancer ♋\nType: monthly\n\nGive me this month\'s detailed horoscope for Cancer. Cover career, love, health, and finances.' },
    { icon: '♌', text: 'Leo compatibility check', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Leo ♌\nType: compatibility\n\nAnalyze compatibility for Leo with other zodiac signs. Include love compatibility and relationship advice.' },
    { icon: '♍', text: 'Virgo career forecast', query: '✨ HOROSCOPE REQUEST\nZodiac Sign: Virgo ♍\nType: daily\n\nGive me career and professional predictions for Virgo today.' }
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
        <div className="border-b border-gray-200 dark:border-gray-800 bg-gradient-to-r from-purple-500 to-pink-500 p-3 sm:p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-white"
            >
              <Menu size={24} />
            </button>
            <Sparkles className="text-white" size={28} />
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-white">Horoscope & Astrology</h1>
              <p className="text-xs sm:text-sm text-purple-100 hidden sm:block">Daily predictions & cosmic insights</p>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="text-xs sm:text-sm bg-white text-purple-600 px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg font-medium hover:bg-purple-50 transition"
          >
            Home
          </button>
        </div>

        {/* Suggestion Chips (shown when no messages) */}
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
            <div className="max-w-3xl w-full">
              <div className="text-center mb-6 sm:mb-8">
                <Sparkles className="mx-auto text-purple-500 mb-4" size={64} />
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  What cosmic insights do you seek?
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                  Choose your zodiac sign and get personalized predictions
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(suggestion.query)}
                    className="text-left p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/10 transition-all group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl sm:text-3xl flex-shrink-0">{suggestion.icon}</span>
                      <div>
                        <p className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white group-hover:text-purple-600">
                          {suggestion.text}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl border border-yellow-200 dark:border-yellow-800">
                <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 text-center">
                  <span className="font-semibold">🌟 Cosmic Insights:</span> Traditional astrology with modern AI analysis
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
          onSend={handleSendMessage}
          loading={loading}
          placeholder="Ask about your horoscope, zodiac sign, or astrology..."
        />
      </div>
    </div>
  );
}
