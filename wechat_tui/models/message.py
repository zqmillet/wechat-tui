"""Message model for WeChat messages."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MessageType(Enum):
    """Type of WeChat message."""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    LINK = "link"
    CARD = "card"  # Name card
    SYSTEM = "system"  # System message
    LOCATION = "location"
    EMOTION = "emotion"  # Sticker/emoji
    RECALL = "recall"  # Message recall notification
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Represents a WeChat message."""

    msg_id: str  # Unique message identifier
    sender_id: str  # Sender's user_id
    receiver_id: str  # Receiver's user_id (could be chatroom)
    msg_type: MessageType
    content: str  # Text content or description
    timestamp: float  # Unix timestamp

    # Optional fields
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
    file_url: Optional[str] = None  # For media files (may expire)
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    local_file_path: Optional[str] = None  # Local storage path (persistent)
    is_sent: bool = False  # True if sent by current user
    is_read: bool = False

    # For chatrooms
    actual_sender_id: Optional[str] = None  # Actual sender in chatroom
    actual_sender_name: Optional[str] = None

    @property
    def datetime(self) -> datetime:
        """Get datetime object from timestamp."""
        return datetime.fromtimestamp(self.timestamp)

    @property
    def display_time(self) -> str:
        """Get formatted time for display."""
        now = datetime.now()
        msg_time = self.datetime

        if msg_time.date() == now.date():
            return msg_time.strftime("%H:%M")
        elif (now - msg_time).days < 7:
            return msg_time.strftime("%a %H:%M")
        else:
            return msg_time.strftime("%m/%d %H:%M")

    @property
    def display_content(self) -> str:
        """Get content formatted for display."""
        if self.msg_type == MessageType.TEXT:
            return self.content
        elif self.msg_type == MessageType.IMAGE:
            return "[图片]"
        elif self.msg_type == MessageType.VOICE:
            return "[语音]"
        elif self.msg_type == MessageType.VIDEO:
            return "[视频]"
        elif self.msg_type == MessageType.FILE:
            return f"[文件] {self.file_name or 'unknown'}"
        elif self.msg_type == MessageType.LINK:
            return f"[链接] {self.content}"
        elif self.msg_type == MessageType.CARD:
            return "[名片]"
        elif self.msg_type == MessageType.LOCATION:
            return "[位置]"
        elif self.msg_type == MessageType.EMOTION:
            return "[表情]"
        elif self.msg_type == MessageType.SYSTEM:
            return f"[系统消息] {self.content}"
        elif self.msg_type == MessageType.RECALL:
            return "[撤回了一条消息]"
        else:
            return "[未知消息]"

    @property
    def chat_id(self) -> str:
        """Get the chat identifier (conversation ID).

        For one-on-one chats, this is the other person's ID.
        For chatrooms, this is the chatroom ID.
        """
        return self.receiver_id if self.is_sent else self.sender_id

    @classmethod
    def from_itchat(cls, raw: dict, is_sent: bool = False) -> "Message":
        """Create a Message from itchat raw data."""
        msg_type_map: dict[int, MessageType] = {
            1: MessageType.TEXT,  # Text
            3: MessageType.IMAGE,  # Image
            34: MessageType.VOICE,  # Voice
            43: MessageType.VIDEO,  # Video
            47: MessageType.EMOTION,  # Emoji/sticker
            48: MessageType.LOCATION,  # Location
            49: MessageType.FILE,  # File/link/card (varies by content)
            51: MessageType.SYSTEM,  # System notification
            10000: MessageType.SYSTEM,  # System message
            10002: MessageType.RECALL,  # Recall notification
        }

        raw_type = raw.get("Type", 0)
        msg_type = msg_type_map.get(raw_type, MessageType.UNKNOWN)

        # Special handling for type 49 (can be file, link, or card)
        if raw_type == 49:
            content = raw.get("Content", "")
            if "appmsg" in content.lower():
                msg_type = MessageType.LINK
            elif "名片" in content or "card" in content.lower():
                msg_type = MessageType.CARD
            else:
                msg_type = MessageType.FILE

        return cls(
            msg_id=str(raw.get("MsgId", "")),
            sender_id=raw.get("FromUserName", ""),
            receiver_id=raw.get("ToUserName", ""),
            msg_type=msg_type,
            content=raw.get("Content", ""),
            timestamp=raw.get("CreateTime", 0),
            raw=raw,
            file_url=raw.get("Url"),
            file_name=raw.get("FileName"),
            is_sent=is_sent,
            actual_sender_id=raw.get("ActualUserName"),
            actual_sender_name=raw.get("ActualNickName"),
        )


@dataclass
class ChatSession:
    """Represents a chat session with a contact."""

    contact_id: str
    messages: list[Message] = field(default_factory=list)
    last_message: Optional[Message] = None
    unread_count: int = 0

    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.last_message = message
        if not message.is_sent and not message.is_read:
            self.unread_count += 1

    def mark_read(self) -> None:
        """Mark all messages as read."""
        for msg in self.messages:
            msg.is_read = True
        self.unread_count = 0

    def get_messages(self, limit: int = 50, before_id: Optional[str] = None) -> list[Message]:
        """Get messages with optional pagination."""
        if before_id:
            try:
                idx = next(i for i, m in enumerate(self.messages) if m.msg_id == before_id)
                return self.messages[max(0, idx - limit) : idx]
            except StopIteration:
                pass
        return self.messages[-limit:]

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.last_message = None
        self.unread_count = 0