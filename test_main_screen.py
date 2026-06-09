"""Test pushing MainScreen."""

import asyncio
from textual.app import App
from textual.screen import Screen

# Import our screens
from wechat_tui.app import MainScreen, LoginScreen, WeChatApp

async def test_app():
    print("Creating WeChatApp...")
    app = WeChatApp()
    print("App created")

    print("Testing screen push...")
    try:
        screen = MainScreen()
        print("MainScreen instance created successfully")
    except Exception as e:
        print(f"MainScreen creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nNow running app headless to test push_screen...")
    # Run in headless mode
    async def push_main():
        try:
            print("Pushing MainScreen...")
            await app.push_screen(MainScreen())
            print("MainScreen pushed successfully!")
        except Exception as e:
            print(f"push_screen failed: {e}")
            import traceback
            traceback.print_exc()
        await app.exit()

    app.run(headless=True)

# Run test
print("=" * 50)
test_app()