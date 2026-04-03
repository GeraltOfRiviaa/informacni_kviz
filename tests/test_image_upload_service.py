"""
Tests for ImageUploadService.

Coverage:
- Image upload with validation
- File format checking
- File size validation
- Dimensions validation
- Image ID generation
- Metadata management
- Image deletion
- Statistics
- Error handling and edge cases
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image
import io

from services.image_upload_service import ImageUploadService, MAX_IMAGE_SIZE_BYTES


@pytest.fixture
def temp_images_dir():
    """Create a temporary images directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def service(temp_images_dir):
    """Create an ImageUploadService instance."""
    return ImageUploadService(images_dir=temp_images_dir)


@pytest.fixture
def sample_jpg_file(tmp_path):
    """Create a sample JPG file."""
    img = Image.new("RGB", (200, 200), color="red")
    file_path = tmp_path / "test.jpg"
    img.save(file_path, "JPEG")
    return str(file_path)


@pytest.fixture
def sample_png_file(tmp_path):
    """Create a sample PNG file."""
    img = Image.new("RGB", (300, 300), color="blue")
    file_path = tmp_path / "test.png"
    img.save(file_path, "PNG")
    return str(file_path)


@pytest.fixture
def small_image_file(tmp_path):
    """Create an image smaller than minimum dimensions."""
    img = Image.new("RGB", (50, 50), color="green")
    file_path = tmp_path / "small.jpg"
    img.save(file_path, "JPEG")
    return str(file_path)


@pytest.fixture
def large_file(tmp_path):
    """Create a file larger than max image size."""
    file_path = tmp_path / "large.bin"
    # Create a file larger than MAX_IMAGE_SIZE_BYTES
    file_path.write_bytes(b"x" * (MAX_IMAGE_SIZE_BYTES + 1024))
    return str(file_path)


class TestImageUpload:
    """Test image upload functionality."""

    def test_upload_jpg_success(self, service, sample_jpg_file):
        """Test successful JPG upload."""
        result = service.upload_image(
            file_path=sample_jpg_file,
            reference_name="test_image",
        )

        assert result["success"] is True
        assert "image_id" in result
        assert result["format"] == "jpg"
        assert result["width"] == 200
        assert result["height"] == 200

    def test_upload_png_success(self, service, sample_png_file):
        """Test successful PNG upload."""
        result = service.upload_image(
            file_path=sample_png_file,
            reference_name="png_test",
            description="Test PNG image",
        )

        assert result["success"] is True
        assert result["format"] == "png"
        assert result["width"] == 300
        assert result["height"] == 300

    def test_upload_nonexistent_file(self, service):
        """Test uploading non-existent file."""
        result = service.upload_image(file_path="/nonexistent/file.jpg")

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_upload_empty_file(self, service, tmp_path):
        """Test uploading empty file."""
        empty_file = tmp_path / "empty.jpg"
        empty_file.write_bytes(b"")

        result = service.upload_image(file_path=str(empty_file))

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_upload_too_large(self, service, large_file):
        """Test uploading file that exceeds size limit."""
        result = service.upload_image(file_path=large_file)

        assert result["success"] is False
        assert "too large" in result["error"].lower()

    def test_upload_unsupported_format(self, service, tmp_path):
        """Test uploading unsupported file format."""
        bad_file = tmp_path / "test.bmp"
        # Create a fake BMP file
        bad_file.write_bytes(b"fake content")

        result = service.upload_image(file_path=str(bad_file))

        assert result["success"] is False
        assert "unsupported" in result["error"].lower() or "magic" in result["error"].lower()

    def test_upload_too_small_image(self, service, small_image_file):
        """Test uploading image too small for quiz."""
        result = service.upload_image(file_path=small_image_file)

        assert result["success"] is False
        assert "too small" in result["error"].lower()

    def test_upload_generates_unique_ids(self, service, sample_jpg_file, sample_png_file):
        """Test that uploads generate unique image IDs."""
        result1 = service.upload_image(file_path=sample_jpg_file)
        result2 = service.upload_image(file_path=sample_png_file)

        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["image_id"] != result2["image_id"]


class TestMetadata:
    """Test metadata management."""

    def test_get_image_metadata(self, service, sample_jpg_file):
        """Test retrieving image metadata."""
        result = service.upload_image(
            file_path=sample_jpg_file,
            reference_name="steve_jobs",
            description="Famous Tech Person",
        )

        image_id = result["image_id"]
        metadata = service.get_image_metadata(image_id)

        assert metadata is not None
        assert metadata["image_id"] == image_id
        assert metadata["reference_name"] == "steve_jobs"
        assert metadata["description"] == "Famous Tech Person"

    def test_get_nonexistent_metadata(self, service):
        """Test getting metadata for non-existent image."""
        metadata = service.get_image_metadata("img_nonexistent")
        assert metadata is None

    def test_get_image_path(self, service, sample_jpg_file):
        """Test getting filesystem path for image."""
        result = service.upload_image(file_path=sample_jpg_file)
        image_id = result["image_id"]

        path = service.get_image_path(image_id)

        assert path is not None
        assert path.exists()
        assert path.name.startswith(image_id)

    def test_get_nonexistent_image_path(self, service):
        """Test getting path for non-existent image."""
        path = service.get_image_path("img_nonexistent")
        assert path is None


