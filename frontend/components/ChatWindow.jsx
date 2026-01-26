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
    <div className="flex-1 overflow-y-auto p-3 sm:p-4 bg-[#0c162a] bg-[radial-gradient(circle_at_20%_20%,rgba(37,99,235,0.15),transparent_25%),radial-gradient(circle_at_80%_0%,rgba(14,165,233,0.12),transparent_23%),linear-gradient(180deg,#0c162a,#0b1220)] text-slate-50">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4 py-8 rounded-3xl border border-slate-800 bg-white/5 backdrop-blur shadow-2xl">
              <div className="mb-6 flex flex-col items-center gap-3">
                <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/30">
                  <span className="text-3xl sm:text-4xl">🤖</span>
                </div>
                <div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white">MyDost</h2>
                  <p className="text-slate-300 text-sm sm:text-base">Friendly AI that remembers you.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xl mx-auto">
                <button
                  onClick={() => router.push('/education')}
                  className="group p-4 rounded-2xl bg-white/5 border border-slate-800 hover:border-cyan-400 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">📚</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-cyan-500/15 text-cyan-200">Study boost</span>
                  </div>
                  <h3 className="font-semibold text-white mt-3">Education</h3>
                  <p className="text-xs text-slate-300">Multilingual explainers & notes</p>
                </button>

                <button
                  onClick={() => router.push('/sports')}
                  className="group p-4 rounded-2xl bg-white/5 border border-slate-800 hover:border-orange-400 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">🏏</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-orange-500/15 text-orange-200">Live edge</span>
                  </div>
                  <h3 className="font-semibold text-white mt-3">Sports</h3>
                  <p className="text-xs text-slate-300">Cricket & football insights</p>
                </button>

                <button
                  onClick={() => router.push('/horoscope')}
                  className="group p-4 rounded-2xl bg-white/5 border border-slate-800 hover:border-emerald-400 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">✨</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-200">Daily calm</span>
                  </div>
                  <h3 className="font-semibold text-white mt-3">Horoscope</h3>
                  <p className="text-xs text-slate-300">Personalized astrology</p>
                </button>

                <button
                  onClick={() => setShowMoreModal(true)}
                  className="group p-4 rounded-2xl bg-white/5 border border-slate-800 hover:border-pink-400 transition-all hover:-translate-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">🛠️</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-pink-500/15 text-pink-200">Utilities</span>
                  </div>
                  <h3 className="font-semibold text-white mt-3">More tools</h3>
                  <p className="text-xs text-slate-300">PDF, OCR, notes & more</p>
                </button>
              </div>

              <p className="text-xs text-slate-400 mt-6">💡 Ask in English, Hindi, or Hinglish. Memory stays with you.</p>
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
