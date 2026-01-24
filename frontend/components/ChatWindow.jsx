import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ messages, loading }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-white dark:bg-gray-900">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-gray-200 mb-3 sm:mb-4">
                MyDost
              </h2>
              <p className="text-gray-600 dark:text-gray-400 text-base sm:text-lg mb-6 sm:mb-8">
                Your Multi-Domain AI Assistant
              </p>
              <div className="grid grid-cols-2 gap-3 sm:gap-4 text-left">
                <div className="p-3 sm:p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <h3 className="font-semibold text-sm sm:text-base mb-1 sm:mb-2">📚 Education</h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    Ask any subject
                  </p>
                </div>
                <div className="p-3 sm:p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <h3 className="font-semibold text-sm sm:text-base mb-1 sm:mb-2">⚽ Sports</h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    Match predictions
                  </p>
                </div>
                <div className="p-3 sm:p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <h3 className="font-semibold text-sm sm:text-base mb-1 sm:mb-2">🎯 Teer</h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    Teer analysis
                  </p>
                </div>
                <div className="p-3 sm:p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <h3 className="font-semibold text-sm sm:text-base mb-1 sm:mb-2">✨ More</h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    News & more
                  </p>
                </div>
              </div>
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
