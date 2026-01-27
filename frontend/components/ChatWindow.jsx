import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import MessageBubble from './MessageBubble';
import EducationModal from './EducationModal';
import MoreDomainsModal from './MoreDomainsModal';
import SportsModal from './SportsModal';

export default function ChatWindow({ messages, loading, onSendMessage, onAstrologyClick, onNewChat }) {
  const router = useRouter();
  const [showEducationModal, setShowEducationModal] = useState(false);
  const [showMoreModal, setShowMoreModal] = useState(false);
  const [showSportsModal, setShowSportsModal] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Handler for domain cards that creates new chat if messages exist
  const handleCardClick = (message) => {
    if (messages.length > 0 && onNewChat) {
      // Start new chat if conversation exists
      onNewChat();
      // Wait a moment for state to clear
      setTimeout(() => onSendMessage && onSendMessage(message), 100);
    } else {
      // Send message directly if no conversation
      onSendMessage && onSendMessage(message);
    }
  };

  const handleEducationSubmit = (query) => {
    if (messages.length > 0 && onNewChat) {
      onNewChat();
      setTimeout(() => onSendMessage && onSendMessage(query), 100);
    } else {
      onSendMessage && onSendMessage(query);
    }
  };

  const handleMoreDomainSelect = (query) => {
    if (messages.length > 0 && onNewChat) {
      onNewChat();
      setTimeout(() => onSendMessage && onSendMessage(query), 100);
    } else {
      onSendMessage && onSendMessage(query);
    }
  };

  const handleSportsSubmit = (query, enableWebSearch = true) => {
    if (messages.length > 0 && onNewChat) {
      onNewChat();
      setTimeout(() => onSendMessage && onSendMessage(query, enableWebSearch), 100);
    } else {
      onSendMessage && onSendMessage(query, enableWebSearch);
    }
    setShowSportsModal(false);
  };

  return (
    <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-slate-100 text-slate-900">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4 py-8 rounded-2xl border border-slate-200 bg-white shadow-sm">
              <div className="mb-4 flex flex-col items-center gap-2">
                <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center">
                  <span className="text-2xl">🤖</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-semibold text-slate-900">MyDost</h2>
                <p className="text-slate-500 text-sm sm:text-base">Ask anything. I’ll keep context when you’re signed in.</p>
              </div>
              <div className="space-y-2 text-sm text-slate-600">
                <p>Try: “Summarize my last chat”, “Plan a 3-day trip to NYC”, or “Explain quantum computing simply”.</p>
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
              <div className="flex justify-start mb-5">
                <div className="max-w-3xl w-fit rounded-2xl px-4 sm:px-5 py-3 bg-white border border-slate-200 shadow-sm">
                  <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                    <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
                    MyDost is thinking…
                  </div>
                  <div className="space-y-2">
                    <div className="h-3 rounded bg-slate-200 animate-pulse" />
                    <div className="h-3 rounded bg-slate-200 animate-pulse w-5/6" />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={endRef} />
      </div>

      {/* Modals */}
      <EducationModal
        isOpen={showEducationModal}
        onClose={() => setShowEducationModal(false)}
        onSubmit={handleEducationSubmit}
      />
      <SportsModal
        isOpen={showSportsModal}
        onClose={() => setShowSportsModal(false)}
        onSubmit={handleSportsSubmit}
      />
      <MoreDomainsModal
        isOpen={showMoreModal}
        onClose={() => setShowMoreModal(false)}
        onSelectDomain={handleMoreDomainSelect}
      />
    </div>
  );
}
