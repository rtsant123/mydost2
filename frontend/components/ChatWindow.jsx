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
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[minmax(0,_3fr)_minmax(260px,_1fr)] gap-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4 py-8 rounded-2xl border border-slate-200 bg-white shadow-sm w-full">
              <div className="mb-4 flex flex-col items-center gap-2">
                <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center">
                  <span className="text-2xl">🤖</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-semibold text-slate-900">MyDost</h2>
                <p className="text-slate-500 text-sm sm:text-base">Ask anything. I’ll keep context when you’re signed in.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xl mx-auto my-4">
                <button
                  onClick={() => router.push('/education')}
                  className="group p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition"
                >
                  <div className="flex items-center justify-between text-slate-700">
                    <span className="text-2xl">📚</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-200 text-slate-700">Study</span>
                  </div>
                  <h3 className="font-semibold text-slate-900 mt-3">Education</h3>
                  <p className="text-xs text-slate-600">Multilingual explainers & notes</p>
                </button>

                <button
                  onClick={() => router.push('/sports')}
                  className="group p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition"
                >
                  <div className="flex items-center justify-between text-slate-700">
                    <span className="text-2xl">🏏</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-200 text-slate-700">Sports</span>
                  </div>
                  <h3 className="font-semibold text-slate-900 mt-3">Sports</h3>
                  <p className="text-xs text-slate-600">Cricket & football insights</p>
                </button>

                <button
                  onClick={() => router.push('/horoscope')}
                  className="group p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition"
                >
                  <div className="flex items-center justify-between text-slate-700">
                    <span className="text-2xl">✨</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-200 text-slate-700">Daily</span>
                  </div>
                  <h3 className="font-semibold text-slate-900 mt-3">Horoscope</h3>
                  <p className="text-xs text-slate-600">Personalized astrology</p>
                </button>

                <button
                  onClick={() => setShowMoreModal(true)}
                  className="group p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition"
                >
                  <div className="flex items-center justify-between text-slate-700">
                    <span className="text-2xl">🛠️</span>
                    <span className="text-[11px] px-2 py-1 rounded-full bg-slate-200 text-slate-700">Tools</span>
                  </div>
                  <h3 className="font-semibold text-slate-900 mt-3">More tools</h3>
                  <p className="text-xs text-slate-600">PDF, OCR, notes & more</p>
                </button>
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
            {/* Follow-up chips */}
            {!loading && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
              <div className="mt-2 mb-4 flex flex-wrap gap-2">
                {[
                  "Summarize that in 2 lines",
                  "List key takeaways with sources",
                  "What should I ask next?",
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage && onSendMessage(suggestion, false)}
                    className="px-3 py-2 text-xs sm:text-sm rounded-full border border-slate-200 bg-white hover:border-slate-300 transition"
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

      {/* Sources rail */}
      <div className="hidden lg:block">
        <div className="sticky top-4 bg-white border border-slate-200 rounded-xl shadow-sm p-4 min-h-[200px]">
          <h3 className="text-sm font-semibold text-slate-800 mb-3">Sources</h3>
          {messages.length === 0 && (
            <p className="text-xs text-slate-500">Ask something to see sources.</p>
          )}
          {messages.length > 0 && (() => {
            const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant' && m.sources && m.sources.length);
            if (!lastAssistant) return <p className="text-xs text-slate-500">No sources for last reply.</p>;
            return (
              <div className="space-y-2">
                {lastAssistant.sources.map((src, idx) => (
                  <a
                    key={idx}
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block border border-slate-200 rounded-lg px-3 py-2 hover:border-slate-300"
                  >
                    <div className="text-[11px] text-slate-500 mb-1">[{src.number || idx + 1}] {src.source || 'source'}</div>
                    <div className="text-sm text-slate-800 line-clamp-2">{src.title}</div>
                  </a>
                ))}
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
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
