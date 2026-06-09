"""Chat panel widget for displaying messages."""

from datetime import datetime
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static

from ...models.contact import Contact, ContactType
from ...models.message import ChatSession, Message, MessageType


class MessageItem(Widget):
    """A single message in the chat."""

    DEFAULT_CSS = """
    MessageItem {
        width: 100%;
        height: auto;
        min-height: 1;
        padding: 0 2;
        margin: 0 0 1 0;
    }

    MessageItem .message-row {
        width: 100%;
        height: auto;
    }

    MessageItem .spacer {
        width: 1fr;
    }

    MessageItem .bubble {
        width: auto;
        max-width: 65%;
        height: auto;
        min-height: 1;
        padding: 1;
        margin: 0;
    }

    MessageItem.sent .bubble {
        background: #238636;
        color: #ffffff;
    }

    MessageItem.received .bubble {
        background: #21262d;
        color: #c9d1d9;
    }

    MessageItem .time {
        color: #8b949e;
        text-style: dim;
    }

    MessageItem .sender {
        color: $accent;
        text-style: bold;
    }

    MessageItem.system {
        text-align: center;
        color: $text-muted;
        text-style: italic;
        width: 100%;
    }

    MessageItem.system .system-text {
        text-align: center;
    }
    """

    def __init__(self, message: Message, contact_name: Optional[str] = None) -> None:
        super().__init__()
        self.message = message
        self.contact_name = contact_name

    def compose(self) -> ComposeResult:
        """Compose the message item with proper alignment."""
        if self.message.msg_type == MessageType.SYSTEM:
            self.add_class("system")
            yield Static(self.message.display_content, classes="system-text")
            return

        # Add alignment class
        if self.message.is_sent:
            self.add_class("sent")
        else:
            self.add_class("received")

        # Build message text
        time_str = self.message.display_time

        if self.message.is_sent:
            # Sent message - right aligned
            text = f"[{time_str}]\n{self.message.display_content}"
            with Horizontal(classes="message-row"):
                yield Static("", classes="spacer")  # Left spacer pushes bubble right
                yield Static(text, classes="bubble")
        else:
            # Received message - left aligned
            sender = self.message.actual_sender_name or self.contact_name or "未知"
            text = f"[{time_str}] {sender}\n{self.message.display_content}"
            with Horizontal(classes="message-row"):
                yield Static(text, classes="bubble")
                yield Static("", classes="spacer")  # Right spacer


class ChatPanel(Widget):
    """Panel displaying a chat conversation."""

    DEFAULT_CSS = """
    ChatPanel {
        width: 1fr;
        height: 1fr;
        background: $surface;
    }

    ChatPanel .header {
        height: 3;
        padding: 0 1;
        background: $panel;
        border-bottom: solid $primary;
    }

    ChatPanel .header .title {
        text-style: bold;
    }

    ChatPanel .header .subtitle {
        color: $text-muted;
    }

    ChatPanel ScrollableContainer {
        height: 1fr;
    }

    ChatPanel .no-chat {
        padding: 2;
        color: $text-muted;
        text-align: center;
    }

    ChatPanel .empty-chat {
        padding: 2;
        color: $text-muted;
        text-align: center;
    }
    """

    session: reactive[Optional[ChatSession]] = reactive(None)
    contact: reactive[Optional[Contact]] = reactive(None)

    class SendMessage(Message):
        """Sent when user wants to send a message."""

        def __init__(self, content: str, contact_id: str) -> None:
            self.content = content
            self.contact_id = contact_id
            super().__init__()

    def __init__(self, *, id: Optional[str] = None, classes: Optional[str] = None) -> None:
        super().__init__(id=id, classes=classes)
        self._message_items: list[MessageItem] = []

    def compose(self) -> ComposeResult:
        """Compose the chat panel."""
        with Vertical(classes="header"):
            yield Static("", id="chat-title", classes="title")
            yield Static("", id="chat-subtitle", classes="subtitle")
        yield ScrollableContainer(id="message-container")

    def watch_session(self, session: Optional[ChatSession]) -> None:
        """Update display when session changes."""
        self._refresh_messages()

    def watch_contact(self, contact: Optional[Contact]) -> None:
        """Update header when contact changes."""
        self._update_header()

    def _update_header(self) -> None:
        """Update the header with contact info."""
        try:
            title = self.query_one("#chat-title", Static)
            subtitle = self.query_one("#chat-subtitle", Static)
        except Exception:
            return

        if self.contact:
            icon = "👥" if self.contact.is_chatroom else "👤"
            if self.contact.contact_type == ContactType.MP:
                icon = "📢"
            title.update(f"{icon} {self.contact.display_name}")

            # Subtitle with status
            if self.contact.is_chatroom:
                subtitle.update(f"{self.contact.member_count} 人")
            elif self.contact.signature:
                subtitle.update(self.contact.signature[:30])
            else:
                subtitle.update("")
        else:
            title.update("选择一个联系人开始聊天")
            subtitle.update("")

    def _refresh_messages(self) -> None:
        """Refresh the message list."""
        try:
            container = self.query_one("#message-container", ScrollableContainer)
        except Exception:
            return

        # Clear old messages
        container.remove_children()
        self._message_items.clear()

        if not self.session or not self.session.messages:
            container.mount(Static("暂无消息，发送消息开始聊天", classes="empty-chat"))
            return

        # Add messages
        for msg in self.session.messages[-100:]:  # Limit to last 100 messages
            item = MessageItem(msg, self.contact.display_name if self.contact else None)
            self._message_items.append(item)
            container.mount(item)

        # Scroll to bottom
        container.scroll_end(animate=False)

    def add_message(self, message: Message) -> None:
        """Add a new message to the display."""
        try:
            container = self.query_one("#message-container", ScrollableContainer)
        except Exception:
            return

        # Remove empty message placeholder if exists
        for child in container.children:
            if isinstance(child, Static) and "empty-chat" in child.classes:
                child.remove()
                break

        # Add new message
        item = MessageItem(message, self.contact.display_name if self.contact else None)
        self._message_items.append(item)
        container.mount(item)

        # Scroll to bottom
        container.scroll_end(animate=True)

    def set_session(self, session: ChatSession, contact: Contact) -> None:
        """Set the current chat session."""
        self.session = session
        self.contact = contact

    def clear(self) -> None:
        """Clear the chat panel."""
        self.session = None
        self.contact = None


# ContactType is imported at the top