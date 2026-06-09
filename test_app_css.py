"""Test full app CSS."""

import asyncio
from textual.app import App
from textual.screen import Screen
from textual.widgets import Header, Static

# Minimal test app
class TestScreen(Screen):
    def compose(self):
        yield Header()
        yield Static("Test")

class TestApp(App):
    async def on_mount(self):
        print("App mounted successfully!")
        self.exit()

app = TestApp()
print("Testing minimal app...")
app.run(headless=True)
print("Minimal app works!")

# Now test with our actual app's CSS
from wechat_tui.app import WeChatApp
print("\nTesting WeChatApp CSS...")
test_app = WeChatApp()
print("WeChatApp created successfully!")
print("CSS:", test_app.CSS if hasattr(test_app, 'CSS') else "No CSS")