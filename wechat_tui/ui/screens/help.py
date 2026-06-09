"""Help screen showing keyboard shortcuts."""

from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Button


class HelpScreen(Screen):
    """Screen showing keyboard shortcuts and help."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen Vertical {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }

    HelpScreen .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }

    HelpScreen .section {
        margin-top: 1;
    }

    HelpScreen .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 0;
    }

    HelpScreen .shortcut {
        height: 1;
        margin: 0;
    }

    HelpScreen .key {
        color: $primary;
        text-style: bold;
        width: 20;
    }

    HelpScreen .description {
        color: $text;
    }

    HelpScreen .footer {
        margin-top: 1;
        padding-top: 1;
        border-top: solid $primary;
        text-align: center;
    }
    """

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Center():
            with Vertical():
                yield Static("⌨️ 键盘快捷键", classes="title")

                yield Static("导航", classes="section-title")
                yield self._shortcut("Tab", "在面板间切换焦点")
                yield self._shortcut("↑ / ↓", "在列表中导航")
                yield self._shortcut("Enter", "选择/确认")
                yield self._shortcut("Esc", "取消/返回")

                yield Static("聊天", classes="section-title section")
                yield self._shortcut("Enter", "发送消息")
                yield self._shortcut("Shift+Enter", "换行")
                yield self._shortcut("↑ / ↓", "浏览历史消息")

                yield Static("联系人", classes="section-title section")
                yield self._shortcut("Ctrl+R", "刷新联系人列表")
                yield self._shortcut("Ctrl+/", "搜索联系人")

                yield Static("应用", classes="section-title section")
                yield self._shortcut("Ctrl+Q", "退出应用")
                yield self._shortcut("Ctrl+H", "显示帮助")
                yield self._shortcut("Ctrl+L", "注销登录")

                with Horizontal(classes="footer"):
                    yield Button("关闭 (Esc)", id="close-btn")

    def _shortcut(self, key: str, description: str) -> Static:
        """Create a shortcut display row."""
        return Static(
            f"[bold]{key}[/bold]{' ' * (15 - len(key))}{description}",
            classes="shortcut",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close-btn":
            self.app.pop_screen()

    def on_key(self, event) -> None:
        """Handle key press."""
        if event.key == "escape":
            self.app.pop_screen()