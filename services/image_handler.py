"""
ImageHandler - Processes quiz images for display in 4x4 grid format.

Responsibilities:
- Load images from a normal directory (default) or ZIP archive (legacy)
- Split image into 4x4 grid of cells
- Generate masked images (hidden cells are pixelated)
- Convert between cell indices and pixel coordinates
"""

import logging
from pathlib import Path
from typing import Tuple, Optional, Set, Iterable
from zipfile import ZipFile
from io import BytesIO

from PIL import Image, ImageFilter, ImageDraw

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handles image processing for quiz rounds."""

    _SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    def __init__(
        self,
        images_archive: str = "assets/images",
        mask_strategy: str = "pixelate",
        pixel_block_size: int = 20,
        allow_placeholder: bool = True,
    ):
        """Initialize ImageHandler."""
        self.images_archive_path = Path(images_archive)
        self.mask_strategy = mask_strategy
        self.pixel_block_size = pixel_block_size
        self.allow_placeholder = allow_placeholder
        self._image_cache = {}
        self.grid_size = 4
        self.grid_cells = 16
        logger.debug(f"ImageHandler initialized with source: {images_archive}")

    def load_image(self, image_id: str, use_cache: bool = True) -> Image.Image:
        """Load image by image_id from directory (default) or ZIP archive."""
        if use_cache and image_id in self._image_cache:
            return self._image_cache[image_id]

        try:
            if self.images_archive_path.suffix.lower() == ".zip":
                image = self._load_from_zip(image_id)
            else:
                image = self._load_from_directory(image_id)
        except FileNotFoundError:
            if self._should_generate_placeholder():
                image = self._generate_placeholder_image(image_id)
            else:
                raise

        if image.mode != "RGB":
            image = image.convert("RGB")

        if use_cache:
            self._image_cache[image_id] = image

        return image

    def _load_from_zip(self, image_id: str) -> Image.Image:
        """Load image from ZIP archive (legacy compatibility)."""
        try:
            with ZipFile(self.images_archive_path, "r") as archive:
                for filename in self._candidate_names(image_id):
                    try:
                        with archive.open(filename) as img_file:
                            img_data = BytesIO(img_file.read())
                            image = Image.open(img_data)
                            image.load()
                            return image
                    except KeyError:
                        continue
                raise FileNotFoundError(f"Image {image_id} not found")
        except Exception as e:
            logger.error(f"Failed to load {image_id}: {e}")
            raise

    def _load_from_directory(self, image_id: str) -> Image.Image:
        """Load image from directory."""
        directory = self.images_archive_path

        for candidate in self._candidate_names(image_id):
            image_path = directory / candidate
            if image_path.exists():
                image = Image.open(image_path)
                image.load()
                return image

        image_stem = Path(image_id).stem
        for path in directory.glob(f"{image_stem}.*"):
            if path.suffix.lower() in self._SUPPORTED_EXTENSIONS:
                image = Image.open(path)
                image.load()
                return image

        raise FileNotFoundError(f"Image {image_id} not found")

    def _candidate_names(self, image_id: str) -> Iterable[str]:
        """Build candidate filenames for an image id."""
        image_path = Path(image_id)
        if image_path.suffix:
            yield image_path.name

        stem = image_path.stem
        for ext in self._SUPPORTED_EXTENSIONS:
            yield f"{stem}{ext}"

    def _should_generate_placeholder(self) -> bool:
        """Generate placeholders only for default runtime image directory."""
        if not self.allow_placeholder:
            return False

        normalized = str(self.images_archive_path).replace("\\", "/").lower()
        return normalized.endswith("assets/images")

    def _generate_placeholder_image(self, image_id: str) -> Image.Image:
        """Generate a visual placeholder when image assets are missing."""
        width, height = 960, 540
        image = Image.new("RGB", (width, height), color="#0f172a")
        draw = ImageDraw.Draw(image)

        cell_w = width // self.grid_size
        cell_h = height // self.grid_size

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * cell_w
                y1 = row * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                is_even = (row + col) % 2 == 0
                fill = "#1e293b" if is_even else "#334155"
                draw.rectangle((x1, y1, x2, y2), fill=fill, outline="#475569", width=2)

        draw.text((30, 24), "Obrázek nebyl nalezen", fill="#f8fafc")
        draw.text((30, 56), f"ID: {image_id}", fill="#cbd5e1")
        draw.text((30, 88), "Doplnte soubor do assets/images/", fill="#94a3b8")
        return image

    def get_cell_dimensions(self, image: Image.Image) -> Tuple[int, int]:
        """Get dimensions of one grid cell."""
        img_width, img_height = image.size
        cell_width = img_width // self.grid_size
        cell_height = img_height // self.grid_size
        return (cell_width, cell_height)

    def get_cell_pixels(
        self,
        image: Image.Image,
        cell_index: int
    ) -> Tuple[int, int, int, int]:
        """Get pixel coordinates (x1, y1, x2, y2) for a grid cell."""
        if cell_index < 0 or cell_index >= self.grid_cells:
            raise ValueError(f"Cell index must be 0-{self.grid_cells-1}")
        
        cell_width, cell_height = self.get_cell_dimensions(image)
        row = cell_index // self.grid_size
        col = cell_index % self.grid_size
        
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height

        return (x1, y1, x2, y2)

    def get_masked_image(
        self,
        image: Image.Image,
        revealed_cells: Optional[Set[int]] = None
    ) -> Image.Image:
        """Generate masked image with unrevealed cells pixelated/blurred."""
        if revealed_cells is None:
            revealed_cells = set()

        masked_image = image.copy()

        for cell_idx in range(self.grid_cells):
            if cell_idx not in revealed_cells:
                self._mask_cell(masked_image, cell_idx)

        return masked_image

    def _mask_cell(self, image: Image.Image, cell_index: int) -> None:
        """Mask a single cell in place."""
        x1, y1, x2, y2 = self.get_cell_pixels(image, cell_index)
        cell = image.crop((x1, y1, x2, y2))

        if self.mask_strategy == "pixelate":
            masked_cell = self._pixelate_cell(cell)
        else:
            masked_cell = self._blur_cell(cell)

        image.paste(masked_cell, (x1, y1))

    def _pixelate_cell(self, cell: Image.Image) -> Image.Image:
        """Pixelate a cell."""
        small_size = max(1, cell.size[0] // self.pixel_block_size)
        small = cell.resize((small_size, small_size), Image.Resampling.BILINEAR)
        return small.resize(cell.size, Image.Resampling.NEAREST)

    def _blur_cell(self, cell: Image.Image) -> Image.Image:
        """Blur a cell."""
        radius = min(cell.size) // 4
        return cell.filter(ImageFilter.GaussianBlur(radius=radius))

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._image_cache.clear()

    def get_cache_info(self) -> dict:
        """Get information about cached images."""
        return {
            "cached_count": len(self._image_cache),
            "cached_ids": list(self._image_cache.keys()),
        }

    def __str__(self) -> str:
        """String representation."""
        return f"ImageHandler(strategy={self.mask_strategy}, cached={len(self._image_cache)})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"ImageHandler(source={self.images_archive_path}, grid={self.grid_size}x{self.grid_size})"
