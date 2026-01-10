import { useState, useRef, useEffect } from 'react';
import type { Session } from '../types';

interface SidebarProps {
  sessions: Session[];
  currentSessionId: number | null;
  onNewChat: () => void;
  onSessionSelect: (sessionId: number) => void;
  onRenameSession: (sessionId: number, newTitle: string) => void;
  onDeleteSession: (sessionId: number) => void;
}

export default function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSessionSelect,
  onRenameSession,
  onDeleteSession,
}: SidebarProps) {
  const [activeMenuId, setActiveMenuId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenuId(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleRenameStart = (session: Session) => {
    setEditingId(session.id);
    setEditTitle(session.title);
    setActiveMenuId(null);
  };

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingId !== null && inputRef.current) {
      inputRef.current.select();
    }
  }, [editingId]);

  const handleRenameSubmit = (e: React.FormEvent, sessionId: number) => {
    e.preventDefault();
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingId(null);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="sidebar-item new-chat" onClick={onNewChat}>
          <svg
            className="icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
          <span>New Chat</span>
        </button>
      </div>
      <div className="session-list">
        {sessions.map((session) => (
          <div key={session.id} className="session-item-container">
            {editingId === session.id ? (
              <form
                className="rename-form"
                onSubmit={(e) => handleRenameSubmit(e, session.id)}
              >
                <input
                  ref={inputRef}
                  autoFocus
                  className="rename-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={(e) => handleRenameSubmit(e, session.id)}
                />
              </form>
            ) : (
              <div
                className={`session-item ${
                  currentSessionId === session.id ? 'active' : ''
                } ${activeMenuId === session.id ? 'menu-open' : ''}`}
                onClick={() => onSessionSelect(session.id)}
              >
                <svg
                  className="icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <span className="session-title">{session.title}</span>
                <div className={`session-actions ${activeMenuId === session.id ? 'visible' : ''}`}>
                  <button
                    className="dots-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveMenuId(activeMenuId === session.id ? null : session.id);
                    }}
                  >
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <circle cx="12" cy="12" r="1" />
                      <circle cx="19" cy="12" r="1" />
                      <circle cx="5" cy="12" r="1" />
                    </svg>
                  </button>
                  {activeMenuId === session.id && (
                    <div className="context-menu" ref={menuRef} onClick={(e) => e.stopPropagation()}>
                      <button
                        className="menu-option"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRenameStart(session);
                        }}
                      >
                        <svg
                          className="menu-icon"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                        >
                          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                        </svg>
                        <span>Rename</span>
                      </button>
                      <div className="menu-divider" />
                      <button
                        className="menu-option delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteSession(session.id);
                          setActiveMenuId(null);
                        }}
                      >
                        <svg
                          className="menu-icon"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                        >
                          <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                        <span>Delete</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
}
