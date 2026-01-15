import { useState } from 'react';
import type { Message } from '../types';
import MessageList from './chat/MessageList';
import ChatInputBar from './chat/ChatInputBar';
import ChatLightbox from './chat/ChatLightbox';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  isChatActive: boolean;
  onSendMessage: (content: string, imageUrls?: string[], videoUrls?: string[], audioUrls?: string[]) => void;
  onStopMessage: () => void;
  onEditMessage: (index: number, content: string) => void;
  onRefreshMessage: (index: number) => void;
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
  const [selectedImageUrl, setSelectedImageUrl] = useState<string | null>(null);

  return (
    <div className="central-interface">
      {!isChatActive && (
        <div className="greeting">
          <h1>How can I help you?</h1>
        </div>
      )}

      <MessageList
        messages={messages}
        isLoading={isLoading}
        isChatActive={isChatActive}
        onEditMessage={onEditMessage}
        onRefreshMessage={onRefreshMessage}
        onImageClick={(url) => setSelectedImageUrl(url)}
      />

      <ChatInputBar
        isLoading={isLoading}
        isChatActive={isChatActive}
        onSendMessage={onSendMessage}
        onStopMessage={onStopMessage}
      />

      <ChatLightbox
        selectedImageUrl={selectedImageUrl}
        onClose={() => setSelectedImageUrl(null)}
      />
    </div>
  );
}
