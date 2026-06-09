"""Main TUI application for WeChat."""

import logging
import threading
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Header, Static

from .models.contact import Contact
from .models.message import ChatSession, Message
from .wechat.client import ClientState, WeChatClient
from .ui.widgets.contact_list import ContactList
from .ui.widgets.chat_panel import ChatPanel
from .ui.widgets.input_box import InputBox
from .ui.widgets.status_bar import StatusBar
from .ui.screens.help import HelpScreen

logger = logging.getLogger(__name__)


class LoginScreen(Screen):
    """Screen for displaying QR code and login status."""

    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
        background: #1a1a2e;
    }

    LoginScreen .container {
        width: 50;
        height: auto;
        padding: 2;
        background: #16213e;
        border: round #0f3460;
    }

    LoginScreen .title {
        text-align: center;
        text-style: bold;
        color: #e94560;
        margin-bottom: 1;
    }

    LoginScreen .qr-code {
        text-align: center;
        padding: 1;
        color: white;
        background: #0f0f0f;
        height: auto;
    }

    LoginScreen .status {
        text-align: center;
        color: #a7a7a7;
        margin-top: 1;
    }

    LoginScreen .error {
        color: #e94560;
        text-style: bold;
    }

    LoginScreen .hint {
        text-align: center;
        color: #5c5c5c;
        margin-top: 1;
    }
    """

    status_text: reactive[str] = reactive("正在准备登录...")

    def compose(self) -> ComposeResult:
        yield StatusBar(id="login-status-bar")
        yield Container(
            Static("💬 微信 TUI", classes="title"),
            Static("等待二维码...", id="qr-display", classes="qr-code"),
            Static(self.status_text, id="login-status", classes="status"),
            Static("请扫描二维码登录", classes="hint"),
            classes="container",
        )

    def on_mount(self) -> None:
        """Update status bar on mount."""
        app = self.app
        if hasattr(app, 'state'):
            self.query_one("#login-status-bar", StatusBar).state = app.state
            self.query_one("#login-status-bar", StatusBar).user_name = app.user_name
            self.query_one("#login-status-bar", StatusBar).message_count = app.message_count

    def update_status(self, status: str, is_error: bool = False) -> None:
        """Update the status text."""
        self.status_text = status
        try:
            status_widget = self.query_one("#login-status", Static)
            status_widget.update(status)
            status_widget.set_class(is_error, "error")
        except Exception:
            pass

    def update_qr(self, qr_text: str) -> None:
        """Update QR code display - compact version."""
        try:
            qr_widget = self.query_one("#qr-display", Static)
            lines = qr_text.strip().split('\n')
            # Merge every 2 lines to reduce height by half
            formatted_lines = []
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    # Combine two rows using half-block characters
                    combined = ""
                    for j in range(len(lines[i])):
                        top = lines[i][j] if j < len(lines[i]) else '0'
                        bot = lines[i+1][j] if j < len(lines[i+1]) else '0'
                        # Use Unicode half-blocks: ▀ (top half), ▄ (bottom half), █ (full), space (none)
                        if top == '1' and bot == '1':
                            combined += "█"
                        elif top == '1' and bot == '0':
                            combined += "▀"
                        elif top == '0' and bot == '1':
                            combined += "▄"
                        else:
                            combined += " "
                    formatted_lines.append(combined)
                else:
                    # Last single row - use top half blocks
                    line = lines[i]
                    formatted_line = ""
                    for char in line:
                        if char == '1':
                            formatted_line += "▀"
                        else:
                            formatted_line += " "
                    formatted_lines.append(formatted_line)
            formatted_qr = "\n".join(formatted_lines)
            qr_widget.update(formatted_qr)
        except Exception as e:
            logger.error(f"QR update error: {e}")


class MainScreen(Screen):
    """Main chat screen - WeChat style layout."""

    DEFAULT_CSS = """
    MainScreen {
        layout: horizontal;
        background: #0d1117;
    }

    MainScreen #sidebar {
        width: 30;
        min-width: 25;
        dock: left;
        background: #161b22;
        border-right: solid #30363d;
    }

    MainScreen #chat-area {
        width: 1fr;
        layout: vertical;
        background: #0d1117;
    }

    MainScreen #chat-header {
        height: 2;
        background: #161b22;
        padding: 0 1;
        border-bottom: solid #30363d;
        color: #c9d1d9;
    }

    MainScreen #messages-area {
        height: 1fr;
        background: #0d1117;
    }

    MainScreen #input-area {
        height: auto;
        min-height: 3;
        background: #161b22;
        border-top: solid #30363d;
    }

    MainScreen StatusBar {
        dock: bottom;
        background: #161b22;
    }
    """

    BINDINGS = [
        Binding("ctrl+r", "refresh_contacts", "刷新"),
        Binding("ctrl+h", "help", "帮助"),
        Binding("tab", "focus_next", "切换焦点"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._selected_contact: Optional[Contact] = None

    def compose(self) -> ComposeResult:
        # Sidebar (contact list)
        with Container(id="sidebar"):
            yield ContactList(id="contact-list")
        # Main chat area
        with Container(id="chat-area"):
            yield Static("选择联系人开始聊天", id="chat-header")
            with Container(id="messages-area"):
                yield ChatPanel(id="chat-panel")
            with Container(id="input-area"):
                yield InputBox(id="input-box")
        yield StatusBar(id="main-status-bar")

    def on_mount(self) -> None:
        """Set up initial state."""
        # Focus on contact list first
        self.query_one("#contact-list", ContactList).focus()
        # Update status bar
        app = self.app
        if hasattr(app, 'state'):
            self.query_one("#main-status-bar", StatusBar).state = app.state
            self.query_one("#main-status-bar", StatusBar).user_name = app.user_name
            self.query_one("#main-status-bar", StatusBar).message_count = app.message_count

    def _update_chat_header(self, contact: Contact) -> None:
        """Update chat header with contact name."""
        header = self.query_one("#chat-header", Static)
        icon = "👥" if contact.is_chatroom else "👤"
        header.update(f"{icon} {contact.display_name}")

    def action_refresh_contacts(self) -> None:
        """Refresh the contact list."""
        app = self.app
        if hasattr(app, "refresh_contacts") and app.client:
            app.refresh_contacts()

    def action_help(self) -> None:
        """Show help screen."""
        self.app.push_screen(HelpScreen())

    def action_focus_next(self) -> None:
        """Cycle focus between panels."""
        # Simple focus cycling
        try:
            input_box = self.query_one("#input-box", InputBox)
            contact_list = self.query_one("#contact-list", ContactList)
            if self.focused == contact_list:
                input_box.focus_input()
            else:
                contact_list.focus()
        except Exception:
            pass

    def on_contact_list_contact_selected(self, event: ContactList.ContactSelected) -> None:
        """Handle contact selection."""
        try:
            self._selected_contact = event.contact
            app = self.app

            # Update header
            self._update_chat_header(event.contact)

            if hasattr(app, "client") and app.client:
                # 从数据库加载历史消息（通过联系人名字）
                session = ChatSession(contact_id=event.contact.user_id)

                # 尝试从数据库加载消息
                try:
                    messages_data = app.client.db.load_messages_by_name(event.contact.display_name, limit=50)
                    if messages_data:
                        for msg_data in messages_data:
                            msg = Message(
                                msg_id=msg_data["msg_id"],
                                sender_id=msg_data["sender_id"],
                                receiver_id=msg_data["receiver_id"],
                                msg_type=msg_data["msg_type"],
                                content=msg_data["content"],
                                timestamp=msg_data["timestamp"],
                                is_sent=msg_data["is_sent"],
                                is_read=msg_data["is_read"],
                                actual_sender_name=msg_data["actual_sender_name"],
                            )
                            session.add_message(msg)
                except Exception as e:
                    logger.error(f"Error loading messages: {e}")

                # 存储到 client 的 sessions
                app.client.chat_sessions[event.contact.user_id] = session

                self.query_one("#chat-panel", ChatPanel).set_session(session, event.contact)
                self.query_one("#input-box", InputBox).enabled = True
                self.query_one("#input-box", InputBox).focus_input()
        except Exception as e:
            logger.error(f"Error handling contact selection: {e}")

    def on_input_box_submit(self, event: InputBox.Submit) -> None:
        """Handle message submission."""
        if self._selected_contact:
            app = self.app
            if hasattr(app, "client") and app.client:
                success = app.client.send_text(self._selected_contact.user_id, event.content)
                if success:
                    # Get the message that was just added
                    session = app.client.get_chat_session(self._selected_contact.user_id)
                    if session and session.last_message:
                        # Add the message directly to the panel
                        self.query_one("#chat-panel", ChatPanel).add_message(session.last_message)
                else:
                    self.notify("发送失败", severity="error")

    def update_contacts(self, contacts: list[Contact]) -> None:
        """Update the contact list."""
        self.query_one("#contact-list", ContactList).contacts = contacts

    def add_message(self, message: Message) -> None:
        """Add a new message to the display."""
        chat_panel = self.query_one("#chat-panel", ChatPanel)

        logger.info(f"MainScreen.add_message: chat_id={message.chat_id}, selected={self._selected_contact.user_id if self._selected_contact else 'None'}")

        if self._selected_contact and message.chat_id == self._selected_contact.user_id:
            chat_panel.add_message(message)
            logger.info("Message added to chat panel")
        else:
            logger.info("Message not for current chat, skipped")


class WeChatApp(App):
    """Main WeChat TUI application."""

    CSS = """
    Screen {
        background: #1a1a2e;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "退出"),
        Binding("ctrl+l", "logout", "注销"),
    ]

    client: Optional[WeChatClient] = None
    state: reactive[ClientState] = reactive(ClientState.DISCONNECTED)
    user_name: reactive[str] = reactive("")
    message_count: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._client_thread: Optional[threading.Thread] = None

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen(LoginScreen())
        # Start login in a moment
        self.set_timer(0.5, self._start_login)

    def _start_login(self) -> None:
        """Start the WeChat login process."""
        self.client = WeChatClient()

        # Set up callbacks using reactive updates
        def on_state(state: ClientState) -> None:
            self.state = state
            # Update all status bars
            self.call_from_thread(self._update_status_bars)
            if state == ClientState.CONNECTED:
                self.call_from_thread(self._switch_to_main)

        def on_login(info: dict) -> None:
            self.user_name = info.get("NickName", "")

        def on_msg(msg: Message) -> None:
            self.message_count += 1
            # Update UI with new message
            self.call_from_thread(self._handle_new_message, msg)

        def on_qr(qr_text: str) -> None:
            """Update QR code display."""
            self._update_qr_code(qr_text)

        self.client.on_state_change = on_state
        self.client.on_login = on_login
        self.client.on_message = on_msg
        self.client.on_qr_update = on_qr

        # Run login in background thread
        self._client_thread = threading.Thread(target=self._login_thread, daemon=True)
        self._client_thread.start()

    def _update_qr_code(self, qr_text: str) -> None:
        """Update QR code in login screen."""
        logger.info(f"_update_qr_code called, length={len(qr_text)}")
        login_screen = self.screen
        if isinstance(login_screen, LoginScreen):
            logger.info("Found LoginScreen, calling update_qr")
            # Call from thread safely - use a single call
            self.call_from_thread(self._do_update_qr, qr_text)
        else:
            logger.warning(f"Current screen is {type(login_screen)}, not LoginScreen")

    def _do_update_qr(self, qr_text: str) -> None:
        """Actually update QR code (called from main thread)."""
        logger.info(f"_do_update_qr executing, length={len(qr_text)}")
        login_screen = self.screen
        if isinstance(login_screen, LoginScreen):
            login_screen.update_qr(qr_text)
            login_screen.update_status("请扫描二维码登录")
            logger.info("QR code displayed successfully")

    def _login_thread(self) -> None:
        """Thread for login."""
        try:
            success = self.client.login(hot_reload=False)
            if success:
                logger.info("Login success, switching to main screen")
                self.call_from_thread(self._switch_to_main)
            else:
                logger.error("Login returned False")
        except Exception as e:
            logger.error(f"Login error: {e}")
            login_screen = self.screen
            if isinstance(login_screen, LoginScreen):
                self.call_from_thread(login_screen.update_status, f"登录失败: {e}", True)

    def _switch_to_main(self) -> None:
        """Switch to main screen."""
        self.push_screen(MainScreen())
        if self.client:
            # Get all contacts (friends + groups)
            all_contacts = list(self.client.contact_list.contacts.values())
            logger.info(f"Loaded {len(all_contacts)} total contacts")
            logger.info(f"  - Users: {len(self.client.contact_list.all_users())}")
            logger.info(f"  - Groups: {len(self.client.contact_list.all_chatrooms())}")

            # Sort by recent chat time using contact name (not user_id)
            # because wxpy uses different IDs for messages and contacts
            def get_last_message_time(contact: Contact) -> float:
                """Get last message time for a contact by name."""
                result = self.client.db.get_last_message_time_by_name(contact.display_name)
                return result

            # Sort: recent chats first, then alphabetically for those without history
            all_contacts.sort(key=lambda c: (
                -get_last_message_time(c),  # Negative for descending (recent first)
                c.display_name.lower()       # Alphabetical as secondary sort
            ))

            # Log top contacts with their times
            logger.info("Top 10 contacts after sorting:")
            for i, c in enumerate(all_contacts[:10]):
                last_time = get_last_message_time(c)
                logger.info(f"  {i+1}. {c.display_name} (last_time={last_time})")

            # Show all contacts
            self.screen.update_contacts(all_contacts)

    def refresh_contacts(self) -> None:
        """Refresh contacts."""
        if self.client:
            self.client._load_contacts()
            contacts = self.client.contact_list.get_recent(30)
            if isinstance(self.screen, MainScreen):
                self.screen.update_contacts(contacts)
            self.notify("联系人已刷新")

    def action_logout(self) -> None:
        """Logout."""
        if self.client:
            self.client.logout()
            self.client = None
        self.pop_screen()
        self.state = ClientState.DISCONNECTED
        self.user_name = ""
        self.message_count = 0

    def on_unmount(self) -> None:
        """Clean up."""
        if self.client:
            self.client.logout()

    def _handle_new_message(self, msg: Message) -> None:
        """Handle new message and update UI."""
        logger.info(f"_handle_new_message: chat_id={msg.chat_id}, is_sent={msg.is_sent}")
        if isinstance(self.screen, MainScreen):
            self.screen.add_message(msg)

    def _update_status_bars(self) -> None:
        """Update all status bars with current state."""
        try:
            # Check if we have screens on stack
            if not self._screen_stack:
                return
            screen = self.screen
            if isinstance(screen, LoginScreen):
                bar = screen.query_one("#login-status-bar", StatusBar)
                bar.state = self.state
                bar.user_name = self.user_name
                bar.message_count = self.message_count
            elif isinstance(screen, MainScreen):
                bar = screen.query_one("#main-status-bar", StatusBar)
                bar.state = self.state
                bar.user_name = self.user_name
                bar.message_count = self.message_count
        except Exception:
            pass
        if isinstance(self.screen, MainScreen):
            self.screen.add_message(msg)


def run_app() -> None:
    """Entry point."""
    app = WeChatApp()
    app.run()