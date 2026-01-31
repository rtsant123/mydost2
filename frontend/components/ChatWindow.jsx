import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import MessageBubble from './MessageBubble';
import EducationModal from './EducationModal';
import SportsModal from './SportsModal';

const ICONS = {
  robot: '\u{1F916}',
  book: '\u{1F4D6}',
  ball: '\u{1F3C0}',
  sparkles: '\u{2728}',
  toolbox: '\u{1F9F0}',
};

export default function ChatWindow({ messages, loading, onSendMessage, onNewChat }) {
  const router = useRouter();
  const [showEducationModal, setShowEducationModal] = useState(false);
  const [showMoreTools, setShowMoreTools] = useState(false);
  const [showSportsModal, setShowSportsModal] = useState(false);
  const endRef = useRef(null);
  const scrollContainerRef = useRef(null);

  // Keep the message list pinned to the bottom whenever messages change.
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    } else {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
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

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 min-h-screen p-3 sm:p-4 pb-28"
    >
      <div className="max-w-5xl mx-auto">
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
                  <DomainCard icon={ICONS.toolbox} label="More tools" pill="Tools" onClick={() => setShowMoreTools((v) => !v)} />
                </div>
                {showMoreTools && (
                  <div className="w-full max-w-4xl mx-auto mt-4">
                    <MoreToolsInline onSelectDomain={handleMoreDomainSelect} />
                  </div>
                )}
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
                  {getSuggestions(messages[messages.length - 1].content, messages).map((suggestion, idx) => (
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
      {/* MoreDomainsModal removed, now inline */}
    </div>
  );
}

// Inline version of MoreDomainsModal as a card grid
function MoreToolsInline({ onSelectDomain }) {
  const router = useRouter();
  const domains = [
    { icon: '\u{1F4C4}', name: 'PDF Tools', description: 'Upload, summarize & chat with PDFs', color: 'red', action: () => router.push('/tools/pdf') },
    { icon: '\u{1F50D}', name: 'OCR - Text Extract', description: 'Extract text from images (4 languages)', color: 'blue', action: () => router.push('/tools/ocr') },
    { icon: '\u{1F9EA}', name: 'Test Web Search', description: 'Test sports predictions & web search', color: 'green', action: () => router.push('/tools/test-search') },
    { icon: '\u{1F3AF}', name: 'Teer Results', description: 'Shillong Teer results & predictions', color: 'green', query: "Show me today's Teer results" },
    { icon: '\u{1F4F0}', name: 'News & Updates', description: 'Latest news from around the world', color: 'blue', query: "Show me today's top news headlines" },
    { icon: '\u{1F48A}', name: 'Health & Wellness', description: 'Health tips, diet & fitness advice', color: 'pink', query: 'I need health and wellness advice' },
    { icon: '\u{1F4C8}', name: 'Stock Market', description: 'Stock prices & market analysis', color: 'teal', query: 'Show me stock market updates' },
    { icon: '\u{1F30D}', name: 'Weather', description: 'Weather forecasts & updates', color: 'sky', query: "What's the weather today?" },
    { icon: '\u{1F9E0}', name: 'General Knowledge', description: 'Facts, trivia & information', color: 'purple', query: 'I want to learn general knowledge' },
    { icon: '\u{1F3B5}', name: 'Entertainment', description: 'Movies, music & celebrities', color: 'red', query: 'Tell me about latest entertainment news' },
    { icon: '\u{1F4BC}', name: 'Career & Jobs', description: 'Job search & career guidance', color: 'indigo', query: 'I need career advice' },
    { icon: '\u{1F373}', name: 'Recipes & Cooking', description: 'Food recipes & cooking tips', color: 'amber', query: 'Show me some easy recipes' },
    { icon: '\u2708\uFE0F', name: 'Travel', description: 'Travel tips & destinations', color: 'cyan', query: 'I want travel recommendations' },
    { icon: '\u{1F4B0}', name: 'Finance', description: 'Personal finance & investment tips', color: 'emerald', query: 'I need personal finance advice' },
  ];
  const colorClasses = {
    orange: 'border-orange-500 hover:bg-orange-50',
    green: 'border-green-500 hover:bg-green-50',
    blue: 'border-blue-500 hover:bg-blue-50',
    pink: 'border-pink-500 hover:bg-pink-50',
    teal: 'border-teal-500 hover:bg-teal-50',
    sky: 'border-sky-500 hover:bg-sky-50',
    purple: 'border-purple-500 hover:bg-purple-50',
    red: 'border-red-500 hover:bg-red-50',
    indigo: 'border-indigo-500 hover:bg-indigo-50',
    amber: 'border-amber-500 hover:bg-amber-50',
    cyan: 'border-cyan-500 hover:bg-cyan-50',
    emerald: 'border-emerald-500 hover:bg-emerald-50',
  };
  const handleDomainClick = (domain) => {
    if (domain.action) {
      domain.action();
    } else {
      onSelectDomain(domain.query);
    }
  };
  return (
    <div className="p-2 sm:p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {domains.map((domain, index) => (
          <button
            key={index}
            onClick={() => handleDomainClick(domain)}
            className={`group p-4 bg-white rounded-xl border-2 ${colorClasses[domain.color]} transition-all hover:shadow-lg hover:-translate-y-1 text-left`}
          >
            <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">{domain.icon}</div>
            <h3 className="font-bold text-gray-900 mb-2">{domain.name}</h3>
            <p className="text-xs text-gray-500">{domain.description}</p>
          </button>
        ))}
      </div>
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
        <p className="text-sm text-gray-700 text-center">
          <span role="img" aria-label="tip" className="mr-1">
            {'\u{1F4A1}'}
          </span>
          <strong>Tip:</strong> You can also just type what you need - I&apos;ll understand!
        </p>
      </div>
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
// Derive context-aware suggestions from the latest assistant reply and recent messages.
function getSuggestions(lastAssistantText = '', allMessages = []) {
  const lower = lastAssistantText.toLowerCase();
  const lastUser = [...allMessages].reverse().find((m) => m.role === 'user');
  const lastUserText = lastUser ? lastUser.content.toLowerCase() : '';

  const finance = /finance|budget|invest|savings|money|loan|debt|retire|portfolio/.test(lastAssistantText + lastUserText);
  const sports = /match|team|cricket|football|prediction|score|odds|ipl|t20/.test(lastAssistantText + lastUserText);
  const study = /study|exam|course|learn|school|college|university|assignment/.test(lastAssistantText + lastUserText);
  const health = /health|diet|exercise|fitness|sleep|mental/.test(lastAssistantText + lastUserText);
  const news = /news|headline|update|today/.test(lastAssistantText + lastUserText);

  if (finance) {
    return [
      'Summarize the key finance tips you gave',
      'Create a 30-day budget plan for me',
      'List 3 next actions to improve my finances',
      'Explain the risk vs return for my situation',
    ];
  }
  if (sports) {
    return [
      'Give me today’s top match insights',
      'List probable XIs with confidence scores',
      'What are 3 key factors for this match?',
      'Suggest a safe bet and a bold bet',
    ];
  }
  if (study) {
    return [
      'Make a 1-week study plan for me',
      'List 5 flashcards worth memorizing',
      'Explain the hardest concept in simple words',
      'Quiz me with 3 quick questions',
    ];
  }
  if (health) {
    return [
      'Summarize a simple daily health routine',
      'Give me a 15-minute workout I can do at home',
      'Suggest a balanced meal plan for today',
      'Share 3 science-backed tips to sleep better',
    ];
  }
  if (news) {
    return [
      'Give me 3 bullet headlines with timestamps',
      'Explain why these stories matter',
      'What should I watch for next?',
      'Find one opposing viewpoint for balance',
    ];
  }

  // Default, general-purpose follow-ups
  return [
    'Summarize that in 2 lines',
    'List key takeaways with sources',
    'What should I ask next?',
    'Can you recall anything relevant I told you before?',
  ];
}
