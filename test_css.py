"""Test MainScreen CSS."""

import sys
sys.path.insert(0, '/root/workspace/wechat-tui')

from textual.app import App
from textual.screen import Screen

# Import all the widgets to test CSS
from wechat_tui.app import MainScreen, LoginScreen
from wechat_tui.ui.widgets.contact_list import ContactList, ContactItem
from wechat_tui.ui.widgets.chat_panel import ChatPanel
from wechat_tui.ui.widgets.input_box import InputBox
from wechat_tui.ui.widgets.status_bar import StatusBar
from wechat_tui.ui.screens.help import HelpScreen

print("Testing CSS parsing...")

try:
    screen = MainScreen()
    print("MainScreen created successfully!")
except Exception as e:
    print(f"MainScreen error: {e}")
    import traceback
    traceback.print_exc()

try:
    screen = LoginScreen()
    print("LoginScreen created successfully!")
except Exception as e:
    print(f"LoginScreen error: {e}")
    import traceback
    traceback.print_exc()

try:
    widget = ContactList()
    print("ContactList created successfully!")
except Exception as e:
    print(f"ContactList error: {e}")
    import traceback
    traceback.print_exc()

try:
    widget = ChatPanel()
    print("ChatPanel created successfully!")
except Exception as e:
    print(f"ChatPanel error: {e}")
    import traceback
    traceback.print_exc()

try:
    widget = InputBox()
    print("InputBox created successfully!")
except Exception as e:
    print(f"InputBox error: {e}")
    import traceback
    traceback.print_exc()

try:
    widget = StatusBar()
    print("StatusBar created successfully!")
except Exception as e:
    print(f"StatusBar error: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests done.")