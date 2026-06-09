"""Main entry point for WeChat TUI."""

import logging
import sys
from pathlib import Path

from .app import run_app

# Create data directory first
data_dir = Path.home() / ".wechat-tui"
data_dir.mkdir(exist_ok=True)

# Set up logging - only to file, not to console (to avoid interfering with TUI)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(data_dir / "wechat-tui.log"),
    ],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    try:
        run_app()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()