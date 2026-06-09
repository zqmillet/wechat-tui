"""SQLAlchemy database manager for chat history persistence."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import Float, Index, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from ..models.message import MessageType

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class MessageRecord(Base):
    """Database model for messages."""
    __tablename__ = "messages"

    msg_id: Mapped[str] = mapped_column(String, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String, nullable=False)
    receiver_id: Mapped[str] = mapped_column(String, nullable=False)
    sender_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    receiver_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    msg_type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    file_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    local_file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_sent: Mapped[int] = mapped_column(Integer, default=0)
    is_read: Mapped[int] = mapped_column(Integer, default=0)
    actual_sender_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    actual_sender_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class SessionRecord(Base):
    """Database model for chat sessions."""
    __tablename__ = "sessions"

    contact_id: Mapped[str] = mapped_column(String, primary_key=True)
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class DatabaseManager:
    """Manages SQLite database for chat history persistence using SQLAlchemy."""

    DEFAULT_DB_PATH = "~/.wechat-tui/history.db"

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize database manager."""
        self.db_path = Path(db_path or self.DEFAULT_DB_PATH).expanduser()
        self._ensure_dir()

        # Create engine and session factory
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        # Run migration to add local_file_path column if needed
        self._migrate_add_local_file_path()

        logger.info(f"Database initialized at {self.db_path}")

    def _ensure_dir(self) -> None:
        """Ensure database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _migrate_add_local_file_path(self) -> None:
        """Add local_file_path column if it doesn't exist."""
        from sqlalchemy import text

        try:
            with self.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text("PRAGMA table_info(messages)"))
                columns = [row[1] for row in result.fetchall()]

                if "local_file_path" not in columns:
                    logger.info("Adding local_file_path column to messages table")
                    conn.execute(text("ALTER TABLE messages ADD COLUMN local_file_path VARCHAR"))
                    conn.commit()
                    logger.info("Migration completed successfully")
        except Exception as e:
            # Column may already exist or other issue
            logger.debug(f"Migration check result: {e}")

    def save_message(
        self,
        msg_id: str,
        chat_id: str,
        sender_id: str,
        receiver_id: str,
        msg_type: MessageType,
        content: str,
        timestamp: float,
        is_sent: bool,
        sender_name: Optional[str] = None,
        receiver_name: Optional[str] = None,
        file_url: Optional[str] = None,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        local_file_path: Optional[str] = None,
        actual_sender_id: Optional[str] = None,
        actual_sender_name: Optional[str] = None,
    ) -> None:
        """Save a message to database."""
        session = self.Session()
        try:
            record = MessageRecord(
                msg_id=msg_id,
                chat_id=chat_id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                sender_name=sender_name,
                receiver_name=receiver_name,
                msg_type=msg_type.value,
                content=content,
                timestamp=timestamp,
                is_sent=int(is_sent),
                file_url=file_url,
                file_name=file_name,
                file_size=file_size,
                local_file_path=local_file_path,
                actual_sender_id=actual_sender_id,
                actual_sender_name=actual_sender_name,
            )
            session.merge(record)
            session.commit()
            logger.debug(f"Saved message {msg_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save message: {e}")
        finally:
            session.close()

    def load_messages(self, contact_id: str, limit: int = 100) -> list[dict]:
        """Load messages for a contact from database."""
        session = self.Session()
        try:
            records = (
                session.query(MessageRecord)
                .filter(MessageRecord.chat_id == contact_id)
                .order_by(MessageRecord.timestamp.desc())
                .limit(limit)
                .all()
            )
            messages = []
            for r in records:
                messages.append({
                    "msg_id": r.msg_id,
                    "sender_id": r.sender_id,
                    "receiver_id": r.receiver_id,
                    "msg_type": MessageType(r.msg_type),
                    "content": r.content or "",
                    "timestamp": r.timestamp,
                    "is_sent": bool(r.is_sent),
                    "is_read": bool(r.is_read),
                    "file_url": r.file_url,
                    "file_name": r.file_name,
                    "file_size": r.file_size,
                    "local_file_path": r.local_file_path,
                    "actual_sender_id": r.actual_sender_id,
                    "actual_sender_name": r.actual_sender_name,
                })
            messages.reverse()
            return messages
        except Exception as e:
            logger.error(f"Failed to load messages: {e}")
            return []
        finally:
            session.close()

    def save_session(self, contact_id: str, unread_count: int = 0, last_message_time: Optional[float] = None) -> None:
        """Save session metadata to database."""
        session = self.Session()
        try:
            record = SessionRecord(
                contact_id=contact_id,
                unread_count=unread_count,
                updated_at=last_message_time,
            )
            session.merge(record)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save session: {e}")
        finally:
            session.close()

    def get_last_message_time_by_name(self, contact_name: str) -> float:
        """Get the last message timestamp for a contact by name."""
        session = self.Session()
        try:
            from sqlalchemy import func

            result = (
                session.query(func.max(MessageRecord.timestamp))
                .filter(
                    (MessageRecord.sender_name == contact_name)
                    | (MessageRecord.receiver_name == contact_name)
                    | (MessageRecord.actual_sender_name == contact_name)
                )
                .scalar()
            )
            return result or 0
        except Exception as e:
            logger.error(f"Failed to get last message time: {e}")
            return 0
        finally:
            session.close()

    def load_messages_by_name(self, contact_name: str, limit: int = 50) -> list[dict]:
        """Load messages for a contact by name."""
        session = self.Session()
        try:
            records = (
                session.query(MessageRecord)
                .filter(
                    (MessageRecord.sender_name == contact_name)
                    | (MessageRecord.receiver_name == contact_name)
                    | (MessageRecord.actual_sender_name == contact_name)
                )
                .order_by(MessageRecord.timestamp.desc())
                .limit(limit)
                .all()
            )
            messages = []
            for r in records:
                messages.append({
                    "msg_id": r.msg_id,
                    "sender_id": r.sender_id,
                    "receiver_id": r.receiver_id,
                    "msg_type": MessageType(r.msg_type),
                    "content": r.content or "",
                    "timestamp": r.timestamp,
                    "is_sent": bool(r.is_sent),
                    "is_read": bool(r.is_read),
                    "file_url": r.file_url,
                    "file_name": r.file_name,
                    "file_size": r.file_size,
                    "local_file_path": r.local_file_path,
                    "actual_sender_id": r.actual_sender_id,
                    "actual_sender_name": r.actual_sender_name,
                    "sender_name": r.sender_name,
                    "receiver_name": r.receiver_name,
                })
            messages.reverse()
            return messages
        except Exception as e:
            logger.error(f"Failed to load messages by name: {e}")
            return []
        finally:
            session.close()

    def get_all_chat_ids(self) -> list[str]:
        """Get all unique chat_ids from messages."""
        session = self.Session()
        try:
            from sqlalchemy import func

            results = (
                session.query(MessageRecord.chat_id, func.max(MessageRecord.timestamp))
                .group_by(MessageRecord.chat_id)
                .order_by(func.max(MessageRecord.timestamp).desc())
                .all()
            )
            return [r[0] for r in results]
        except Exception as e:
            logger.error(f"Failed to get chat_ids: {e}")
            return []
        finally:
            session.close()

    def close(self) -> None:
        """Close database connection."""
        self.engine.dispose()
        logger.info("Database connection closed")