import type { Session } from '../types';

interface SidebarProps {
  sessions: Session[];
  currentSessionId: number | null;
  onNewChat: () => void;
  onSessionSelect: (sessionId: number) => void;
}

export default function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSessionSelect,
}: SidebarProps) {
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
          <button
            key={session.id}
            className={`session-item ${
              currentSessionId === session.id ? 'active' : ''
            }`}
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
          </button>
        ))}
      </div>
    </aside>
  );
}
