import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ messages, loading, onSendMessage, onAstrologyClick }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4">
              <div className="mb-6">
                <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-3xl sm:text-4xl">🤖</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent mb-2">
                  MyDost
                </h2>
                <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                  Your Smart AI Study Companion
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-md mx-auto">
                <button onClick={() => onSendMessage && onSendMessage("Help me with my studies")} className="group p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-cyan-500 dark:hover:border-cyan-500 transition-all hover:shadow-lg hover:-translate-y-1">
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">📚</div>
                  <h3 className="font-semibold text-sm mb-1 text-gray-900 dark:text-gray-100">Education</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Study help & homework</p>
                </button>
                
                <button onClick={() => onAstrologyClick && onAstrologyClick()} className="group p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-500 dark:hover:border-purple-500 transition-all hover:shadow-lg hover:-translate-y-1">
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">✨</div>
                  <h3 className="font-semibold text-sm mb-1 text-gray-900 dark:text-gray-100">Astrology</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Horoscope & predictions</p>
                </button>
                
                <button onClick={() => onSendMessage && onSendMessage("Take notes for my class")} className="group p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all hover:shadow-lg hover:-translate-y-1">
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">📝</div>
                  <h3 className="font-semibold text-sm mb-1 text-gray-900 dark:text-gray-100">Notes</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Smart note taking</p>
                </button>
                
                <button onClick={() => onSendMessage && onSendMessage("Show me more options")} className="group p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-pink-500 dark:hover:border-pink-500 transition-all hover:shadow-lg hover:-translate-y-1">
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">🔮</div>
                  <h3 className="font-semibold text-sm mb-1 text-gray-900 dark:text-gray-100">More</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Teer, sports, news & more</p>
                </button>
              </div>
              
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-6">
                💡 Just start typing - I'll understand what you need!
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <MessageBubble
                key={idx}
                message={msg.content}
                isUser={msg.role === 'user'}
                sources={msg.sources}
              />
            ))}
            {loading && (
              <div className="message-bubble message-assistant">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
