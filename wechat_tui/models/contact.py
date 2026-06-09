"""Contact model for WeChat users and chat rooms."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ContactType(Enum):
    """Type of contact."""

    USER = "user"
    CHATROOM = "chatroom"
    MP = "mp"  # Official account


@dataclass
class Contact:
    """Represents a WeChat contact (user, chatroom, or official account)."""

    user_id: str  # Unique identifier (UserName in WeChat)
    name: str  # Display name (NickName or RemarkName)
    contact_type: ContactType = ContactType.USER

    # Optional fields
    avatar_url: Optional[str] = None
    signature: Optional[str] = None  # Personal signature
    province: Optional[str] = None
    city: Optional[str] = None
    gender: int = 0  # 0: unknown, 1: male, 2: female

    # For chatrooms
    member_count: int = 0
    owner_id: Optional[str] = None

    # UI state
    is_starred: bool = False
    unread_count: int = 0
    last_message_time: Optional[float] = None  # Unix timestamp

    @property
    def display_name(self) -> str:
        """Get the display name for the contact."""
        return self.name or self.user_id

    @property
    def is_chatroom(self) -> bool:
        """Check if this is a chatroom."""
        return self.contact_type == ContactType.CHATROOM

    @classmethod
    def from_itchat(cls, raw: dict) -> "Contact":
        """Create a Contact from itchat raw data."""
        user_name = raw.get("UserName", "")
        remark_name = raw.get("RemarkName", "")
        nick_name = raw.get("NickName", "")

        # Determine contact type
        if user_name.endswith("@chatroom"):
            contact_type = ContactType.CHATROOM
        elif raw.get("VerifyFlag", 0) & 8:  # Official account
            contact_type = ContactType.MP
        else:
            contact_type = ContactType.USER

        return cls(
            user_id=user_name,
            name=remark_name or nick_name or user_name,
            contact_type=contact_type,
            avatar_url=raw.get("HeadImgUrl"),
            signature=raw.get("Signature"),
            province=raw.get("Province"),
            city=raw.get("City"),
            gender=raw.get("Sex", 0),
            member_count=raw.get("MemberCount", 0),
            is_starred=raw.get("StarFriend", False),
        )

    def __hash__(self) -> int:
        return hash(self.user_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return False
        return self.user_id == other.user_id


@dataclass
class ContactList:
    """Manages a collection of contacts."""

    contacts: dict[str, Contact] = field(default_factory=dict)
    recent_chats: list[str] = field(default_factory=list)  # List of user_ids

    def add(self, contact: Contact) -> None:
        """Add or update a contact."""
        self.contacts[contact.user_id] = contact

    def get(self, user_id: str) -> Optional[Contact]:
        """Get a contact by user_id."""
        return self.contacts.get(user_id)

    def remove(self, user_id: str) -> None:
        """Remove a contact."""
        self.contacts.pop(user_id, None)
        if user_id in self.recent_chats:
            self.recent_chats.remove(user_id)

    def update_recent(self, user_id: str) -> None:
        """Move a contact to the front of recent chats."""
        if user_id in self.recent_chats:
            self.recent_chats.remove(user_id)
        self.recent_chats.insert(0, user_id)

    def get_recent(self, limit: int = 20) -> list[Contact]:
        """Get recent contacts sorted by last activity."""
        return [
            self.contacts[uid]
            for uid in self.recent_chats[:limit]
            if uid in self.contacts
        ]

    def search(self, query: str) -> list[Contact]:
        """Search contacts by name."""
        query_lower = query.lower()
        return [
            c
            for c in self.contacts.values()
            if query_lower in c.name.lower() or query_lower in c.user_id.lower()
        ]

    def all_users(self) -> list[Contact]:
        """Get all user contacts."""
        return [c for c in self.contacts.values() if c.contact_type == ContactType.USER]

    def all_chatrooms(self) -> list[Contact]:
        """Get all chatroom contacts."""
        return [c for c in self.contacts.values() if c.contact_type == ContactType.CHATROOM]