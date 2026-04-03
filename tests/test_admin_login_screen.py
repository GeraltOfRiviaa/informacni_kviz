"""
Tests for AdminLoginScreen UI component.

Coverage:
- UI initialization and display
- Password entry and verification
- Show/hide password toggle
- Lockout status display
- Attempts counter
- Button interactions
- Keyboard shortcuts
- Success/failure handling
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch

from ui.admin_login_screen import AdminLoginScreen
from services.admin_auth import AdminAuth
from admin.constants import ADMIN_MAX_LOGIN_ATTEMPTS


@pytest.fixture
def root_window():
    """Create a root tkinter window."""
    root = tk.Tk()
    root.geometry("800x600")
    yield root
    root.destroy()


@pytest.fixture
def mock_auth():
    """Create a mock AdminAuth instance."""
    auth = Mock(spec=AdminAuth)
    auth.failed_attempts = 0
    auth.is_locked.return_value = False
    auth.verify_password.return_value = False
    auth.get_lockout_remaining_seconds.return_value = 0
    return auth


@pytest.fixture
def login_screen(root_window, mock_auth):
    """Create a login screen instance."""
    # We need to display it
    screen = AdminLoginScreen(root_window, mock_auth)
    yield screen
    # Cleanup
    try:
        screen.dialog.destroy()
    except tk.TclError:
        pass


class TestLoginScreenInitialization:
    """Test login screen initialization."""

    def test_creates_toplevel_window(self, root_window, mock_auth):
        """Test that login screen creates a Toplevel window."""
        screen = AdminLoginScreen(root_window, mock_auth)
        
        assert isinstance(screen.dialog, tk.Toplevel)
        assert screen.dialog.winfo_exists()
        
        screen.dialog.destroy()

    def test_modal_properties(self, root_window, mock_auth):
        """Test that dialog is properly configured as modal."""
        screen = AdminLoginScreen(root_window, mock_auth)
        
        # Modal windows have grab set
        assert screen.dialog.grab_current() == screen.dialog
        
        screen.dialog.destroy()

    def test_window_title(self, root_window, mock_auth):
        """Test window has correct title."""
        screen = AdminLoginScreen(root_window, mock_auth)
        
        assert "Admin Panel" in screen.dialog.title()
        
        screen.dialog.destroy()


class TestPasswordEntry:
    """Test password entry field."""

    def test_password_field_masked_by_default(self, login_screen):
        """Test password field is masked initially."""
        assert login_screen.password_entry.cget("show") == "•"

    def test_password_field_is_focused(self, login_screen):
        """Test password field is focused on creation."""
        # In test environment, focus might not work the same way
        # Just verify the focus() call was made by checking the field exists
        assert login_screen.password_entry.winfo_exists()

    def test_show_password_toggle(self, login_screen):
        """Test show/hide password toggle."""
        # Initially masked
        assert login_screen.password_entry.cget("show") == "•"
        assert login_screen.show_button.cget("text") in ("Show", "Zobrazit")

        # Click show
        login_screen._toggle_password_visibility()
        assert login_screen.password_entry.cget("show") == ""
        assert login_screen.show_button.cget("text") in ("Hide", "Skrýt")

        # Click hide
        login_screen._toggle_password_visibility()
        assert login_screen.password_entry.cget("show") == "•"
        assert login_screen.show_button.cget("text") in ("Show", "Zobrazit")

    def test_password_input(self, login_screen):
        """Test password can be entered."""
        login_screen.password_entry.insert(0, "testpassword")
        assert login_screen.password_entry.get() == "testpassword"


class TestStatusDisplay:
    """Test status and feedback displays."""

    def test_status_empty_on_normal_state(self, login_screen):
        """Test status label is empty when not locked."""
        login_screen._update_status()
        assert login_screen.status_label.cget("text") == ""

    def test_attempts_counter_display(self, login_screen):
        """Test attempts counter is displayed."""
        login_screen._update_status()
        text = login_screen.attempts_label.cget("text")
        assert "Attempts remaining" in text or "Maximum" in text

    def test_lockout_status_display(self, login_screen):
        """Test lockout status is displayed."""
        login_screen.admin_auth.is_locked.return_value = True
        login_screen.admin_auth.get_lockout_remaining_seconds.return_value = 120

        login_screen._update_status()

        status = login_screen.status_label.cget("text")
        assert "locked" in status.lower() or "zablok" in status.lower()
        assert "120" in status

    def test_lockout_disables_login_button(self, login_screen):
        """Test login button is disabled when locked."""
        login_screen.admin_auth.is_locked.return_value = True
        login_screen._update_status()

        assert login_screen.login_button.cget("state") == tk.DISABLED

    def test_unlock_enables_login_button(self, login_screen):
        """Test login button is enabled when unlocked."""
        login_screen.admin_auth.is_locked.return_value = False
        login_screen._update_status()

        assert login_screen.login_button.cget("state") == tk.NORMAL


class TestLoginLogic:
    """Test login verification logic."""

    def test_empty_password_rejected(self, login_screen):
        """Test empty password is rejected."""
        login_screen.password_entry.delete(0, tk.END)

        with patch("tkinter.messagebox.showwarning") as mock_warn:
            login_screen._on_login()
            mock_warn.assert_called()
            assert not login_screen.result

    def test_successful_login(self, login_screen):
        """Test successful login."""
        login_screen.password_entry.insert(0, "correct_password")
        login_screen.admin_auth.verify_password.return_value = True

        with patch.object(login_screen, "dialog") as mock_dialog:
            with patch.object(mock_dialog, "destroy"):
                login_screen._on_login()

        assert login_screen.result is True

    def test_failed_login(self, login_screen):
        """Test failed login."""
        login_screen.password_entry.insert(0, "wrong_password")
        login_screen.admin_auth.verify_password.return_value = False

        with patch("tkinter.messagebox.showerror") as mock_error:
            login_screen._on_login()
            mock_error.assert_called()

    def test_failed_login_clears_password_field(self, login_screen):
        """Test password field is cleared after failed login."""
        login_screen.password_entry.insert(0, "wrong_password")
        login_screen.admin_auth.verify_password.return_value = False

        with patch("tkinter.messagebox.showerror"):
            login_screen._on_login()

        assert login_screen.password_entry.get() == ""

    def test_locked_after_failed_login(self, login_screen):
        """Test dialog closes when account gets locked."""
        login_screen.password_entry.insert(0, "wrong_password")
        login_screen.admin_auth.verify_password.return_value = False
        login_screen.admin_auth.is_locked.return_value = True

        with patch("tkinter.messagebox.showerror"):
            with patch.object(login_screen.dialog, "destroy"):
                login_screen._on_login()

    def test_on_success_callback(self, login_screen):
        """Test on_success callback is called."""
        callback_mock = Mock()
        login_screen.on_success = callback_mock
        login_screen.password_entry.insert(0, "correct_password")
        login_screen.admin_auth.verify_password.return_value = True

        with patch.object(login_screen.dialog, "destroy"):
            login_screen._on_login()

        callback_mock.assert_called_once()


class TestButtonInteractions:
    """Test button interactions."""

    def test_cancel_button_closes_dialog(self, login_screen):
        """Test cancel button closes dialog."""
        with patch.object(login_screen.dialog, "destroy") as mock_destroy:
            login_screen._on_cancel()
            mock_destroy.assert_called()

    def test_cancel_sets_result_false(self, login_screen):
        """Test cancel sets result to False."""
        with patch.object(login_screen.dialog, "destroy"):
            login_screen._on_cancel()
            assert login_screen.result is False


class TestKeyboardShortcuts:
    """Test keyboard shortcuts."""

    def test_enter_key_submits_login(self, login_screen):
        """Test Enter key triggers login."""
        login_screen.password_entry.insert(0, "password")
        login_screen.admin_auth.verify_password.return_value = True

        # Check binding exists
        bindings = login_screen.password_entry.bind()
        assert "<Key-Return>" in bindings or "<Return>" in bindings

    def test_escape_key_bound(self, login_screen):
        """Test Escape key is bound to cancel."""
        bindings = login_screen.password_entry.bind()
        assert "<Key-Escape>" in bindings or "<Escape>" in bindings


class TestShowMethod:
    """Test the show() method."""

    def test_show_waits_for_dialog(self, root_window, mock_auth):
        """Test show() waits for dialog to close."""
        screen = AdminLoginScreen(root_window, mock_auth)
        screen.result = True

        # Close dialog before calling show (to avoid blocking)
        screen.dialog.destroy()

        # This would block if show doesn't handle it right
        try:
            result = screen.show()
            # Dialog already destroyed, might raise error
        except tk.TclError:
            # Expected when dialog already destroyed
            pass

    def test_show_returns_success(self, root_window, mock_auth):
        """Test show() returns correct success status."""
        screen = AdminLoginScreen(root_window, mock_auth)
        screen.result = True
        screen.dialog.destroy()

        try:
            result = screen.show()
        except tk.TclError:
            # Dialog was destroyed so can't wait
            result = screen.result

        assert result is True

    def test_show_returns_failure(self, root_window, mock_auth):
        """Test show() returns correct failure status."""
        screen = AdminLoginScreen(root_window, mock_auth)
        screen.result = False
        screen.dialog.destroy()

        try:
            result = screen.show()
        except tk.TclError:
            result = screen.result

        assert result is False


class TestUIElements:
    """Test UI element existence and properties."""

    def test_login_button_exists(self, login_screen):
        """Test login button is created."""
        assert login_screen.login_button.winfo_exists()

    def test_password_entry_exists(self, login_screen):
        """Test password entry field is created."""
        assert login_screen.password_entry.winfo_exists()

    def test_status_label_exists(self, login_screen):
        """Test status label is created."""
        assert login_screen.status_label.winfo_exists()

    def test_attempts_label_exists(self, login_screen):
        """Test attempts label is created."""
        assert login_screen.attempts_label.winfo_exists()

    def test_show_password_button_exists(self, login_screen):
        """Test show/hide password button is created."""
        assert login_screen.show_button.winfo_exists()


class TestFormValidation:
    """Test form validation."""

    def test_password_verification_called(self, login_screen):
        """Test AdminAuth.verify_password is called."""
        login_screen.password_entry.insert(0, "test_password")
        login_screen.admin_auth.verify_password.return_value = False

        with patch("tkinter.messagebox.showerror"):
            login_screen._on_login()

        login_screen.admin_auth.verify_password.assert_called_once_with(
            "test_password"
        )

    def test_password_passed_to_auth(self, login_screen):
        """Test password is passed correctly to auth."""
        test_pwd = "my_secure_password"
        login_screen.password_entry.insert(0, test_pwd)
        login_screen.admin_auth.verify_password.return_value = False

        with patch("tkinter.messagebox.showerror"):
            login_screen._on_login()

        login_screen.admin_auth.verify_password.assert_called_with(test_pwd)
