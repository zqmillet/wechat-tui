"""Simple test for Static widget."""

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Container


class TestApp(App):
    CSS = """
    Container {
        layout: horizontal;
    }
    Vertical {
        width: 30;
        background: #161b22;
    }
    Static {
        height: 2;
        padding: 0 1;
        color: #c9d1d9;
        background: #161b22;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                # 测试不同情况
                yield Static("123456789012345678901234567890")  # 30 ASCII
                yield Static("一二三四五六七八九十")  # 10 Chinese
                yield Static("一二三四五六七八九十十一十二")  # 12 Chinese
                yield Static("AA保利")  # 混合短
                yield Static("AA保利金町湾")  # 混合
                yield Static("AA保利金町湾一线")  # 混合更长
                yield Static("[友] Kinopico")  # 带前缀短
                yield Static("[友] AA保利")  # 带前缀混合短
                yield Static("[友] A大洋图文")  # 带前缀混合
            with Vertical():
                yield Static("右侧")


if __name__ == "__main__":
    app = TestApp()
    app.run()