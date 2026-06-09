"""Input widget for composing messages."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static, TextArea


class MessageTextArea(TextArea):
    """Custom TextArea that handles Enter key for sending messages."""

    class SendMessage(Message):
        """Sent when Enter is pressed to send message."""

        pass

    def on_key(self, event) -> None:
        """Handle key events."""
        # Check if Shift is pressed by looking at the key string
        # In Textual, shift+enter produces key="shift+enter"
        if "enter" in event.key and "shift" not in event.key:
            # Enter: send message
            event.stop()
            event.prevent_default()
            self.post_message(self.SendMessage())
            return
        # Shift+Enter: let it pass through for newline


class InputBox(Widget):
    """Input area for composing messages."""

    DEFAULT_CSS = """
    InputBox {
        width: 100%;
        height: 8;
        background: #161b22;
        border-top: solid #30363d;
        padding: 1;
    }

    InputBox Vertical {
        height: 5;
    }

    InputBox .input-area {
        height: 5;
    }

    InputBox MessageTextArea {
        height: 5;
        background: #0d1117;
        border: solid #30363d;
        color: #c9d1d9;
        padding: 0 1;
    }

    InputBox .toolbar {
        height: 2;
        align-horizontal: right;
    }

    InputBox .toolbar Button {
        min-width: 8;
        height: 1;
        margin-left: 1;
    }

    InputBox .char-count {
        color: #8b949e;
    }

    InputBox .char-count.warning {
        color: #d29922;
    }

    InputBox .char-count.error {
        color: #f85149;
    }
    """

    enabled: reactive[bool] = reactive(True)
    char_limit: reactive[int] = reactive(5000)  # WeChat message limit

    class Submit(Message):
        """Sent when user submits a message."""

        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()

    class RequestFile(Message):
        """Sent when user wants to send a file."""

        pass

    class RequestImage(Message):
        """Sent when user wants to send an image."""

        pass

    def __init__(self, *, id: Optional[str] = None, classes: Optional[str] = None) -> None:
        super().__init__(id=id, classes=classes)

    def compose(self) -> ComposeResult:
        """Compose the input box."""
        with Vertical():
            yield MessageTextArea(id="message-input", classes="input-area")
        with Horizontal(classes="toolbar"):
            yield Static("0/5000", id="char-count", classes="char-count")
            yield Button("📎 文件", id="file-btn", variant="primary")
            yield Button("🖼️ 图片", id="image-btn", variant="primary")
            yield Button("发送 (Enter)", id="send-btn", variant="success")

    def on_mount(self) -> None:
        """Set up event handlers on mount."""
        self.query_one("#send-btn", Button).disabled = not self.enabled
        self.query_one("#message-input", MessageTextArea).disabled = not self.enabled

    def watch_enabled(self, enabled: bool) -> None:
        """Update UI when enabled state changes."""
        try:
            self.query_one("#send-btn", Button).disabled = not enabled
            self.query_one("#message-input", MessageTextArea).disabled = not enabled
        except Exception:
            pass

    def on_message_text_area_changed(self, event: MessageTextArea.Changed) -> None:
        """Update character count when text changes."""
        if event.text_area.id == "message-input":
            self._update_char_count(len(event.text_area.text))

    def on_message_text_area_send_message(self, event: MessageTextArea.SendMessage) -> None:
        """Handle send message from TextArea."""
        self._submit()

    def _update_char_count(self, count: int) -> None:
        """Update the character count display."""
        try:
            char_count = self.query_one("#char-count", Static)
            char_count.update(f"{count}/{self.char_limit}")

            # Update color based on limit
            char_count.remove_class("warning", "error")
            if count > self.char_limit:
                char_count.add_class("error")
            elif count > self.char_limit * 0.8:
                char_count.add_class("warning")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send-btn":
            self._submit()
        elif event.button.id == "file-btn":
            self.post_message(self.RequestFile())
        elif event.button.id == "image-btn":
            self.post_message(self.RequestImage())

    def _submit(self) -> None:
        """Submit the current message."""
        if not self.enabled:
            return

        try:
            textarea = self.query_one("#message-input", MessageTextArea)
            content = textarea.text.strip()
            if content:
                self.post_message(self.Submit(content))
                textarea.clear()
                self._update_char_count(0)
        except Exception:
            pass

    def focus_input(self) -> None:
        """Focus the input textarea."""
        try:
            self.query_one("#message-input", MessageTextArea).focus()
        except Exception:
            pass

    def clear(self) -> None:
        """Clear the input."""
        try:
            self.query_one("#message-input", MessageTextArea).clear()
            self._update_char_count(0)
        except Exception:
            pass