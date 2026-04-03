"""
Tests for ImageHandler service.

Tests image loading, masking, and cell processing.
"""

import pytest
from pathlib import Path
from PIL import Image
import tempfile
import os

from services.image_handler import ImageHandler


class TestImageHandlerInit:
    """Test ImageHandler initialization."""
    
    def test_initialization(self):
        """Test basic initialization."""
        handler = ImageHandler()
        assert handler.grid_size == 4
        assert handler.grid_cells == 16
        assert handler.mask_strategy == "pixelate"
        assert handler.pixel_block_size == 20
        assert len(handler._image_cache) == 0
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        handler = ImageHandler(
            images_archive="custom/path.zip",
            mask_strategy="blur",
            pixel_block_size=30
        )
        assert handler.mask_strategy == "blur"
        assert handler.pixel_block_size == 30


class TestImageHandlerLoading:
    """Test image loading from file system."""
    
    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a 400x400 test image (divisible by 4)
            img = Image.new("RGB", (400, 400), color=(255, 0, 0))
            img_path = Path(tmpdir) / "test_img.jpg"
            img.save(img_path)
            yield str(Path(tmpdir)), "test_img"
    
    def test_load_from_directory(self, temp_image):
        """Test loading image from directory."""
        tmpdir, image_id = temp_image
        handler = ImageHandler(images_archive=tmpdir)
        image = handler.load_image(image_id)
        
        assert image is not None
        assert image.size == (400, 400)
        assert image.mode == "RGB"
    
    def test_load_with_cache(self, temp_image):
        """Test that images are cached."""
        tmpdir, image_id = temp_image
        handler = ImageHandler(images_archive=tmpdir)
        
        img1 = handler.load_image(image_id)
        img2 = handler.load_image(image_id)
        
        assert image_id in handler._image_cache
        assert img1 is img2  # Same object in cache
    
    def test_load_without_cache(self, temp_image):
        """Test loading without caching."""
        tmpdir, image_id = temp_image
        handler = ImageHandler(images_archive=tmpdir)
        
        img1 = handler.load_image(image_id, use_cache=True)
        img2 = handler.load_image(image_id, use_cache=False)
        
        # Both should be valid images but different objects
        assert img1.size == img2.size
    
    def test_load_nonexistent(self):
        """Test loading non-existent image."""
        handler = ImageHandler(images_archive="nonexistent/path")
        with pytest.raises(FileNotFoundError):
            handler.load_image("img_0000")


class TestImageHandlerCellDimensions:
    """Test cell dimension calculations."""
    
    def test_get_cell_dimensions(self):
        """Test cell dimension calculation."""
        img = Image.new("RGB", (400, 400))
        handler = ImageHandler()
        
        width, height = handler.get_cell_dimensions(img)
        assert width == 100
        assert height == 100
    
    def test_get_cell_dimensions_non_square(self):
        """Test cell dimensions for non-square image."""
        img = Image.new("RGB", (800, 400))
        handler = ImageHandler()
        
        width, height = handler.get_cell_dimensions(img)
        assert width == 200
        assert height == 100


class TestImageHandlerCellPixels:
    """Test cell pixel coordinate calculations."""
    
    def test_get_cell_pixels_first_cell(self):
        """Test pixel coordinates for first cell (0,0)."""
        img = Image.new("RGB", (400, 400))
        handler = ImageHandler()
        
        x1, y1, x2, y2 = handler.get_cell_pixels(img, 0)
        assert (x1, y1, x2, y2) == (0, 0, 100, 100)
    
    def test_get_cell_pixels_last_cell(self):
        """Test pixel coordinates for last cell (3,3)."""
        img = Image.new("RGB", (400, 400))
        handler = ImageHandler()
        
        # Cell 15 is at position (3, 3)
        x1, y1, x2, y2 = handler.get_cell_pixels(img, 15)
        assert (x1, y1, x2, y2) == (300, 300, 400, 400)
    
    def test_get_cell_pixels_middle(self):
        """Test pixel coordinates for middle cell."""
        img = Image.new("RGB", (400, 400))
        handler = ImageHandler()
        
        # Cell 5 is at position (1, 1)
        x1, y1, x2, y2 = handler.get_cell_pixels(img, 5)
        assert (x1, y1, x2, y2) == (100, 100, 200, 200)
    
    def test_get_cell_pixels_invalid(self):
        """Test invalid cell indices."""
        img = Image.new("RGB", (400, 400))
        handler = ImageHandler()
        
        with pytest.raises(ValueError):
            handler.get_cell_pixels(img, -1)
        
        with pytest.raises(ValueError):
            handler.get_cell_pixels(img, 16)


class TestImageHandlerMasking:
    """Test image masking functionality."""
    
    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        img = Image.new("RGB", (400, 400), color=(100, 100, 100))
        return img
    
    def test_get_masked_image_all_masked(self, test_image):
        """Test fully masked image (no cells revealed)."""
        handler = ImageHandler()
        masked = handler.get_masked_image(test_image, revealed_cells=set())
        
        assert masked.size == test_image.size
        assert masked is not test_image  # Should be a copy
    
    def test_get_masked_image_all_revealed(self, test_image):
        """Test fully revealed image (all cells shown)."""
        handler = ImageHandler()
        all_cells = set(range(16))
        masked = handler.get_masked_image(test_image, revealed_cells=all_cells)
        
        # Get pixels from original and masked
        orig_pixels = test_image.load()
        mask_pixels = masked.load()
        
        # Sample some pixels - should be similar (some pixelation may occur)
        assert orig_pixels[0, 0] == mask_pixels[0, 0]
    
    def test_get_masked_image_partial(self, test_image):
        """Test partially masked image."""
        handler = ImageHandler()
        revealed = {0, 5, 10, 15}  # Corners and some middle
        masked = handler.get_masked_image(test_image, revealed_cells=revealed)
        
        assert masked.size == test_image.size
    
    def test_pixelation_strategy(self, test_image):
        """Test pixelate masking strategy."""
        handler = ImageHandler(mask_strategy="pixelate", pixel_block_size=20)
        masked = handler.get_masked_image(test_image, revealed_cells={0})
        
        assert masked.size == test_image.size
    
    def test_blur_strategy(self, test_image):
        """Test blur masking strategy."""
        handler = ImageHandler(mask_strategy="blur")
        masked = handler.get_masked_image(test_image, revealed_cells={0})
        
        assert masked.size == test_image.size


class TestImageHandlerCaching:
    """Test image cache management."""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return ImageHandler()
    
    def test_clear_cache(self, handler, tmp_path):
        """Test cache clearing."""
        # Create a test image
        img = Image.new("RGB", (400, 400))
        img_path = tmp_path / "test_img.jpg"
        img.save(img_path)
        
        handler.images_archive_path = tmp_path
        handler.load_image("test_img")
        
        assert len(handler._image_cache) > 0
        handler.clear_cache()
        assert len(handler._image_cache) == 0
    
    def test_get_cache_info(self, handler):
        """Test cache info retrieval."""
        info = handler.get_cache_info()
        
        assert "cached_count" in info
        assert "cached_ids" in info
        assert info["cached_count"] == 0


class TestImageHandlerStringMethods:
    """Test string representations."""
    
    def test_str(self):
        """Test __str__ method."""
        handler = ImageHandler()
        s = str(handler)
        assert "ImageHandler" in s
        assert "pixelate" in s
    
    def test_repr(self):
        """Test __repr__ method."""
        handler = ImageHandler()
        r = repr(handler)
        assert "ImageHandler" in r
        assert "4x4" in r
