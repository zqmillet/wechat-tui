"""Capture exact CSS errors."""

from textual.app import App
from textual.screen import Screen
from textual.widgets import Header, Static, Button, TextArea
from textual.containers import Container, Vertical, ScrollableContainer, Horizontal

# Manually recreate MainScreen with its CSS to find the error
class TestMainScreen(Screen):
    DEFAULT_CSS = """
    TestMainScreen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        grid-rows: 1fr auto;
    }

    TestMainScreen .left-panel {
        column: 1;
        row: 1;
    }

    TestMainScreen .right-panel {
        column: 2;
        row: 1;
        layout: vertical;
    }

    TestMainScreen .input-panel {
        column: 2;
        row: 2;
    }

    TestMainScreen Header {
        dock: top;
    }

    TestMainScreen StatusBar {
        dock: bottom;
    }
    """

    def compose(self):
        yield Header()
        yield Static("Status", classes="status-bar")
        with Container(classes="left-panel"):
            yield Static("Left")
        with Vertical(classes="right-panel"):
            yield Static("Right")
        with Container(classes="input-panel"):
            yield Static("Input")

class TestApp(App):
    async def on_mount(self):
        print("Mounted, pushing screen...")
        try:
            await self.push_screen(TestMainScreen())
            print("Screen pushed successfully!")
        except Exception as e:
            print(f"Error: {e}")
            # Print the error object details
            if hasattr(e, '__str__'):
                print(f"Error string: {str(e)}")
        self.exit()

print("Running test...")
app = TestApp()
app.run(headless=True)
print("Done")