import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  return (
    <div className={`message-bubble ${isUser ? 'message-user' : 'message-assistant'} break-words`}>
      <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-1">
        {isUser ? 'You' : 'MyDost'}
      </div>
      <div className="prose dark:prose-invert max-w-none text-sm sm:text-base">
        <ReactMarkdown
          components={{
            code: ({ inline, children }) => {
              if (inline) {
                return <code className="text-xs sm:text-sm">{children}</code>;
              }
              return (
                <pre className="overflow-x-auto">
                  <code className="text-xs sm:text-sm">{children}</code>
                </pre>
              );
            },
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer" className="break-all">
                {children}
              </a>
            ),
          }}
        >
          {message}
        </ReactMarkdown>
      </div>
      {sources && sources.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600 text-xs">
          <div className="font-semibold text-gray-600 dark:text-gray-400 flex items-center gap-1">
            🔍 Sources:
          </div>
          {sources.map((source, idx) => (
            <div key={idx} className="text-gray-600 dark:text-gray-400 truncate">
              [{source.number}] <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {source.title}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
