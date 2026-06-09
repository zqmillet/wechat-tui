"""Application configuration management."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration.

    Manages storage paths and application settings.
    """

    data_dir: Path = field(default_factory=lambda: Path.home() / ".wechat-tui")
    auto_download_images: bool = True
    image_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Initialize derived paths and ensure directories exist."""
        # Convert to Path if string was provided
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)

        self.image_dir = self.data_dir / "images"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create necessary storage directories."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for private and chatroom images
        (self.image_dir / "private").mkdir(exist_ok=True)
        (self.image_dir / "chatroom").mkdir(exist_ok=True)

    def get_image_path(self, chat_id: str, timestamp: float) -> Path:
        """Get the directory path for storing an image.

        Args:
            chat_id: The chat ID (user ID or chatroom ID)
            timestamp: Message timestamp for date-based folder

        Returns:
            Path to the appropriate storage directory
        """
        from datetime import datetime

        # Determine if chatroom (starts with @@) or private chat
        is_chatroom = chat_id.startswith("@@")
        subdir = "chatroom" if is_chatroom else "private"

        # Create date-based folder (YYYY-MM)
        date_folder = datetime.fromtimestamp(timestamp).strftime("%Y-%m")

        return self.image_dir / subdir / chat_id / date_folder