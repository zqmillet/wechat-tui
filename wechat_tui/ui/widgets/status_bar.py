"""Status bar widget showing connection and user status."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...wechat.client import ClientState


class StatusBar(Widget):
    """Status bar at the bottom of the application."""

    DEFAULT_CSS = """
    StatusBar {
        width: 100%;
        height: 1;
        background: #161b22;
        color: #8b949e;
        dock: bottom;
    }

    StatusBar Horizontal {
        width: 100%;
        height: 1;
    }

    StatusBar .left {
        width: 1fr;
        content-align: left middle;
        padding: 0 1;
    }

    StatusBar .right {
        width: auto;
        content-align: right middle;
        padding: 0 1;
    }

    StatusBar .connected {
        color: #3fb950;
    }

    StatusBar .disconnected {
        color: #f85149;
    }

    StatusBar .connecting {
        color: #d29922;
    }

    StatusBar .error {
        color: #f85149;
        text-style: bold;
    }
    """

    state: reactive[ClientState] = reactive(ClientState.DISCONNECTED)
    user_name: reactive[str] = reactive("")
    message_count: reactive[int] = reactive(0)

    def __init__(self, *, id: Optional[str] = None, classes: Optional[str] = None) -> None:
        super().__init__(id=id, classes=classes)

    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        with Horizontal():
            yield Static("", id="status-left", classes="left")
            yield Static("", id="status-right", classes="right")

    def on_mount(self) -> None:
        """Update display on mount."""
        self._update_display()

    def watch_state(self, state: ClientState) -> None:
        """Update display when state changes."""
        self._update_display()

    def watch_user_name(self, name: str) -> None:
        """Update display when user name changes."""
        self._update_display()

    def watch_message_count(self, count: int) -> None:
        """Update display when message count changes."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the status bar display."""
        try:
            left = self.query_one("#status-left", Static)
            right = self.query_one("#status-right", Static)
        except Exception:
            return

        # Status icon and text
        status_map = {
            ClientState.DISCONNECTED: ("●", "disconnected", "未连接"),
            ClientState.CONNECTING: ("●", "connecting", "连接中..."),
            ClientState.LOGGING_IN: ("●", "connecting", "登录中..."),
            ClientState.CONNECTED: ("●", "connected", "已连接"),
            ClientState.ERROR: ("✗", "error", "连接错误"),
        }

        icon, css_class, text = status_map.get(self.state, ("?", "", "未知"))

        if self.user_name and self.state == ClientState.CONNECTED:
            left_text = f"{icon} {text} · {self.user_name}"
        else:
            left_text = f"{icon} {text}"

        left.update(left_text)
        left.set_class(True, css_class)

        # Right side: message count and help
        right_text = f"消息: {self.message_count} | Ctrl+Q 退出 | Ctrl+/ 帮助"
        right.update(right_text)