class TestImageDeletion:
    """Test image deletion."""

    def test_delete_existing_image(self, service, sample_jpg_file):
        """Test deleting an uploaded image."""
        result = service.upload_image(file_path=sample_jpg_file)
        image_id = result["image_id"]

        # Verify it exists
        path = service.get_image_path(image_id)
        assert path.exists()

        # Delete it
        deleted = service.delete_image(image_id)

        assert deleted is True
        assert service.get_image_metadata(image_id) is None
        assert not path.exists()

    def test_delete_nonexistent_image(self, service):
        """Test deleting non-existent image."""
        result = service.delete_image("img_nonexistent")
        assert result is False

    def test_delete_persists(self, service, sample_jpg_file):
        """Test that deletion persists after reload."""
        result = service.upload_image(file_path=sample_jpg_file)
        image_id = result["image_id"]

        service.delete_image(image_id)

        # Create new service instance to reload metadata
        images_dir = service.images_dir
        service2 = ImageUploadService(images_dir=str(images_dir))

        assert service2.get_image_metadata(image_id) is None


class TestListing:
    """Test image listing."""

    def test_list_empty(self, service):
        """Test listing when no images uploaded."""
        images = service.list_images()
        assert len(images) == 0

    def test_list_multiple_images(self, service, sample_jpg_file, sample_png_file):
        """Test listing multiple images."""
        service.upload_image(file_path=sample_jpg_file, reference_name="image1")
        service.upload_image(file_path=sample_png_file, reference_name="image2")

        images = service.list_images()

        assert len(images) == 2
        assert images[0]["reference_name"] == "image1"
        assert images[1]["reference_name"] == "image2"


class TestStatistics:
    """Test statistics generation."""

    def test_statistics_empty(self, service):
        """Test statistics on empty service."""
        stats = service.get_statistics()

        assert stats["total_images"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["by_format"] == {}

    def test_statistics_with_images(self, service, sample_jpg_file, sample_png_file):
        """Test statistics with uploaded images."""
        service.upload_image(file_path=sample_jpg_file)
        service.upload_image(file_path=sample_png_file)

        stats = service.get_statistics()

        assert stats["total_images"] == 2
        assert stats["total_size_bytes"] > 0
        assert "jpg" in stats["by_format"]
        assert "png" in stats["by_format"]
        assert stats["by_format"]["jpg"] == 1
        assert stats["by_format"]["png"] == 1


class TestMagicBytesValidation:
    """Test magic bytes validation."""

    def test_detect_invalid_jpg_header(self, service, tmp_path):
        """Test detection of invalid JPG header."""
        bad_jpg = tmp_path / "fake.jpg"
        # Write PNG header but claim it's JPG
        bad_jpg.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 100)

        result = service.upload_image(file_path=str(bad_jpg))

        # Should fail magic bytes check
        assert result["success"] is False

    def test_detect_invalid_png_header(self, service, tmp_path):
        """Test detection of invalid PNG header."""
        bad_png = tmp_path / "fake.png"
        # Write JPG header but claim it's PNG
        bad_png.write_bytes(b"\xff\xd8\xff" + b"x" * 100)

        result = service.upload_image(file_path=str(bad_png))

        # Should fail magic bytes check
        assert result["success"] is False


class TestMetadataPersistence:
    """Test metadata persistence."""

    def test_metadata_persists_on_reload(self, temp_images_dir, sample_jpg_file):
        """Test that metadata persists when service is reloaded."""
        # Upload image with first instance
        service1 = ImageUploadService(images_dir=temp_images_dir)
        result = service1.upload_image(
            file_path=sample_jpg_file,
            reference_name="persist_test",
        )
        image_id = result["image_id"]

        # Create new instance
        service2 = ImageUploadService(images_dir=temp_images_dir)

        # Check metadata is still there
        metadata = service2.get_image_metadata(image_id)
        assert metadata is not None
        assert metadata["reference_name"] == "persist_test"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_upload_with_special_characters_in_filename(self, service, tmp_path):
        """Test uploading file with special characters."""
        img = Image.new("RGB", (200, 200), color="red")
        special_file = tmp_path / "test_特殊文字.jpg"
        img.save(special_file, "JPEG")

        result = service.upload_image(file_path=str(special_file))

        assert result["success"] is True

    def test_upload_with_long_reference_name(self, service, sample_jpg_file):
        """Test uploading with very long reference name."""
        long_name = "x" * 500

        result = service.upload_image(
            file_path=sample_jpg_file,
            reference_name=long_name,
        )

        assert result["success"] is True

    def test_concurrent_uploads_unique_ids(self, service, sample_jpg_file):
        """Test that concurrent uploads would get unique IDs."""
        # Upload same file multiple times
        results = []
        for _ in range(5):
            results.append(service.upload_image(file_path=sample_jpg_file))

        # All should succeed
        assert all(r["success"] for r in results)

        # All should have different IDs
        image_ids = [r["image_id"] for r in results]
        assert len(image_ids) == len(set(image_ids))
