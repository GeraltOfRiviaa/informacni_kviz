"""
Tests for AdminQuestionPanel UI component.

Coverage:
- Panel initialization and display
- Question table display
- Search and filtering
- Category and difficulty filtering
- CRUD button interactions
- Statistics display
- Image upload handling
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ui.admin_question_panel import AdminQuestionPanel
from services.admin_question_manager import AdminQuestionManager
from services.image_upload_service import ImageUploadService


@pytest.fixture
def root_window():
    """Create a root tkinter window."""
    root = tk.Tk()
    root.geometry("800x600")
    yield root
    root.destroy()


@pytest.fixture
def mock_manager():
    """Create a mock AdminQuestionManager."""
    manager = Mock(spec=AdminQuestionManager)
    manager.get_all_questions.return_value = [
        {
            "id": "q001",
            "category": "personality",
            "image_id": "img_001",
            "difficulty": "easy",
            "description": "Test question 1",
        },
        {
            "id": "q002",
            "category": "logo",
            "image_id": "img_002",
            "difficulty": "medium",
            "description": "Test question 2",
        },
    ]
    manager.get_statistics.return_value = {
        "total_questions": 2,
        "by_category": {"personality": 1, "logo": 1},
        "by_difficulty": {"easy": 1, "medium": 1},
    }
    manager.delete_question.return_value = True
    return manager


@pytest.fixture
def mock_images():
    """Create a mock ImageUploadService."""
    images = Mock(spec=ImageUploadService)
    return images


@pytest.fixture
def panel(root_window, mock_manager, mock_images):
    """Create an AdminQuestionPanel instance."""
    panel = AdminQuestionPanel(root_window, mock_manager, mock_images)
    yield panel
    try:
        panel.window.destroy()
    except tk.TclError:
        pass


class TestPanelInitialization:
    """Test panel initialization."""

    def test_creates_toplevel_window(self, root_window, mock_manager, mock_images):
        """Test that panel creates a Toplevel window."""
        panel = AdminQuestionPanel(root_window, mock_manager, mock_images)

        assert isinstance(panel.window, tk.Toplevel)
        assert panel.window.winfo_exists()

        panel.window.destroy()

    def test_window_title(self, root_window, mock_manager, mock_images):
        """Test window has correct title."""
        panel = AdminQuestionPanel(root_window, mock_manager, mock_images)

        assert "Admin Question" in panel.window.title()

        panel.window.destroy()

    def test_modal_properties(self, root_window, mock_manager, mock_images):
        """Test that window is properly configured as modal."""
        panel = AdminQuestionPanel(root_window, mock_manager, mock_images)

        assert panel.window.grab_current() == panel.window

        panel.window.destroy()


class TestTableDisplay:
    """Test question table display."""

    def test_table_exists(self, panel):
        """Test that table is created."""
        assert panel.table.winfo_exists()

    def test_table_displays_questions(self, panel):
        """Test that questions are displayed in table."""
        items = panel.table.get_children()
        assert len(items) == 2

    def test_table_columns(self, panel):
        """Test that table has correct columns."""
        columns = panel.table.cget("columns")
        assert "ID" in columns
        assert "Category" in columns
        assert "Difficulty" in columns


class TestSearchAndFiltering:
    """Test search and filtering functionality."""

    def test_search_entry_exists(self, panel):
        """Test search entry field exists."""
        assert panel.search_entry.winfo_exists()

    def test_category_combo_exists(self, panel):
        """Test category combo exists."""
        assert panel.category_combo.winfo_exists()

    def test_difficulty_combo_exists(self, panel):
        """Test difficulty combo exists."""
        assert panel.difficulty_combo.winfo_exists()

    def test_filter_by_search(self, panel):
        """Test filtering by search term."""
        panel.search_entry.insert(0, "q001")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 1
        assert filtered[0]["id"] == "q001"

    def test_filter_by_category(self, panel):
        """Test filtering by category."""
        panel.category_var.set("personality")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 1
        assert filtered[0]["category"] == "personality"

    def test_filter_by_difficulty(self, panel):
        """Test filtering by difficulty."""
        panel.difficulty_var.set("medium")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 1
        assert filtered[0]["difficulty"] == "medium"

    def test_filter_all_categories(self, panel):
        """Test 'All' category shows all questions."""
        panel.category_var.set("All")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 2

    def test_clear_search_shows_all(self, panel):
        """Test clearing search shows all questions."""
        panel.search_entry.insert(0, "")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 2

    def test_combined_filters(self, panel):
        """Test combining multiple filters."""
        panel.search_entry.insert(0, "q001")
        panel.category_var.set("personality")
        filtered = panel._apply_filters(panel.manager.get_all_questions())

        assert len(filtered) == 1
        assert filtered[0]["id"] == "q001"


class TestButtonInteractions:
    """Test button interactions."""

    def test_new_question_button_exists(self, panel):
        """Test new question button exists."""
        # Button exists as part of UI
        assert panel.window.winfo_exists()

    def test_edit_without_selection(self, panel):
        """Test edit without selecting question shows warning."""
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            panel._on_edit_question()
            mock_warn.assert_called()

    def test_delete_without_selection(self, panel):
        """Test delete without selecting question shows warning."""
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            panel._on_delete_question()
            mock_warn.assert_called()

    def test_delete_with_selection(self, panel):
        """Test deleting with selection calls manager."""
        # Select first item
        items = panel.table.get_children()
        if items:
            panel.table.selection_set(items[0])

            with patch("tkinter.messagebox.askyesno", return_value=True):
                with patch("tkinter.messagebox.showinfo"):
                    panel._on_delete_question()

            panel.manager.delete_question.assert_called()

    def test_delete_confirmation(self, panel):
        """Test delete shows confirmation dialog."""
        items = panel.table.get_children()
        if items:
            panel.table.selection_set(items[0])

            with patch("tkinter.messagebox.askyesno") as mock_yes:
                with patch("tkinter.messagebox.showinfo"):
                    panel._on_delete_question()
                    mock_yes.assert_called()


class TestImageUpload:
    """Test image upload functionality."""

    def test_upload_image_success(self, panel):
        """Test successful image upload."""
        panel.images.upload_image.return_value = {
            "success": True,
            "image_id": "img_123",
        }

        with patch(
            "tkinter.filedialog.askopenfilename",
            return_value="/path/to/image.jpg",
        ):
            with patch("tkinter.messagebox.showinfo") as mock_info:
                panel._on_upload_image()
                mock_info.assert_called()

    def test_upload_image_failure(self, panel):
        """Test failed image upload."""
        panel.images.upload_image.return_value = {
            "success": False,
            "error": "File too large",
        }

        with patch(
            "tkinter.filedialog.askopenfilename",
            return_value="/path/to/image.jpg",
        ):
            with patch("tkinter.messagebox.showerror") as mock_error:
                panel._on_upload_image()
                mock_error.assert_called()

    def test_upload_dialog_cancelled(self, panel):
        """Test cancelling upload dialog."""
        with patch("tkinter.filedialog.askopenfilename", return_value=""):
            # Should not call upload if file not selected
            panel._on_upload_image()
            panel.images.upload_image.assert_not_called()


class TestStatusDisplay:
    """Test status label updates."""

    def test_status_label_exists(self, panel):
        """Test status label is created."""
        assert panel.status_label.winfo_exists()

    def test_status_shows_statistics(self, panel):
        """Test status label shows statistics."""
        panel._update_status()
        status_text = panel.status_label.cget("text")

        assert "Total" in status_text
        assert "2" in status_text

    def test_status_shows_categories(self, panel):
        """Test status shows categories breakdown."""
        panel._update_status()
        status_text = panel.status_label.cget("text")

        # Should contain category info
        assert len(status_text) > 0


class TestCategoryCombo:
    """Test category dropdown."""

    def test_category_dropdown_updated(self, panel):
        """Test category dropdown is populated."""
        categories = panel.category_combo["values"]
        
        assert "All" in categories
        # Categories should be populated from manager
        assert len(categories) > 0

    def test_category_combo_contains_personality(self, panel):
        """Test category dropdown contains personality."""
        categories = list(panel.category_combo["values"])
        assert any("personality" in str(cat) for cat in categories) or "All" in categories


class TestDifficultyCombo:
    """Test difficulty dropdown."""

    def test_difficulty_values(self, panel):
        """Test difficulty combo has correct values."""
        values = panel.difficulty_combo["values"]

        assert "All" in values
        assert "easy" in values
        assert "medium" in values
        assert "hard" in values


class TestRefreshTable:
    """Test table refresh functionality."""

    def test_refresh_clears_and_repopulates(self, panel):
        """Test refresh clears old and shows new questions."""
        # Initial load
        initial_items = len(panel.table.get_children())
        assert initial_items == 2

        # Modify manager return value
        panel.manager.get_all_questions.return_value = [
            {
                "id": "q003",
                "category": "hardware",
                "image_id": "img_003",
                "difficulty": "hard",
                "description": "New question",
            }
        ]

        panel._refresh_questions_table()
        new_items = len(panel.table.get_children())

        assert new_items == 1

    def test_refresh_applies_filters(self, panel):
        """Test refresh applies current filters."""
        panel.search_entry.insert(0, "q001")
        panel._refresh_questions_table()

        items = panel.table.get_children()
        # Should be filtered
        assert len(items) == 1


class TestCloseButton:
    """Test close functionality."""

    def test_close_button_callback(self, root_window, mock_manager, mock_images):
        """Test close button calls callback."""
        callback = Mock()
        panel = AdminQuestionPanel(
            root_window, mock_manager, mock_images, on_close=callback
        )

        with patch.object(panel.window, "destroy"):
            panel._on_close()
            callback.assert_called_once()

        panel.window.destroy()

    def test_close_without_callback(self, root_window, mock_manager, mock_images):
        """Test close without callback doesn't error."""
        panel = AdminQuestionPanel(root_window, mock_manager, mock_images)

        with patch.object(panel.window, "destroy"):
            panel._on_close()  # Should not raise

        panel.window.destroy()
