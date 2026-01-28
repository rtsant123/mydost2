import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  const bubbleClasses = isUser
    ? 'bg-slate-900 text-white border-slate-800'
    : 'bg-white text-slate-900 border-slate-200';
  const proseClasses = isUser
    ? 'prose prose-invert max-w-none text-sm sm:text-base prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2 prose-strong:text-white'
    : 'prose max-w-none text-sm sm:text-base prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2 prose-strong:text-slate-800 prose-headings:text-slate-900';
  const labelClasses = isUser ? 'text-slate-200' : 'text-slate-500';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 sm:mb-5`}>
      <div
        className={`max-w-3xl w-fit rounded-2xl px-4 sm:px-5 py-3 shadow-sm border ${bubbleClasses}`}
      >
        <div className={`flex items-center gap-2 mb-1 text-[11px] font-semibold ${labelClasses}`}>
          <span className="uppercase tracking-wide">{isUser ? 'You' : 'MyDost'}</span>
        </div>

        <div className={proseClasses}>
          <ReactMarkdown
            components={{
              code: ({ inline, children }) => {
                if (inline) {
                  return (
                    <code
                      className={`text-xs sm:text-sm px-1.5 py-0.5 rounded ${
                        isUser ? 'bg-slate-800 text-white' : 'bg-slate-200 text-slate-900'
                      }`}
                    >
                      {children}
                    </code>
                  );
                }
                return (
                  <pre
                    className={`overflow-x-auto p-3 rounded-lg my-2 border ${
                      isUser ? 'bg-black text-white border-slate-800' : 'bg-slate-900 text-slate-50 border-slate-800'
                    }`}
                  >
                    <code className="text-xs sm:text-sm">{children}</code>
                  </pre>
                );
              },
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`hover:underline break-all ${isUser ? 'text-cyan-300' : 'text-cyan-600'}`}
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
          <div className="mt-4 pt-3 border-t border-slate-200">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 mb-2">
              <span>References</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group border border-slate-200 rounded-xl px-3 py-2 hover:border-slate-300 transition-colors bg-white"
                >
                  <div className="flex items-center gap-2 text-[11px] text-slate-700 font-semibold">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-700">
                      {source.number || idx + 1}
                    </span>
                    <span className="line-clamp-1 group-hover:underline">{source.title}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1 line-clamp-2">
                    {source.source || (source.url ? new URL(source.url).hostname : 'Unknown')}
                  </p>
                  {source.fetched_at && (
                    <p className="text-[10px] text-slate-400">
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
