import { useState, useRef } from 'react';
import { apiClient } from '../../api/apiClient';

type PendingFile = {
  id: string;
  url?: string;
  progress: number;
  file: File;
  blobUrl: string;
  type: 'image' | 'video' | 'audio';
};

type ChatInputBarProps = {
  isLoading: boolean;
  isChatActive: boolean;
  onSendMessage: (content: string, imageUrls?: string[], videoUrls?: string[], audioUrls?: string[]) => void;
  onStopMessage: () => void;
};

const ChatInputBar = ({ isLoading, isChatActive, onSendMessage, onStopMessage }: ChatInputBarProps) => {
  const [input, setInput] = useState('');
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const newPending = Array.from(files).map((file): PendingFile => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      blobUrl: URL.createObjectURL(file),
      type: file.type.startsWith('video/')
        ? 'video'
        : file.type.startsWith('audio/')
          ? 'audio'
          : 'image',
    }));

    setPendingFiles((prev) => [...prev, ...newPending]);

    if (fileInputRef.current) fileInputRef.current.value = '';

    for (const item of newPending) {
      try {
        let uploadFn;
        if (item.type === 'video') {
          uploadFn = apiClient.uploadVideo.bind(apiClient);
        } else if (item.type === 'audio') {
          uploadFn = apiClient.uploadAudio.bind(apiClient);
        } else {
          uploadFn = apiClient.uploadImage.bind(apiClient);
        }

        const url = await uploadFn(item.file, (progress) => {
          setPendingFiles((prev) => prev.map((p) => (p.id === item.id ? { ...p, progress } : p)));
        });
        if (url) {
          setPendingFiles((prev) => prev.map((p) => (p.id === item.id ? { ...p, url, progress: 100 } : p)));
        }
      } catch (err) {
        console.error('Upload failed', err);
        setPendingFiles((prev) => prev.filter((p) => p.id !== item.id));
      }
    }
  };

  const removePendingFile = (id: string) => {
    setPendingFiles((prev) => {
      const item = prev.find((p) => p.id === id);
      if (item) URL.revokeObjectURL(item.blobUrl);
      return prev.filter((p) => p.id !== id);
    });
  };

  const handleSubmit = () => {
    if (isLoading) {
      onStopMessage();
      return;
    }
    if (input.trim() || pendingFiles.some((f) => f.url)) {
      const imageUrls = pendingFiles.filter((f) => f.url && f.type === 'image').map((f) => f.url!);
      const videoUrls = pendingFiles.filter((f) => f.url && f.type === 'video').map((f) => f.url!);
      const audioUrls = pendingFiles.filter((f) => f.url && f.type === 'audio').map((f) => f.url!);
      onSendMessage(input, imageUrls, videoUrls, audioUrls);
      setInput('');
      pendingFiles.forEach((f) => URL.revokeObjectURL(f.blobUrl));
      setPendingFiles([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) handleSubmit();
    }
  };

  return (
    <div className={`input-container ${isChatActive ? 'chat-active' : ''}`}>
      {pendingFiles.length > 0 && (
        <div className="pending-images-bar">
          {pendingFiles.map((file) => (
            <div key={file.id} className="pending-image-container">
              {file.type === 'video' ? (
                <video src={file.blobUrl} className="pending-image" />
              ) : file.type === 'audio' ? (
                <div className="pending-image audio-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '24px' }}>
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" y1="19" x2="12" y2="23" />
                    <line x1="8" y1="23" x2="16" y2="23" />
                  </svg>
                </div>
              ) : (
                <img src={file.blobUrl} alt="pending" className="pending-image" />
              )}
              {file.progress < 100 && (
                <div className="upload-progress-overlay">
                  <div
                    className="progress-ring"
                    style={{ ['--progress' as string]: `${file.progress}%` }}
                  ></div>
                </div>
              )}
              <button className="remove-image-btn" onClick={() => removePendingFile(file.id)}>×</button>
            </div>
          ))}
        </div>
      )}
      <div className="input-bar">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
          multiple
          accept="image/*,video/*,audio/*"
        />
        <button className="attachment-btn" onClick={() => fileInputRef.current?.click()}>
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
          disabled={!isLoading && !input.trim() && !pendingFiles.some((f) => f.url)}
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
  );
};

export default ChatInputBar;
