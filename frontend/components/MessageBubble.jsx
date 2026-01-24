import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`message-bubble ${isUser ? 'message-user' : 'message-assistant'} break-words shadow-sm`}>
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${isUser ? 'bg-cyan-600 text-white' : 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'}`}>
            {isUser ? '👤' : '🤖'}
          </div>
          <div className="text-xs font-medium text-gray-600 dark:text-gray-400">
            {isUser ? 'You' : 'MyDost'}
          </div>
        </div>
        <div className="prose dark:prose-invert max-w-none text-sm sm:text-base prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-ol:my-2">
          <ReactMarkdown
            components={{
              code: ({ inline, children }) => {
                if (inline) {
                  return <code className="text-xs sm:text-sm bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded">{children}</code>;
                }
                return (
                  <pre className="overflow-x-auto bg-gray-900 dark:bg-gray-950 p-3 rounded-lg my-2">
                    <code className="text-xs sm:text-sm text-gray-100">{children}</code>
                  </pre>
                );
              },
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" className="text-cyan-600 dark:text-cyan-400 hover:underline break-all">
                  {children}
                </a>
              ),
              p: ({ children }) => (
                <p className="leading-relaxed">{children}</p>
              ),
            }}
          >
            {message}
          </ReactMarkdown>
        </div>
        {sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <div className="flex items-center gap-1 text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
              <span className="text-sm">🔍</span>
              <span>Sources</span>
            </div>
            <div className="space-y-1.5">
              {sources.map((source, idx) => (
                <a 
                  key={idx}
                  href={source.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors group"
                >
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-cyan-100 dark:bg-cyan-900 flex items-center justify-center text-[10px] font-bold text-cyan-700 dark:text-cyan-300 group-hover:bg-cyan-200 dark:group-hover:bg-cyan-800">
                    {source.number || idx + 1}
                  </span>
                  <div className="flex-1">
                    <span className="line-clamp-1 group-hover:underline font-medium">
                      {source.title}
                    </span>
                    <span className="text-[10px] text-gray-500 dark:text-gray-500 block mt-0.5">
                      {source.source || (source.url ? new URL(source.url).hostname : 'Unknown')}
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
