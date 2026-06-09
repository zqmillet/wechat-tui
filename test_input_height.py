"""Test Input height."""

from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.containers import Vertical


class TestApp(App):
    CSS = """
    Vertical {
        width: 30;
        background: #161b22;
    }

    /* 测试不同的 Input 样式 */
    Input {
        width: 100%;
        background: #0d1117;
        border: none;
        padding: 0;
        color: #c9d1d9;
    }

    /* 强制最小和最大高度 */
    Input {
        height: 1;
        min-height: 1;
        max-height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="🔍 搜索")
            yield Input(placeholder="第二行")


if __name__ == "__main__":
    app = TestApp()
    app.run()