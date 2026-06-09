"""WeChat client wrapper using wxpy."""

import html
import logging
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import pyqrcode

from ..models.contact import Contact, ContactList, ContactType
from ..models.message import ChatSession, Message, MessageType
from ..database import DatabaseManager
from ..utils.config import AppConfig
from ..utils.image_downloader import ImageDownloader

logger = logging.getLogger(__name__)

# Import wxpy
from wxpy import Bot

# Fix itchat Python 3.9+ compatibility
import itchat.utils as itchat_utils
itchat_utils.htmlParser.unescape = lambda s: html.unescape(s)


class ClientState(Enum):
    """State of the WeChat client."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    LOGGING_IN = "logging in"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class WeChatClient:
    """WeChat client that wraps wxpy for TUI usage."""

    state: ClientState = ClientState.DISCONNECTED
    contact_list: ContactList = field(default_factory=ContactList)
    chat_sessions: dict[str, ChatSession] = field(default_factory=dict)
    db: DatabaseManager = field(default_factory=DatabaseManager)

    # Callbacks
    on_message: Optional[Callable[[Message], None]] = None
    on_state_change: Optional[Callable[[ClientState], None]] = None
    on_contact_update: Optional[Callable[[Contact], None]] = None
    on_login: Optional[Callable[[dict], None]] = None
    on_logout: Optional[Callable[[], None]] = None
    on_qr_update: Optional[Callable[[str], None]] = None

    # Current user info
    user_id: Optional[str] = None
    user_name: Optional[str] = None

    # Internal state
    _logged_in: bool = False
    _bot: Optional[Bot] = None
    _qr_callback_internal: Optional[Callable] = None
    _config: Optional[AppConfig] = None
    _image_downloader: Optional[ImageDownloader] = None

    def __post_init__(self) -> None:
        """Initialize config and image downloader."""
        self._config = AppConfig()
        self._image_downloader = ImageDownloader(self._config.image_dir)

    def _set_state(self, state: ClientState) -> None:
        """Update client state and notify."""
        self.state = state
        logger.info(f"State changed to: {state}")
        if self.on_state_change:
            self.on_state_change(state)

    def login(self, hot_reload: bool = True, status_storage_dir: str = ".wechat") -> bool:
        """Login to WeChat with QR code using wxpy.

        Args:
            hot_reload: Enable hot reload to avoid scanning QR every time
            status_storage_dir: Directory to store login status

        Returns:
            True if login successful
        """
        self._set_state(ClientState.CONNECTING)

        try:
            logger.info("Starting wxpy login...")

            # Create internal QR callback that will be called by wxpy
            def internal_qr_callback(uuid, status, qrcode):
                logger.info(f"wypy qr_callback: uuid={uuid}, status={status}, qrcode_size={len(qrcode) if qrcode else 0}")

                if status == '0':
                    # Generate ASCII QR
                    url = f"https://login.weixin.qq.com/l/{uuid}"
                    qr = pyqrcode.create(url)
                    qr_text = qr.text()
                    self._set_state(ClientState.LOGGING_IN)
                    if self.on_qr_update:
                        self.on_qr_update(qr_text)
                elif status == '201':
                    logger.info("User scanned QR code")
                    if self.on_qr_update:
                        self.on_qr_update("已扫码，请在手机上确认登录...")
                elif status == '200':
                    logger.info("Login confirmed (status 200)")
                    self._set_state(ClientState.CONNECTED)
                elif status == '400':
                    logger.error("Login failed (status 400)")
                    self._set_state(ClientState.ERROR)
                    if self.on_qr_update:
                        self.on_qr_update("❌ 登录失败：账号可能被限制")

            self._qr_callback_internal = internal_qr_callback

            # 使用持久化缓存路径
            cache_path = os.path.expanduser("~/.wechat-tui/wxpy_cache.pkl")

            # wxpy Bot blocks until login completes
            self._bot = Bot(
                cache_path=cache_path,  # Enable login cache with persistent path
                console_qr=False,  # Don't use console QR, use our callback
                qr_callback=internal_qr_callback,
                login_callback=None,
                logout_callback=self._on_logout_callback,
            )

            self._logged_in = True

            # Get user info from wxpy bot
            self.user_name = self._bot.self.name if self._bot.self else 'Unknown'
            self.user_id = self._bot.self.user_name if self._bot.self else None

            logger.info(f"wxpy login successful: {self.user_name}")

            # Load contacts
            self._load_contacts()

            # Register message handler to receive incoming messages
            self.register_message_handler()

            if self.on_login:
                self.on_login({'NickName': self.user_name, 'UserName': self.user_id})

            return True

        except Exception as e:
            import traceback
            logger.error(f"Login failed: {e}")
            logger.error(traceback.format_exc())
            self._set_state(ClientState.ERROR)
            if self.on_qr_update:
                self.on_qr_update(f"登录失败: {e}")
            return False

    def _on_logout_callback(self) -> None:
        """Called when wxpy logout."""
        logger.info("wxpy logout callback triggered")
        self._logged_in = False
        self._set_state(ClientState.DISCONNECTED)
        if self.on_logout:
            self.on_logout()

    def _load_contacts(self) -> None:
        """Load contacts from wxpy bot."""
        if not self._bot:
            return

        try:
            import html
            # Load friends
            friends = self._bot.friends(update=True)
            for friend in friends:
                # 优先使用备注名 (remark_name)，然后是昵称，最后是 user_name
                # 确保不使用空字符串
                name = (
                    friend.remark_name or
                    friend.nick_name or
                    getattr(friend, 'name', None) or
                    friend.user_name or
                    "未知好友"
                )
                # Decode HTML entities (e.g. &amp; -> &)
                name = html.unescape(str(name))
                # 确保名字不为空
                if not name or name.strip() == "":
                    name = friend.user_name[:20] if friend.user_name else "未知好友"
                contact = Contact(
                    user_id=friend.user_name,
                    name=name,
                    contact_type=ContactType.USER,
                    avatar_url=friend.avatar_url if hasattr(friend, 'avatar_url') else None,
                    signature=friend.signature if hasattr(friend, 'signature') else None,
                    gender=friend.sex if hasattr(friend, 'sex') else 0,
                )
                self.contact_list.add(contact)

            logger.info(f"Loaded {len(self.contact_list.all_users())} friends")

            # Load groups
            groups = self._bot.groups(update=True)
            for group in groups:
                # Decode HTML entities in group name (e.g. &amp; -> &)
                import html
                group_name = html.unescape(group.name or group.user_name)
                # Get member count properly (members.count is a method in wxpy)
                try:
                    member_count = len(group.members) if hasattr(group, 'members') else 0
                except Exception:
                    member_count = 0
                contact = Contact(
                    user_id=group.user_name,
                    name=group_name,
                    contact_type=ContactType.CHATROOM,
                    member_count=member_count,
                )
                self.contact_list.add(contact)

            logger.info(f"Loaded {len(self.contact_list.all_chatrooms())} groups")

        except Exception as e:
            logger.error(f"Error loading contacts: {e}")

    def send_text(self, to_user_id: str, text: str) -> bool:
        """Send text message to a contact."""
        if not self._logged_in or not self._bot:
            logger.error("Not logged in")
            return False

        try:
            # Find the target chat
            target = None

            # Search in friends
            for friend in self._bot.friends():
                if friend.user_name == to_user_id:
                    target = friend
                    break

            # Search in groups if not found
            if not target:
                for group in self._bot.groups():
                    if group.user_name == to_user_id:
                        target = group
                        break

            if target:
                target.send(text)
                logger.debug(f"Sent message to {target.name}")

                from time import time
                ts = time()
                msg_id = f"local_{ts}"
                chat_id = to_user_id

                # Add to local chat session
                session = self.get_chat_session(to_user_id)
                msg = Message(
                    msg_id=msg_id,
                    sender_id=self.user_id or "",
                    receiver_id=to_user_id,
                    msg_type=MessageType.TEXT,
                    content=text,
                    timestamp=ts,
                    is_sent=True,
                )
                session.add_message(msg)

                # Persist to database with names
                self.db.save_message(
                    msg_id=msg_id,
                    chat_id=chat_id,
                    sender_id=self.user_id or "",
                    receiver_id=to_user_id,
                    msg_type=MessageType.TEXT,
                    content=text,
                    timestamp=ts,
                    is_sent=True,
                    sender_name=self.user_name,
                    receiver_name=target.name,
                )
                self.db.save_session(chat_id, session.unread_count, ts)
                return True
            else:
                logger.error(f"Target not found: {to_user_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def get_chat_session(self, contact_id: str) -> ChatSession:
        """Get or create chat session for a contact."""
        if contact_id not in self.chat_sessions:
            self.chat_sessions[contact_id] = ChatSession(contact_id=contact_id)
        return self.chat_sessions[contact_id]

    def register_message_handler(self) -> None:
        """Register message handler with wxpy."""
        if not self._bot:
            return

        from wxpy import TEXT, PICTURE, VIDEO, ATTACHMENT

        @self._bot.register(msg_types=[TEXT, PICTURE, VIDEO, ATTACHMENT])
        def handle_wxpy_message(msg):
            """Handle incoming messages from wxpy."""
            logger.info(f"Received message: {msg.type} from {msg.sender.name}")

            try:
                # Convert to our Message format
                msg_type_map = {
                    'Text': MessageType.TEXT,
                    'Picture': MessageType.IMAGE,
                    'Video': MessageType.VIDEO,
                    'Attachment': MessageType.FILE,
                }

                # Determine if message is sent by us
                is_sent = msg.sender == self._bot.self

                sender_name = msg.sender.name if hasattr(msg, 'sender') and msg.sender else None
                receiver_name = msg.receiver.name if hasattr(msg, 'receiver') and msg.receiver else self.user_name

                # Download image if it's a Picture message
                local_file_path = None
                file_url = None
                file_name = None
                file_size = None

                if msg.type == 'Picture' and self._config.auto_download_images:
                    try:
                        chat_id_temp = msg.sender.user_name if not is_sent else msg.receiver.user_name
                        timestamp_temp = msg.create_time.timestamp() if hasattr(msg, 'create_time') else 0
                        msg_id_temp = str(msg.id) if hasattr(msg, 'id') else f"wxpy_{int(timestamp_temp)}"

                        logger.info(f"Downloading image: chat_id={chat_id_temp}, msg_id={msg_id_temp}")
                        local_file_path = self._image_downloader.download_image(
                            msg, chat_id_temp, timestamp_temp, msg_id_temp
                        )

                        # Get file metadata from wxpy message
                        file_name = getattr(msg, 'file_name', None)
                        file_size = getattr(msg, 'file_size', None)

                        logger.info(f"Image download result: local_path={local_file_path}")

                    except Exception as e:
                        logger.error(f"Image download failed: {e}", exc_info=True)

                our_msg = Message(
                    msg_id=str(msg.id) if hasattr(msg, 'id') else f"wxpy_{int(msg.create_time.timestamp() if hasattr(msg, 'create_time') else 0)}",
                    sender_id=msg.sender.user_name,
                    receiver_id=msg.receiver.user_name if hasattr(msg, 'receiver') else self.user_id,
                    msg_type=msg_type_map.get(msg.type, MessageType.TEXT),
                    content=msg.text if hasattr(msg, 'text') else str(msg),
                    timestamp=msg.create_time.timestamp() if hasattr(msg, 'create_time') else 0,
                    is_sent=is_sent,
                    actual_sender_name=msg.sender.name if not is_sent else None,
                    file_url=file_url,
                    file_name=file_name,
                    file_size=file_size,
                    local_file_path=local_file_path,
                )

                # Add to session
                chat_id = our_msg.chat_id
                logger.info(f"Message chat_id: {chat_id}")
                session = self.get_chat_session(chat_id)
                session.add_message(our_msg)
                logger.info(f"Added message to session, total messages: {len(session.messages)}")

                # Persist to database with names
                self.db.save_message(
                    msg_id=our_msg.msg_id,
                    chat_id=chat_id,
                    sender_id=our_msg.sender_id,
                    receiver_id=our_msg.receiver_id,
                    msg_type=our_msg.msg_type,
                    content=our_msg.content,
                    timestamp=our_msg.timestamp,
                    is_sent=our_msg.is_sent,
                    sender_name=sender_name,
                    receiver_name=receiver_name,
                    actual_sender_name=our_msg.actual_sender_name,
                    file_url=file_url,
                    file_name=file_name,
                    file_size=file_size,
                    local_file_path=local_file_path,
                )
                self.db.save_session(chat_id, session.unread_count, our_msg.timestamp)

                # Notify callback
                if self.on_message:
                    logger.info(f"Calling on_message callback")
                    self.on_message(our_msg)
                else:
                    logger.warning("on_message callback not set")

            except Exception as e:
                import traceback
                logger.error(f"Error processing message: {e}")
                logger.error(traceback.format_exc())

        logger.info("Message handler registered with wxpy")

    def logout(self) -> None:
        """Logout from WeChat."""
        if self._bot:
            try:
                self._bot.logout()
            except Exception as e:
                logger.error(f"Logout error: {e}")

        self._logged_in = False
        self._bot = None

        # Close database connection
        if self.db:
            self.db.close()

        self._set_state(ClientState.DISCONNECTED)
        logger.info("Logged out")

    def __enter__(self) -> "WeChatClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.logout()