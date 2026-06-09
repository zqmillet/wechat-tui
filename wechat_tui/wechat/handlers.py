"""Message handlers for different message types."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from ..models.message import Message, MessageType

logger = logging.getLogger(__name__)


class MessageHandler(ABC):
    """Base class for message handlers."""

    @abstractmethod
    def can_handle(self, message: Message) -> bool:
        """Check if this handler can handle the message."""
        pass

    @abstractmethod
    def handle(self, message: Message) -> Optional[str]:
        """Handle the message and optionally return a response."""
        pass


class TextHandler(MessageHandler):
    """Handler for text messages."""

    def __init__(
        self,
        auto_reply: bool = False,
        reply_handler: Optional[Callable[[str], Optional[str]]] = None,
    ):
        self.auto_reply = auto_reply
        self.reply_handler = reply_handler

    def can_handle(self, message: Message) -> bool:
        return message.msg_type == MessageType.TEXT

    def handle(self, message: Message) -> Optional[str]:
        if self.auto_reply and self.reply_handler:
            return self.reply_handler(message.content)
        return None


class ImageHandler(MessageHandler):
    """Handler for image messages."""

    def __init__(self, download_dir: Optional[Path] = None, auto_download: bool = False):
        self.download_dir = download_dir or Path("./downloads/images")
        self.auto_download = auto_download

    def can_handle(self, message: Message) -> bool:
        return message.msg_type == MessageType.IMAGE

    def handle(self, message: Message) -> Optional[str]:
        if self.auto_download and message.file_url:
            # TODO: Implement download
            logger.info(f"Would download image from {message.file_url}")
        return None


class FileHandler(MessageHandler):
    """Handler for file messages."""

    def __init__(self, download_dir: Optional[Path] = None, auto_download: bool = False):
        self.download_dir = download_dir or Path("./downloads/files")
        self.auto_download = auto_download

    def can_handle(self, message: Message) -> bool:
        return message.msg_type == MessageType.FILE

    def handle(self, message: Message) -> Optional[str]:
        if self.auto_download:
            logger.info(f"Would download file: {message.file_name}")
        return None


class SystemHandler(MessageHandler):
    """Handler for system messages."""

    def __init__(self, notification_callback: Optional[Callable[[str], None]] = None):
        self.notification_callback = notification_callback

    def can_handle(self, message: Message) -> bool:
        return message.msg_type == MessageType.SYSTEM

    def handle(self, message: Message) -> Optional[str]:
        if self.notification_callback:
            self.notification_callback(message.content)
        logger.info(f"System message: {message.content}")
        return None


class RecallHandler(MessageHandler):
    """Handler for message recall notifications."""

    def __init__(self, recall_callback: Optional[Callable[[str, str], None]] = None):
        self.recall_callback = recall_callback

    def can_handle(self, message: Message) -> bool:
        return message.msg_type == MessageType.RECALL

    def handle(self, message: Message) -> Optional[str]:
        # Parse recall content to get original message ID
        # TODO: Implement proper recall handling
        if self.recall_callback:
            self.recall_callback(message.sender_id, message.content)
        logger.info(f"Message recalled by {message.sender_id}")
        return None


class MessageDispatcher:
    """Dispatches messages to appropriate handlers."""

    def __init__(self):
        self.handlers: list[MessageHandler] = []

    def register(self, handler: MessageHandler) -> None:
        """Register a message handler."""
        self.handlers.append(handler)

    def dispatch(self, message: Message) -> Optional[str]:
        """Dispatch a message to the appropriate handler."""
        for handler in self.handlers:
            if handler.can_handle(message):
                try:
                    result = handler.handle(message)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.error(f"Handler {handler.__class__.__name__} error: {e}")
        return None


# Default handlers setup
def create_default_handlers() -> list[MessageHandler]:
    """Create default set of message handlers."""
    return [
        TextHandler(),
        ImageHandler(),
        FileHandler(),
        SystemHandler(),
        RecallHandler(),
    ]