"""Convert images to ASCII art for terminal display."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ImageToAscii:
    """Convert images to ASCII art.

    Uses PIL/Pillow to load images and convert them to ASCII characters
    based on pixel brightness.
    """

    # ASCII characters from dark to light
    ASCII_CHARS = "@%#*+=-:. "

    # For more detailed output
    ASCII_CHARS_DENSE = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    def __init__(self, width: int = 40) -> None:
        """Initialize the converter.

        Args:
            width: Target width for ASCII output (characters)
        """
        self.width = width

    def convert(
        self,
        image_path: str,
        width: Optional[int] = None,
        colored: bool = False,
        dense: bool = False,
    ) -> Optional[str]:
        """Convert an image to ASCII art.

        Args:
            image_path: Path to the image file
            width: Override default width
            colored: Whether to use ANSI color codes (experimental)
            dense: Use dense character set for more detail

        Returns:
            ASCII art string or None on failure
        """
        try:
            from PIL import Image

            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image file not found: {path}")
                return None

            # Load image
            img = Image.open(path)

            # Convert to RGB if necessary (for color mode)
            if colored and img.mode != 'RGB':
                img = img.convert('RGB')
            elif not colored and img.mode != 'L':
                img = img.convert('L')  # Convert to grayscale

            # Resize image to target width
            target_width = width or self.width

            # Calculate new dimensions maintaining aspect ratio
            # ASCII characters are taller than wide, so adjust ratio
            aspect_ratio = img.height / img.width
            new_width = target_width
            new_height = int(target_width * aspect_ratio * 0.5)  # 0.5 to account for char height

            img = img.resize((new_width, new_height))

            # Convert to ASCII
            if colored:
                return self._convert_colored(img, new_width, new_height)
            else:
                chars = self.ASCII_CHARS_DENSE if dense else self.ASCII_CHARS
                return self._convert_grayscale(img, new_width, new_height, chars)

        except ImportError:
            logger.warning("PIL/Pillow not installed, cannot convert image to ASCII")
            return None
        except Exception as e:
            logger.error(f"Failed to convert image to ASCII: {e}", exc_info=True)
            return None

    def _convert_grayscale(
        self,
        img,  # PIL Image in grayscale mode
        width: int,
        height: int,
        chars: str,
    ) -> str:
        """Convert grayscale image to ASCII."""
        pixels = img.getdata()

        # Map each pixel to a character
        ascii_str = ""
        for i, pixel in enumerate(pixels):
            # Map pixel value (0-255) to character index
            char_idx = int(pixel / 255 * (len(chars) - 1))
            ascii_str += chars[char_idx]

            # Add newline at end of each row
            if (i + 1) % width == 0:
                ascii_str += "\n"

        return ascii_str

    def _convert_colored(
        self,
        img,  # PIL Image in RGB mode
        width: int,
        height: int,
    ) -> str:
        """Convert RGB image to colored ASCII using ANSI codes."""
        pixels = img.getdata()

        # Use a simple block character
        char = "█"

        ascii_str = ""
        for i, pixel in enumerate(pixels):
            r, g, b = pixel

            # ANSI escape code for RGB color
            # \033[38;2;R;G;B;m sets foreground color
            color_code = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            ascii_str += color_code

            # Add newline at end of each row
            if (i + 1) % width == 0:
                ascii_str += "\n"

        return ascii_str

    def convert_small(self, image_path: str) -> Optional[str]:
        """Convert image to small ASCII preview (20 chars width).

        Args:
            image_path: Path to the image file

        Returns:
            Small ASCII art string
        """
        return self.convert(image_path, width=20)

    def convert_medium(self, image_path: str) -> Optional[str]:
        """Convert image to medium ASCII preview (40 chars width).

        Args:
            image_path: Path to the image file

        Returns:
            Medium ASCII art string
        """
        return self.convert(image_path, width=40)

    def convert_large(self, image_path: str) -> Optional[str]:
        """Convert image to large ASCII preview (80 chars width).

        Args:
            image_path: Path to the image file

        Returns:
            Large ASCII art string
        """
        return self.convert(image_path, width=80, dense=True)