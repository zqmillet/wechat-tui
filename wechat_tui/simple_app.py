"""Simple test app to verify TUI works."""

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Header, Static


class TestScreen(Screen):
    """Test screen."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Vertical(
                Static("微信 TUI 测试"),
                Static("按 Ctrl+Q 退出"),
            )
        )


class TestApp(App):
    """Test application."""

    BINDINGS = [("ctrl+q", "quit", "退出")]

    def on_mount(self) -> None:
        self.push_screen(TestScreen())


if __name__ == "__main__":
    app = TestApp()
    app.run()