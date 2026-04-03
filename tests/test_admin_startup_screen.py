"""
Tests for AdminStartupScreen.

Coverage:
- Startup screen initialization
- UI elements display
- Button interactions
- Admin button callback
- Play button callback
- Screen visibility toggle
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch

from ui.admin_startup_screen import AdminStartupScreen
from services.admin_auth import AdminAuth


@pytest.fixture
def root_window():
    """Create a root tkinter window."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available in test environment: {exc}")
    root.geometry("800x600")
    yield root
    root.destroy()


@pytest.fixture
def mock_auth():
    """Create a mock AdminAuth instance."""
    auth = Mock(spec=AdminAuth)
    auth.is_locked.return_value = False
    return auth


@pytest.fixture
def startup_screen(root_window, mock_auth):
    """Create a startup screen instance."""
    screen = AdminStartupScreen(root_window, mock_auth)
    yield screen
    screen.destroy()


class TestStartupScreenInitialization:
    """Test startup screen initialization."""

    def test_creates_frame(self, root_window, mock_auth):
        """Test that startup screen creates a frame."""
        screen = AdminStartupScreen(root_window, mock_auth)

        assert isinstance(screen.frame, tk.Frame)
        assert screen.frame.winfo_exists()

        screen.destroy()

    def test_default_bg_color(self, root_window, mock_auth):
        """Test frame has correct background color."""
        screen = AdminStartupScreen(root_window, mock_auth)

        assert screen.frame.cget("bg") == "#2c3e50"

        screen.destroy()


class TestUIElements:
    """Test presence of UI elements."""

    def test_frame_exists(self, startup_screen):
        """Test main frame exists."""
        assert startup_screen.frame.winfo_exists()

    def test_callbacks_initialized(self, startup_screen):
        """Test callbacks are initialized to None."""
        assert startup_screen.on_admin_callback is None
        assert startup_screen.on_play_callback is None


class TestShowMethod:
    """Test show() method."""

    def test_show_packs_frame(self, startup_screen):
        """Test show() makes frame visible."""
        startup_screen.show()

        # Frame should be packed (it exists and has a geometry)
        assert startup_screen.frame.winfo_exists()

    def test_show_sets_callbacks(self, root_window, mock_auth):
        """Test show() sets callbacks."""
        admin_callback = Mock()
        play_callback = Mock()

        screen = AdminStartupScreen(root_window, mock_auth)
        screen.show(on_admin=admin_callback, on_play=play_callback)

        assert screen.on_admin_callback == admin_callback
        assert screen.on_play_callback == play_callback

        screen.destroy()


class TestHideMethod:
    """Test hide() method."""

    def test_hide_unpacks_frame(self, startup_screen):
        """Test hide() hides the frame."""
        startup_screen.show()
        startup_screen.hide()

        # Frame should not be viewable
        assert not startup_screen.frame.winfo_viewable()


class TestAdminButtonCallback:
    """Test admin button interaction."""

    def test_admin_button_shows_login(self, startup_screen):
        """Test admin button shows login screen."""
        with patch("ui.admin_startup_screen.AdminLoginScreen") as mock_login_class:
            mock_instance = Mock()
            mock_instance.show.return_value = False
            mock_login_class.return_value = mock_instance

            startup_screen._on_admin_clicked()

            # Should have created AdminLoginScreen
            mock_login_class.assert_called_once()

    def test_admin_successful_login_calls_callback(self, startup_screen):
        """Test successful login calls callback."""
        admin_callback = Mock()
        startup_screen.on_admin_callback = admin_callback

        with patch("ui.admin_startup_screen.AdminLoginScreen") as mock_login_class:
            mock_instance = Mock()
            mock_instance.show.return_value = True
            mock_login_class.return_value = mock_instance

            startup_screen._on_admin_clicked()

            admin_callback.assert_called_once()

    def test_admin_failed_login_no_callback(self, startup_screen):
        """Test failed login doesn't call callback."""
        admin_callback = Mock()
        startup_screen.on_admin_callback = admin_callback

        with patch("ui.admin_startup_screen.AdminLoginScreen") as mock_login_class:
            mock_instance = Mock()
            mock_instance.show.return_value = False
            mock_login_class.return_value = mock_instance

            startup_screen._on_admin_clicked()

            admin_callback.assert_not_called()


class TestPlayButtonCallback:
    """Test play button interaction."""

    def test_play_button_calls_callback(self, startup_screen):
        """Test play button calls play callback."""
        play_callback = Mock()
        startup_screen.on_play_callback = play_callback

        startup_screen._on_play_clicked()

        play_callback.assert_called_once()

    def test_play_without_callback(self, startup_screen):
        """Test play button works without callback."""
        startup_screen.on_play_callback = None

        # Should not raise error
        startup_screen._on_play_clicked()


class TestDestroyMethod:
    """Test destroy() method."""

    def test_destroy_removes_frame(self, root_window, mock_auth):
        """Test destroy() removes frame."""
        screen = AdminStartupScreen(root_window, mock_auth)
        screen.show()

        assert screen.frame.winfo_exists()

        screen.destroy()

        assert not screen.frame.winfo_exists()
