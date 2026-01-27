import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import MessageBubble from './MessageBubble';
import EducationModal from './EducationModal';
import MoreDomainsModal from './MoreDomainsModal';
import SportsModal from './SportsModal';

const ICONS = {
  robot: '\u{1F916}',
  book: '\u{1F4D6}',
  ball: '\u{1F3C0}',
  sparkles: '\u{2728}',
  toolbox: '\u{1F9F0}',
};

export default function ChatWindow({ messages, loading, onSendMessage, onAstrologyClick, onNewChat }) {
  const router = useRouter();
  const [showEducationModal, setShowEducationModal] = useState(false);
  const [showMoreModal, setShowMoreModal] = useState(false);
  const [showSportsModal, setShowSportsModal] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

  const lastAssistantWithSources = [...messages].reverse().find(
    (m) => m.role === 'assistant' && m.sources && m.sources.length
  );

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 min-h-screen p-3 sm:p-4 pb-28">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[minmax(0,_3fr)_minmax(260px,_1fr)] gap-3 sm:gap-4">
        <div>
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center px-4 py-8 rounded-2xl border border-slate-200 bg-white shadow-sm w-full max-w-3xl mx-auto">
                <div className="mb-4 flex flex-col items-center gap-2">
                  <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center">
                    <span className="text-2xl">{ICONS.robot}</span>
                  </div>
                  <h2 className="text-xl sm:text-2xl font-semibold text-slate-900">MyDost</h2>
                  <p className="text-slate-500 text-sm sm:text-base">Ask anything. I will keep context when you are signed in.</p>
                </div>
                <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xl mx-auto my-4">
                  <DomainCard icon={ICONS.book} label="Education" pill="Study" onClick={() => router.push('/education')} />
                  <DomainCard icon={ICONS.ball} label="Sports" pill="Sports" onClick={() => router.push('/sports')} />
                  <DomainCard icon={ICONS.sparkles} label="Horoscope" pill="Daily" onClick={() => router.push('/horoscope')} />
                  <DomainCard icon={ICONS.toolbox} label="More tools" pill="Tools" onClick={() => setShowMoreModal(true)} />
                </div>
                <div className="space-y-2 text-sm text-slate-600">
                  <p>
                    Try: &quot;Summarize my last chat&quot;, &quot;Plan a 3-day trip to NYC&quot;, or &quot;Explain
                    quantum computing simply&quot;.
                  </p>
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
                      MyDost is thinking...
                    </div>
                    <div className="space-y-2">
                      <div className="h-3 rounded bg-slate-200 animate-pulse" />
                      <div className="h-3 rounded bg-slate-200 animate-pulse w-5/6" />
                    </div>
                  </div>
                </div>
              )}
              {!loading && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
                <div className="mt-2 mb-4 flex flex-wrap gap-2">
                  {[
                    'Summarize that in 2 lines',
                    'List key takeaways with sources',
                    'What should I ask next?',
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

        {/* Sources rail desktop */}
        <div className="hidden lg:block">
          <SourcesPanel lastAssistant={lastAssistantWithSources} />
        </div>
      </div>

      {/* Sources mobile */}
      <div className="lg:hidden mt-2">
        <SourcesPanel lastAssistant={lastAssistantWithSources} collapsible />
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

function DomainCard({ icon, label, pill, onClick }) {
  return (
    <button
      onClick={onClick}
      className="group p-4 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 transition text-left"
    >
      <div className="flex items-center justify-between text-slate-700">
        <span className="text-2xl">{icon}</span>
        <span className="text-[11px] px-2 py-1 rounded-full bg-slate-200 text-slate-700">{pill}</span>
      </div>
      <h3 className="font-semibold text-slate-900 mt-3">{label}</h3>
      <p className="text-xs text-slate-600">Tap to start quickly</p>
    </button>
  );
}

function SourcesPanel({ lastAssistant, collapsible = false }) {
  const [open, setOpen] = useState(!collapsible);
  if (collapsible) {
    return (
      <div className="border border-slate-200 rounded-xl bg-white shadow-sm">
        <button
          onClick={() => setOpen(!open)}
          className="w-full px-4 py-2 flex items-center justify-between text-sm font-semibold text-slate-700"
        >
          Sources
          <span>{open ? '-' : '+'}</span>
        </button>
        {open && <SourcesList lastAssistant={lastAssistant} />}
      </div>
    );
  }
  return (
    <div className="sticky top-4 bg-white border border-slate-200 rounded-xl shadow-sm p-4 min-h-[200px]">
      <h3 className="text-sm font-semibold text-slate-800 mb-3">Sources</h3>
      <SourcesList lastAssistant={lastAssistant} />
    </div>
  );
}

function SourcesList({ lastAssistant }) {
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
}
