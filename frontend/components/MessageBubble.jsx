import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message, isUser, sources }) {
  return (
    <div className={`message-bubble ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
        {isUser ? 'You' : 'Claude'}
      </div>
      <div className="prose dark:prose-invert max-w-none text-base">
        <ReactMarkdown
          components={{
            code: ({ inline, children }) => {
              if (inline) {
                return <code>{children}</code>;
              }
              return (
                <pre>
                  <code>{children}</code>
                </pre>
              );
            },
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer">
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
          <div className="font-semibold text-gray-600 dark:text-gray-400">Sources:</div>
          {sources.map((source, idx) => (
            <div key={idx} className="text-gray-600 dark:text-gray-400">
              [{source.number}] <a href={source.url} target="_blank" rel="noopener noreferrer">
                {source.title}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
