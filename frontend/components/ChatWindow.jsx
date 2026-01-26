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
    <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-gradient-to-b from-[#f5f6f8] via-[#eef1f5] to-[#f5f6f8] text-slate-900">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4 py-8 rounded-3xl border border-slate-800/70 bg-[#14171f] backdrop-blur shadow-2xl">
              <div className="mb-6 flex flex-col items-center gap-3">
                <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-slate-600 to-slate-400 rounded-2xl flex items-center justify-center shadow-lg shadow-slate-800/30">
                  <span className="text-3xl sm:text-4xl">🤖</span>
                </div>
                <div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-50">MyDost</h2>
                  <p className="text-slate-400 text-sm sm:text-base">Friendly AI that remembers you.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xl mx-auto">
                <button
                  onClick={() => router.push('/education')}
                  className="group p-4 rounded-2xl bg-[#171b24] border border-slate-800 hover:border-slate-500 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">📚</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-700 text-slate-200">Study</span>
                  </div>
                  <h3 className="font-semibold text-slate-50 mt-3">Education</h3>
                  <p className="text-xs text-slate-400">Multilingual explainers & notes</p>
                </button>

                <button
                  onClick={() => router.push('/sports')}
                  className="group p-4 rounded-2xl bg-[#171b24] border border-slate-800 hover:border-slate-500 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">🏏</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-700 text-slate-200">Sports</span>
                  </div>
                  <h3 className="font-semibold text-slate-50 mt-3">Sports</h3>
                  <p className="text-xs text-slate-400">Cricket & football insights</p>
                </button>

                <button
                  onClick={() => router.push('/horoscope')}
                  className="group p-4 rounded-2xl bg-[#171b24] border border-slate-800 hover:border-slate-500 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">✨</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-700 text-slate-200">Daily</span>
                  </div>
                  <h3 className="font-semibold text-slate-50 mt-3">Horoscope</h3>
                  <p className="text-xs text-slate-400">Personalized astrology</p>
                </button>

                <button
                  onClick={() => setShowMoreModal(true)}
                  className="group p-4 rounded-2xl bg-[#171b24] border border-slate-800 hover:border-slate-500 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">🛠️</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-700 text-slate-200">Tools</span>
                  </div>
                  <h3 className="font-semibold text-slate-50 mt-3">More tools</h3>
                  <p className="text-xs text-slate-400">PDF, OCR, notes & more</p>
                </button>
              </div>

              <p className="text-xs text-slate-500 mt-6">💡 Ask in English, Hindi, or Hinglish. Memory stays with you.</p>
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
                <div className="max-w-3xl w-fit rounded-2xl px-4 sm:px-5 py-4 bg-white/10 backdrop-blur border border-slate-800 shadow-lg">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-slate-300 mb-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    MyDost is thinking
                  </div>
                  <div className="space-y-2">
                    <div className="h-3 rounded bg-white/15 animate-pulse" />
                    <div className="h-3 rounded bg-white/10 animate-pulse w-5/6" />
                  </div>
                </div>
              </div>
            )}
            {/* Suggestions after latest assistant message */}
            {!loading && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
              <div className="mt-2 mb-6 flex flex-wrap gap-2">
                {[
                  "Summarize that in 2 lines",
                  "List key takeaways with sources",
                  "What should I ask next?",
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage && onSendMessage(suggestion, false)}
                    className="px-3 py-2 text-xs sm:text-sm rounded-full border border-slate-700 bg-[#14171f] hover:border-slate-500 hover:bg-[#1a1d26] transition"
                  >
                    {suggestion}
                  </button>
                ))}
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
