import { useState, useRef, useEffect } from 'react';
import type { Message } from '../types';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  isChatActive: boolean;
  onSendMessage: (content: string) => void;
  onStopMessage: () => void;
  onEditMessage: (index: number, content: string) => void;
  onRefreshMessage: (index: number) => void;
}

function ChatMessage({ 
  message, 
  index, 
  onEdit, 
  onRefresh 
}: { 
  message: Message; 
  index: number; 
  onEdit: (index: number, content: string) => void;
  onRefresh: (index: number) => void;
}) {
  const [isThoughtExpanded, setIsThoughtExpanded] = useState(true);
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
                {message.thought_process}
              </div>
            )}
          </div>
        )}
        <div className="message-content">{message.content}</div>
      </div>
      {message.role === 'user' && (
        <div className="message-actions">
          <button 
            className={`action-btn ${copied ? 'success' : ''}`} 
            onClick={handleCopy}
            title={copied ? "Copied!" : "Copy message"}
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
            title={copied ? "Copied!" : "Copy message"}
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
        </div>
      )}
    </div>
  );
}

export default function ChatArea({
  messages,
  isLoading,
  isChatActive,
  onSendMessage,
  onStopMessage,
  onEditMessage,
  onRefreshMessage,
}: ChatAreaProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = () => {
    if (isLoading) {
      onStopMessage();
      return;
    }
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) handleSubmit();
    }
  };

  const lastMessage = messages[messages.length - 1];
  const showTypingIndicator = isLoading && (
    !lastMessage || 
    lastMessage.role === 'user' || 
    (lastMessage.role === 'assistant' && !lastMessage.content && !lastMessage.thought_process)
  );

  return (
    <div className="central-interface">
      {!isChatActive && (
        <div className="greeting">
          <h1>How can I help you?</h1>
        </div>
      )}

      <div className={`chat-messages ${isChatActive ? 'visible' : ''}`}>
        {messages.map((message, index) => {
          const isLast = index === messages.length - 1;
          if (showTypingIndicator && isLast && message.role === 'assistant' && !message.content && !message.thought_process) {
            return null;
          }
          return <ChatMessage key={index} message={message} index={index} onEdit={onEditMessage} onRefresh={onRefreshMessage} />;
        })}
        {showTypingIndicator && (
          <div className="message assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={`input-container ${isChatActive ? 'chat-active' : ''}`}>
        <div className="input-bar">
          <button className="attachment-btn" onClick={() => inputRef.current?.focus()}>
            <svg
              className="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
          <input
            ref={inputRef}
            type="text"
            className="text-input"
            placeholder="Ask any question"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            className={`send-btn ${isLoading ? 'stop' : ''}`}
            onClick={handleSubmit}
            disabled={!isLoading && !input.trim()}
          >
            {isLoading ? (
              <div className="stop-icon"></div>
            ) : (
              <svg
                className="icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
