"""Test MainScreen CSS parsing."""

from textual.css.stylesheet import Stylesheet
from wechat_tui.app import MainScreen

# Get the CSS from MainScreen
css = MainScreen.DEFAULT_CSS

print("MainScreen CSS:")
print(css)
print("\nParsing CSS...")

try:
    ss = Stylesheet()
    # This is how textual parses CSS internally
    ss.add(css, "test")
    ss.parse()
    print("CSS parsed successfully!")
except Exception as e:
    print(f"CSS parse error: {e}")
    # Try to get more details
    if hasattr(e, '__cause__'):
        print(f"Cause: {e.__cause__}")
    import traceback
    traceback.print_exc()