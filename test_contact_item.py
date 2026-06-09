"""Test ContactItem display."""

from textual.app import App, ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical


class TestApp(App):
    CSS = """
    Button {
        height: 2;
        color: red;
        background: blue;
    }

    Static {
        height: 2;
        color: green;
        background: yellow;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Button("Button 测试文字")
            yield Static("Static 测试文字")


if __name__ == "__main__":
    app = TestApp()
    app.run()