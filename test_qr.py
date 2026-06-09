"""Test QR code display in Textual."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static
import pyqrcode


class QRScreen(Screen):
    """Test screen for QR code."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Test QR Code", id="title"),
            Static("Loading...", id="qr-code"),
        )

    def on_mount(self) -> None:
        """Generate and display QR code."""
        # Generate QR code
        url = "https://login.weixin.qq.com/l/test_uuid_12345"
        qr = pyqrcode.create(url)
        qr_text = qr.text()

        # Format for display
        lines = qr_text.strip().split('\n')
        formatted_lines = []
        for line in lines:
            formatted_line = ""
            for char in line:
                if char == '1':
                    formatted_line += "██"
                else:
                    formatted_line += "  "
            formatted_lines.append(formatted_line)

        formatted_qr = "\n".join(formatted_lines)

        # Update display
        qr_widget = self.query_one("#qr-code", Static)
        qr_widget.update(formatted_qr)
        print(f"QR code updated, lines: {len(lines)}")


class QRTestApp(App):
    """Test app."""

    def on_mount(self) -> None:
        self.push_screen(QRScreen())


if __name__ == "__main__":
    app = QRTestApp()
    app.run()