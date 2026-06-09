"""Test Button display in Textual."""

from textual.app import App, ComposeResult
from textual.widgets import Button


class TestApp(App):
    def compose(self) -> ComposeResult:
        yield Button("测试按钮")
        yield Button(label="好友名称测试")


if __name__ == "__main__":
    app = TestApp()
    app.run()