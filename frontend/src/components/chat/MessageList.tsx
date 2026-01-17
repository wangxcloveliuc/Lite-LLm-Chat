import { useEffect, useRef } from 'react';
import type { Message } from '../../types';
import ChatMessage from './ChatMessage';

type MessageListProps = {
  messages: Message[];
  isLoading: boolean;
  isChatActive: boolean;
  onEditMessage: (index: number, content: string) => void;
  onRefreshMessage: (index: number) => void;
  onImageClick: (url: string) => void;
};

const MessageList = ({
  messages,
  isLoading,
  isChatActive,
  onEditMessage,
  onRefreshMessage,
  onImageClick,
}: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const lastMessage = messages[messages.length - 1];
  const showTypingIndicator = isLoading && (
    !lastMessage ||
    lastMessage.role === 'user' ||
    (lastMessage.role === 'assistant' && !lastMessage.content && !lastMessage.thought_process)
  );

  return (
    <div className={`chat-messages ${isChatActive ? 'visible' : ''}`}>
      {messages.map((message, index) => {
        const isLast = index === messages.length - 1;
        if (
          showTypingIndicator &&
          isLast &&
          message.role === 'assistant' &&
          !message.content &&
          !message.thought_process
        ) {
          return null;
        }
        return (
          <ChatMessage
            key={index}
            message={message}
            index={index}
            onEdit={onEditMessage}
            onRefresh={onRefreshMessage}
            onImageClick={onImageClick}
          />
        );
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
  );
};

export default MessageList;
