"""Test Static widget with long text."""

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
        padding: 0 1;  /* 只左右 padding */
        color: #c9d1d9;
        background: #161b22;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Static("[友] Kinopico")
                yield Static("[友] 可爱的小导子")
                # 直接硬编码短名字测试
                yield Static("[友] AA保利金町湾")
                yield Static("[友] A大洋图文")
                # 更短的测试
                yield Static("[友] 测试")
                # 英文长名字
                yield Static("[友] ThisIsAVeryLongEng")
            with Vertical():
                yield Static("右侧区域")


if __name__ == "__main__":
    app = TestApp()
    app.run()