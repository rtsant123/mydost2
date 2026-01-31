import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  // Modern card style for assistant, chat bubble for user
  if (isUser) {
    return (
      <div className="flex justify-end mb-4 sm:mb-5">
        <div className="max-w-3xl w-fit rounded-2xl px-4 sm:px-5 py-3 shadow border bg-slate-900 text-white border-slate-800">
          <div className="flex items-center gap-2 mb-1 text-[11px] font-semibold text-slate-200">
            <span className="uppercase tracking-wide">You</span>
          </div>
          <div className="prose prose-invert max-w-none text-sm sm:text-base prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2 prose-strong:text-white">
            <ReactMarkdown>{message}</ReactMarkdown>
          </div>
        </div>
      </div>
    );
  }

  // Assistant (Perplexity/Poe style)
  return (
    <div className="flex justify-start mb-8">
      <div className="max-w-3xl w-full rounded-2xl sm:rounded-2xl rounded-xl bg-white border border-slate-200 shadow-xl px-0 sm:px-0 py-0 relative professional-bubble">
        {/* Colored left border for emphasis */}
        <div className="absolute left-0 top-0 h-full w-2 rounded-l-2xl bg-gradient-to-b from-cyan-500 via-blue-500 to-indigo-500" />
        {/* Header */}
        <div className="flex items-center gap-2 px-4 sm:px-7 pt-4 sm:pt-6 pb-1 sm:pb-2">
          <span className="inline-flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-gradient-to-br from-cyan-600 to-indigo-600 text-white text-lg sm:text-xl font-bold shadow">🤖</span>
          <span className="font-semibold text-slate-900 text-sm sm:text-base tracking-wide">MyDost</span>
        </div>
        {/* Main content */}
        <div className="prose max-w-none text-slate-900 px-4 sm:px-7 pb-4 sm:pb-5 pt-1 text-[14px] sm:text-[15px] font-inter prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:pl-2 prose-li:marker:text-cyan-600 prose-strong:text-blue-700 prose-headings:text-indigo-700">
          <ReactMarkdown
            components={{
              code: ({ inline, children }) =>
                inline ? (
                  <code className="text-xs sm:text-sm px-1 py-0.5 sm:px-1.5 rounded bg-slate-100 text-slate-900 border border-slate-200">{children}</code>
                ) : (
                  <pre className="overflow-x-auto p-2 sm:p-3 rounded-lg my-2 border bg-slate-900 text-slate-50 border-slate-800 text-xs sm:text-sm">
                    <code>{children}</code>
                  </pre>
                ),
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline break-all text-cyan-600"
                >
                  {children}
                </a>
              ),
              p: ({ children }) => <p className="leading-relaxed my-2">{children}</p>,
              li: ({ children }) => <li className="pl-1 my-1">{children}</li>,
              h2: ({ children }) => <h2 className="text-base sm:text-lg font-bold text-indigo-700 mt-4 mb-2">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm sm:text-base font-semibold text-blue-700 mt-3 mb-1">{children}</h3>,
            }}
          >
            {message}
          </ReactMarkdown>
        </div>
        {/* References */}
        {sources && sources.length > 0 && (
          <div className="bg-slate-50 border-t border-slate-200 px-4 sm:px-7 pt-3 sm:pt-4 pb-2 sm:pb-3 rounded-b-2xl">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-2">
              <span className="inline-block text-slate-500">References</span>
            </div>
            <div className="grid gap-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3">
              {sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group border border-slate-200 rounded-xl px-3 py-2 hover:border-cyan-400 transition-colors bg-white flex flex-col h-full shadow-sm"
                >
                  <div className="flex items-center gap-2 text-[11px] text-slate-700 font-semibold mb-1">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-cyan-100 text-cyan-700 font-bold">
                      {source.number || idx + 1}
                    </span>
                    <span className="line-clamp-1 group-hover:underline text-xs font-medium">{source.title}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 line-clamp-2">
                    {source.source || (source.url ? new URL(source.url).hostname : 'Unknown')}
                  </p>
                  {source.fetched_at && (
                    <p className="text-[10px] text-slate-400 mt-1">
                      Updated: {new Date(source.fetched_at).toLocaleTimeString()}
                    </p>
                  )}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
