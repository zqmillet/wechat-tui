"""Test MainScreen push."""

from textual.app import App

class TestApp(App):
    async def on_mount(self):
        print("App mounted, now importing MainScreen...")
        from wechat_tui.app import MainScreen
        print("MainScreen imported")

        try:
            print("Creating MainScreen...")
            screen = MainScreen()
            print("MainScreen created")
            await self.push_screen(screen)
            print("push_screen succeeded!")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        self.exit()

print("Running test app...")
app = TestApp()
app.run(headless=True)
print("Test complete")