import { useState, useRef, useEffect } from 'react';
import type { Message } from '../types';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  isChatActive: boolean;
  onSendMessage: (content: string) => void;
}

function ChatMessage({ message }: { message: Message }) {
  const [isThoughtExpanded, setIsThoughtExpanded] = useState(true);

  return (
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
  );
}

export default function ChatArea({
  messages,
  isLoading,
  isChatActive,
  onSendMessage,
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
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
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
          return <ChatMessage key={index} message={message} />;
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
            className="send-btn"
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
          >
            <svg
              className="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
