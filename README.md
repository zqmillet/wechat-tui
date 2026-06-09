# WeChat TUI

A Terminal User Interface (TUI) WeChat client built with Python and Textual.

![WeChat TUI](https://via.placeholder.com/800x400?text=WeChat+TUI+Screenshot)

## Features

- 🖥️ Cross-platform terminal interface (Linux, macOS, Windows)
- 💬 Real-time messaging with WeChat contacts
- 👥 Contact list management (friends, groups, official accounts)
- 🔍 Contact search
- 📱 QR code login in terminal
- 🎨 Beautiful and intuitive UI with CSS styling
- ⌨️ Comprehensive keyboard shortcuts
- 🔔 Unread message indicators
- 📁 File and image sending support (planned)

## Requirements

- Python 3.10+
- Terminal with Unicode support (recommended: modern terminals like iTerm2, Alacritty, Windows Terminal)

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/qiqi/wechat-tui.git
cd wechat-tui

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Run the application
wechat-tui
```

### Development Setup

```bash
pip install -e ".[dev]"
```

## Usage

### Running the Application

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run via entry point
wechat-tui

# Or run directly
python -m wechat_tui.main
```

### First Login

1. On first run, a QR code will be displayed in the terminal
2. Open WeChat on your phone
3. Go to Settings → Devices → Scan QR Code
4. Scan the QR code displayed in the terminal
5. Confirm login on your phone

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Switch between panels (contacts ↔ chat ↔ input) |
| `Enter` | Send message / Select contact |
| `Shift+Enter` | Insert new line in message |
| `Esc` | Cancel / Close dialog |
| `↑` / `↓` | Navigate messages / contacts |
| `Ctrl+Q` | Quit application |
| `Ctrl+L` | Logout from WeChat |
| `Ctrl+R` | Refresh contacts |
| `Ctrl+/` | Search contacts |
| `Ctrl+H` | Show help |

## Architecture

```
wechat_tui/
├── main.py              # Entry point and logging setup
├── app.py               # Main Textual application
├── wechat/
│   ├── client.py        # Itchat wrapper for WeChat protocol
│   └── handlers.py      # Message type handlers
├── ui/
│   ├── widgets/
│   │   ├── contact_list.py  # Contact list panel
│   │   ├── chat_panel.py    # Chat message display
│   │   ├── input_box.py     # Message input area
│   │   └── status_bar.py    # Bottom status bar
│   └── screens/
│   │   ├── login.py         # QR code login screen
│   │   └── help.py          # Help/shortcuts screen
├── models/
│   ├── contact.py       # Contact data model
│   └── message.py       # Message data model
└── utils/               # Helper functions
```

## Tech Stack

- **TUI Framework**: [Textual](https://github.com/Textualize/textual) - Modern async Python TUI framework
- **WeChat Protocol**: [itchat](https://github.com/littlecodersh/ItChat) - WeChat personal account API
- **Rich**: For beautiful terminal text rendering

## Limitations & Notes

1. **Web WeChat Protocol**: This project uses the Web WeChat protocol which may have limitations compared to the official client. Some features like video calls are not supported.

2. **Login Restrictions**: WeChat may restrict Web WeChat login for some accounts. If you cannot login, you may need to use the official WeChat app first.

3. **Rate Limits**: Be mindful of message sending rates to avoid being flagged by WeChat.

4. **Session Persistence**: Login sessions are stored in `~/.wechat/` directory for hot reload.

## Disclaimer

This is an **unofficial** WeChat client for educational purposes. It is not affiliated with Tencent. Please use responsibly and in accordance with WeChat's terms of service.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License