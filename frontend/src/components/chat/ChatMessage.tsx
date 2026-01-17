import { useState } from 'react';
import type { CSSProperties } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Components } from 'react-markdown';
import type { Message } from '../../types';
import getFullImageUrl from './utils';

type ChatMessageProps = {
  message: Message;
  index: number;
  onEdit: (index: number, content: string) => void;
  onRefresh: (index: number) => void;
  onImageClick: (url: string) => void;
};

const syntaxTheme: { [key: string]: CSSProperties } = oneLight as unknown as { [key: string]: CSSProperties };

const ChatMessage = ({ message, index, onEdit, onRefresh, onImageClick }: ChatMessageProps) => {
  const [isThoughtExpanded, setIsThoughtExpanded] = useState(true);
  const [expandedSearchResults, setExpandedSearchResults] = useState<Record<string, boolean>>({});
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditContent(message.content);
  };

  const handleSend = () => {
    if (editContent.trim()) {
      onEdit(index, editContent);
      setIsEditing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className="message-edit-container">
        <textarea
          className="message-edit-input"
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
        />
        <div className="edit-actions">
          <button className="edit-btn cancel" onClick={handleCancel}>Cancel</button>
          <button className="edit-btn send" onClick={handleSend}>Send</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`message-container ${message.role}`}>
      <div className={`message ${message.role}`}>
        {message.role === 'assistant' && message.thought_process && (
          <div className="thought-process-container">
            <button
              className="thought-process-header"
              onClick={() => setIsThoughtExpanded(!isThoughtExpanded)}
            >
              <svg
                className={`chevron-icon ${isThoughtExpanded ? 'expanded' : ''}`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
              <span>Thought Process</span>
            </button>
            {isThoughtExpanded && (
              <div className="thought-process-content">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                  {message.thought_process}
                </ReactMarkdown>
              </div>
            )}
          </div>
        )}
        {message.images && message.images.length > 0 && (
          <div className="message-images">
            {message.images.map((url, i) =>
              url ? (
                <img
                  key={i}
                  src={getFullImageUrl(url)}
                  alt="attachment"
                  className="message-image"
                  onClick={() => onImageClick(getFullImageUrl(url))}
                />
              ) : null
            )}
          </div>
        )}
        {message.videos && message.videos.length > 0 && (
          <div className="message-videos">
            {message.videos.map((url, i) => (
              <video
                key={i}
                src={getFullImageUrl(url)}
                controls
                className="message-video"
                style={{ maxWidth: '100%', borderRadius: '8px', marginTop: '8px' }}
              />
            ))}
          </div>
        )}
        {message.audios && message.audios.length > 0 && (
          <div className="message-audios" style={{ marginTop: '8px' }}>
            {message.audios.map((url, i) => (
              <audio
                key={i}
                src={getFullImageUrl(url)}
                controls
                className="message-audio"
                style={{ width: '100%', borderRadius: '8px' }}
              />
            ))}
          </div>
        )}
        <div className="message-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkBreaks]}
            components={
              {
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <SyntaxHighlighter
                      style={syntaxTheme}
                      language={match[1]}
                      PreTag="div"
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
                img({ src, alt }) {
                  if (!src) {
                    return null;
                  }
                  const isVideo = src?.toLowerCase().endsWith('.mp4') || alt === 'video';
                  if (isVideo && src) {
                    return (
                      <video
                        src={getFullImageUrl(src)}
                        controls
                        className="message-markdown-video"
                        style={{ maxWidth: '100%', borderRadius: '8px', margin: '8px 0', display: 'block' }}
                      />
                    );
                  }
                  return (
                    <img
                      src={getFullImageUrl(src)}
                      alt={alt}
                      className="message-markdown-image"
                      onClick={() => onImageClick(getFullImageUrl(src))}
                      title="Click to view full size"
                    />
                  );
                },
                a({ href, children }) {
                  if (!href) {
                    return <>{children}</>;
                  }
                  return (
                    <a href={href} target="_blank" rel="noreferrer">
                      {children}
                    </a>
                  );
                },
              } satisfies Components
            }
          >
            {message.content}
          </ReactMarkdown>
        </div>
        {message.role === 'assistant' && message.search_results && message.search_results.length > 0 && (
          <div className="search-results-container">
            <button
              className="search-results-header"
            >
              <svg
                className="chevron-icon expanded"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
              <span>Search Results</span>
            </button>
            <div className="search-results-content">
              <ul className="search-results-list">
                {message.search_results.map((result, i) => {
                  const resultKey = `${result.url}-${i}`;
                  const isExpanded = expandedSearchResults[resultKey] ?? false;
                  const hasContent = Boolean(result.content);

                  return (
                    <li key={resultKey} className="search-results-item">
                      <div className="search-results-item-header">
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noreferrer"
                          className="search-results-link"
                        >
                          {result.title || result.url}
                        </a>
                        {hasContent && (
                          <button
                            className="search-results-toggle"
                            onClick={() =>
                              setExpandedSearchResults((prev) => ({
                                ...prev,
                                [resultKey]: !isExpanded,
                              }))
                            }
                          >
                            <svg
                              className={`chevron-icon ${isExpanded ? 'expanded' : ''}`}
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                            >
                              <path d="m9 18 6-6-6-6" />
                            </svg>
                            <span>{isExpanded ? 'Hide' : 'Show'}</span>
                          </button>
                        )}
                      </div>
                      {hasContent && isExpanded && (
                        <div className="search-results-snippet">{result.content}</div>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        )}
      </div>
      {message.role === 'user' && (
        <div className="message-actions">
          <button
            className={`action-btn ${copied ? 'success' : ''}`}
            onClick={handleCopy}
            title={copied ? 'Copied!' : 'Copy message'}
          >
            {copied ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 12L10 16L18 8" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <rect x="8" y="4" width="12" height="12" rx="2.5" />
                <rect x="4" y="8" width="12" height="12" rx="2.5" fill="white" stroke="currentColor" />
              </svg>
            )}
          </button>
          <button
            className="action-btn"
            onClick={() => setIsEditing(true)}
            title="Edit message"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14.5 3.5L19 8L7 20H4V17L14.5 3.5Z" />
              <path d="M13.5 4.5L18 9" />
            </svg>
          </button>
        </div>
      )}
      {message.role === 'assistant' && (
        <div className="message-actions assistant-visible">
          <button
            className={`action-btn ${copied ? 'success' : ''}`}
            onClick={handleCopy}
            title={copied ? 'Copied!' : 'Copy message'}
          >
            {copied ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 12L10 16L18 8" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <rect x="8" y="4" width="12" height="12" rx="2.5" />
                <rect x="4" y="8" width="12" height="12" rx="2.5" fill="white" stroke="currentColor" />
              </svg>
            )}
          </button>
          <button
            className="action-btn"
            onClick={() => onRefresh(index)}
            title="Refresh response"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 4v6h6" />
              <path d="M23 20v-6h-6" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10" />
              <path d="M3.51 15a9 9 0 0 0 14.85 4.36L23 14" />
            </svg>
          </button>
          {message.provider && message.model && (
            <span className="message-model-info">{message.provider}/{message.model}</span>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
