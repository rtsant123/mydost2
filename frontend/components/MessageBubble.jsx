import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 sm:mb-5`}>
      <div
        className={`max-w-3xl w-fit rounded-2xl px-4 sm:px-5 py-3 shadow-sm border ${
          isUser
            ? 'bg-indigo-50 text-slate-900 border-indigo-100'
            : 'bg-white text-slate-900 border-slate-200'
        }`}
      >
        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-500">
          <span className="uppercase tracking-wide">{isUser ? 'You' : 'MyDost'}</span>
        </div>

        <div className="prose max-w-none text-sm sm:text-base prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2 prose-strong:text-slate-800 prose-headings:text-slate-900">
          <ReactMarkdown
            components={{
              code: ({ inline, children }) => {
                if (inline) {
                  return (
                    <code className="text-xs sm:text-sm bg-slate-200 px-1.5 py-0.5 rounded text-slate-900">
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className="overflow-x-auto bg-slate-900 text-slate-50 p-3 rounded-lg my-2 border border-slate-800">
                    <code className="text-xs sm:text-sm">{children}</code>
                  </pre>
                );
              },
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-600 dark:text-cyan-300 hover:underline break-all"
                >
                  {children}
                </a>
              ),
              p: ({ children }) => <p className="leading-relaxed">{children}</p>,
            }}
          >
            {message}
          </ReactMarkdown>
        </div>

        {sources && sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-300 mb-2">
              <span className="text-sm">🔎</span>
              <span>References</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 hover:border-cyan-500 dark:hover:border-cyan-500 transition-colors bg-white/60 dark:bg-slate-800/80"
                >
                  <div className="flex items-center gap-2 text-[11px] text-cyan-700 dark:text-cyan-200 font-semibold">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-cyan-100 dark:bg-cyan-900/60 text-cyan-700 dark:text-cyan-200">
                      {source.number || idx + 1}
                    </span>
                    <span className="line-clamp-1 group-hover:underline">{source.title}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                    {source.source || (source.url ? new URL(source.url).hostname : 'Unknown')}
                  </p>
                  {source.fetched_at && (
                    <p className="text-[10px] text-slate-400 dark:text-slate-500">
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
