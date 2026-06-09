"""Login screen for QR code display."""

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Static


class LoginScreen(Screen):
    """Screen for displaying QR code and login status."""

    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
    }

    LoginScreen Vertical {
        width: auto;
        height: auto;
        padding: 2;
        background: $surface;
        border: thick $primary;
    }

    LoginScreen .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    LoginScreen .qr-code {
        text-align: center;
        margin: 1 0;
    }

    LoginScreen .status {
        text-align: center;
        color: $text-muted;
    }

    LoginScreen .error {
        color: $error;
        text-style: bold;
    }

    LoginScreen .hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    LoginScreen StatusBar {
        dock: bottom;
    }
    """

    def __init__(self, qr_code: str = "", status: str = "正在获取登录二维码...") -> None:
        super().__init__()
        self.qr_code = qr_code
        self.status = status

    def compose(self) -> ComposeResult:
        """Compose the login screen."""
        from ..widgets.status_bar import StatusBar
        yield StatusBar()
        with Center():
            with Vertical():
                yield Static("🔐 微信登录", classes="title")
                yield Static(self.qr_code or "加载中...", id="qr-display", classes="qr-code")
                yield Static(self.status, id="login-status", classes="status")
                yield Static("请使用微信扫描二维码登录", classes="hint")

    def on_mount(self) -> None:
        """Start login when screen is mounted."""
        # Import here to avoid circular import
        app = self.app
        if hasattr(app, 'start_login'):
            app.start_login()

    def get_status_bar(self) -> "StatusBar":
        """Get the status bar widget."""
        from ..widgets.status_bar import StatusBar
        return self.query_one(StatusBar)

    def update_qr_code(self, qr_code: str) -> None:
        """Update the QR code display."""
        self.qr_code = qr_code
        try:
            display = self.query_one("#qr-display", Static)
            display.update(qr_code)
        except Exception:
            pass

    def update_status(self, status: str, is_error: bool = False) -> None:
        """Update the status text."""
        self.status = status
        try:
            status_widget = self.query_one("#login-status", Static)
            status_widget.update(status)
            status_widget.set_class(is_error, "error")
        except Exception:
            pass