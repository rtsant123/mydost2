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
    <div className="flex justify-start mb-6">
      <div className="max-w-3xl w-full rounded-2xl bg-white border border-slate-200 shadow-lg px-0 sm:px-0 py-0">
        {/* Header */}
        <div className="flex items-center gap-2 px-5 pt-5 pb-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-slate-900 text-white text-xl font-bold">🤖</span>
          <span className="font-semibold text-slate-900 text-base">MyDost</span>
        </div>
        {/* Main content */}
        <div className="prose max-w-none text-slate-900 px-5 pb-4 pt-1 text-[15px] sm:text-base">
          <ReactMarkdown
            components={{
              code: ({ inline, children }) =>
                inline ? (
                  <code className="text-xs sm:text-sm px-1.5 py-0.5 rounded bg-slate-200 text-slate-900">{children}</code>
                ) : (
                  <pre className="overflow-x-auto p-3 rounded-lg my-2 border bg-slate-900 text-slate-50 border-slate-800">
                    <code className="text-xs sm:text-sm">{children}</code>
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
            }}
          >
            {message}
          </ReactMarkdown>
        </div>
        {/* References */}
        {sources && sources.length > 0 && (
          <div className="bg-slate-50 border-t border-slate-200 px-5 pt-4 pb-3 rounded-b-2xl">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-2">
              <span className="inline-block text-slate-500">References</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
              {sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group border border-slate-200 rounded-xl px-3 py-2 hover:border-slate-300 transition-colors bg-white flex flex-col h-full"
                >
                  <div className="flex items-center gap-2 text-[11px] text-slate-700 font-semibold mb-1">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-700 font-bold">
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
