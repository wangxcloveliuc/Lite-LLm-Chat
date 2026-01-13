"""
Database models and setup
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
from config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)  # List of image URLs/paths
    videos = Column(JSON, nullable=True)  # List of video URLs/paths
    audios = Column(JSON, nullable=True)  # List of audio URLs/paths
    thought_process = Column(Text, nullable=True)  # For reasoning/thinking content from inference models
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

    # Lightweight migration for existing SQLite databases (create_all does not add columns).
    with engine.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA table_info(chat_messages)")
        existing_cols = {row[1] for row in result.fetchall()}
        if "provider" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN provider VARCHAR(50)")
        if "model" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN model VARCHAR(100)")
        if "thought_process" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN thought_process TEXT")
        if "images" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN images TEXT")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
