"""Test grid layout CSS."""

from textual.app import App
from textual.screen import Screen
from textual.widgets import Header, Static
from textual.containers import Container, Vertical

# Test minimal grid layout
class TestScreen1(Screen):
    # No grid - just basic
    def compose(self):
        yield Header()
        yield Static("Test")

class TestScreen2(Screen):
    DEFAULT_CSS = """
    TestScreen2 {
        layout: grid;
        grid-size: 2;
    }
    """
    def compose(self):
        yield Static("A")
        yield Static("B")

class TestScreen3(Screen):
    DEFAULT_CSS = """
    TestScreen3 {
        layout: grid;
        grid-size: 2 2;
    }
    """
    def compose(self):
        yield Static("A")
        yield Static("B")
        yield Static("C")
        yield Static("D")

class TestScreen4(Screen):
    DEFAULT_CSS = """
    TestScreen4 {
        layout: grid;
        grid-columns: 1fr 2fr;
        grid-rows: 1fr auto;
    }
    """
    def compose(self):
        yield Static("A")
        yield Static("B")

class TestScreen5(Screen):
    DEFAULT_CSS = """
    TestScreen5 .left-panel {
        column: 1;
    }
    """
    def compose(self):
        with Container(classes="left-panel"):
            yield Static("Left")

class TestApp(App):
    async def on_mount(self):
        tests = [
            ("TestScreen1 (no grid)", TestScreen1),
            ("TestScreen2 (grid-size 2)", TestScreen2),
            ("TestScreen3 (grid-size 2x2)", TestScreen3),
            ("TestScreen4 (grid-columns/rows)", TestScreen4),
            ("TestScreen5 (column selector)", TestScreen5),
        ]

        for name, screen_cls in tests:
            try:
                await self.push_screen(screen_cls())
                print(f"{name}: OK")
                self.pop_screen()
            except Exception as e:
                print(f"{name}: FAILED - {e}")

        self.exit()

print("Testing CSS layouts...")
app = TestApp()
app.run(headless=True)
print("Done")