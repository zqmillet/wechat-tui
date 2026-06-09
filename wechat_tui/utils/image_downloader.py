"""Image downloader for WeChat messages."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Downloads and stores images from WeChat messages.

    Uses wxpy's msg.get_file() method to download images to local storage.
    """

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}
    DEFAULT_EXTENSION = "jpg"

    def __init__(self, image_dir: Path) -> None:
        """Initialize the image downloader.

        Args:
            image_dir: Base directory for image storage
        """
        self.image_dir = image_dir

    def download_image(
        self,
        msg,  # wxpy Message object
        chat_id: str,
        timestamp: float,
        msg_id: str,
    ) -> Optional[str]:
        """Download an image from a wxpy message.

        Args:
            msg: wxpy Message object with get_file() method
            chat_id: Chat ID for determining storage location
            timestamp: Message timestamp
            msg_id: Message ID for filename uniqueness

        Returns:
            Local file path if successful, None on failure
        """
        try:
            # Detect file extension
            ext = self._detect_extension(msg)

            # Generate filename
            filename = self._generate_filename(timestamp, msg_id, ext)

            # Determine storage directory
            is_chatroom = chat_id.startswith("@@")
            subdir = "chatroom" if is_chatroom else "private"
            date_dir = datetime.fromtimestamp(timestamp).strftime("%Y-%m")

            storage_dir = self.image_dir / subdir / chat_id / date_dir
            storage_dir.mkdir(parents=True, exist_ok=True)

            file_path = storage_dir / filename

            # Handle filename collision (rare due to msg_id uniqueness)
            if file_path.exists():
                counter = 1
                base = file_path.stem
                while file_path.exists():
                    file_path = storage_dir / f"{base}_{counter}.{ext}"
                    counter += 1

            # Download using wxpy's get_file() method
            # get_file() saves to the specified path
            msg.get_file(str(file_path))

            # Verify download succeeded
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"Image downloaded successfully: {file_path}")
                return str(file_path)
            else:
                logger.error(
                    f"Image download verification failed: "
                    f"file_path={file_path}, exists={file_path.exists()}, "
                    f"size={file_path.stat().st_size if file_path.exists() else 0}"
                )
                # Clean up empty file if created
                if file_path.exists():
                    file_path.unlink()
                return None

        except Exception as e:
            logger.error(f"Image download error: {e}", exc_info=True)
            return None

    def _detect_extension(self, msg) -> str:
        """Detect file extension from wxpy message.

        Args:
            msg: wxpy Message object

        Returns:
            File extension (e.g., 'jpg', 'png')
        """
        # Try to get extension from file_name attribute
        if hasattr(msg, "file_name") and msg.file_name:
            ext = Path(msg.file_name).suffix.lower().lstrip(".")
            if ext in self.ALLOWED_EXTENSIONS:
                return ext

        # Default to jpg if unable to detect
        return self.DEFAULT_EXTENSION

    def _generate_filename(self, timestamp: float, msg_id: str, ext: str) -> str:
        """Generate a unique filename for the image.

        Args:
            timestamp: Message timestamp
            msg_id: Message ID
            ext: File extension

        Returns:
            Filename string
        """
        return f"{timestamp}_{msg_id}.{ext}"