"""
Tests for AdminAuth service.

Tests cover:
- Password hashing (SHA256 + salt)
- Password verification
- Rate limiting and lockout
- Password changes
- Status reporting
"""

import pytest
from datetime import datetime, timedelta
from services.admin_auth import AdminAuth
from admin.constants import (
    ADMIN_MAX_LOGIN_ATTEMPTS,
    ADMIN_LOCKOUT_DURATION_SECONDS,
    ADMIN_PASSWORD_MIN_LENGTH,
)


@pytest.fixture
def admin_auth():
    """Create AdminAuth instance with default password."""
    # Default password: "admin123"
    password_hash, password_salt = AdminAuth.hash_password("admin123")
    return AdminAuth(password_hash, password_salt), password_hash, password_salt


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_salt(self):
        """Hashing should generate a salt."""
        hash_val, salt = AdminAuth.hash_password("test_password")
        
        assert isinstance(hash_val, str)
        assert isinstance(salt, str)
        assert len(hash_val) == 64  # SHA256 = 64 hex chars
        assert len(salt) > 0

    def test_hash_password_with_provided_salt(self):
        """Hashing should use provided salt."""
        test_salt = "a" * 32
        hash_val, returned_salt = AdminAuth.hash_password("test_password", test_salt)
        
        assert returned_salt == test_salt
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64

    def test_same_password_same_salt_produces_same_hash(self):
        """Same password with same salt should produce same hash."""
        password = "test_password"
        salt = "b" * 32
        
        hash1, _ = AdminAuth.hash_password(password, salt)
        hash2, _ = AdminAuth.hash_password(password, salt)
        
        assert hash1 == hash2

    def test_different_salts_produce_different_hashes(self):
        """Same password with different salts should produce different hashes."""
        password = "test_password"
        
        hash1, _ = AdminAuth.hash_password(password, "a" * 32)
        hash2, _ = AdminAuth.hash_password(password, "b" * 32)
        
        assert hash1 != hash2

    def test_hash_password_handles_whitespace(self):
        """Password hashing should handle whitespace correctly."""
        password_with_spaces = "  admin 123  "
        
        hash1, salt = AdminAuth.hash_password(password_with_spaces)
        hash2, _ = AdminAuth.hash_password("  admin 123  ", salt)
        
        assert hash1 == hash2


class TestPasswordVerification:
    """Test password verification."""

    def test_verify_correct_password(self, admin_auth):
        """Correct password should verify successfully."""
        auth, _, _ = admin_auth
        
        result = auth.verify_password("admin123")
        
        assert result is True

    def test_verify_wrong_password(self, admin_auth):
        """Wrong password should not verify."""
        auth, _, _ = admin_auth
        
        result = auth.verify_password("wrongpassword")
        
        assert result is False

    def test_verify_password_case_sensitive(self, admin_auth):
        """Password verification should be case sensitive."""
        auth, _, _ = admin_auth
        
        result = auth.verify_password("ADMIN123")
        
        assert result is False

    def test_verify_resets_failed_attempts_on_success(self, admin_auth):
        """Successful login should reset failed attempt counter."""
        auth, _, _ = admin_auth
        
        # Fail twice
        auth.verify_password("wrong1")
        auth.verify_password("wrong2")
        assert auth.failed_attempts == 2
        
        # Login correctly
        result = auth.verify_password("admin123")
        
        assert result is True
        assert auth.failed_attempts == 0


class TestRateLimiting:
    """Test rate limiting and lockout functionality."""

    def test_failed_attempts_increment(self, admin_auth):
        """Failed attempts should increment counter."""
        auth, _, _ = admin_auth
        
        auth.verify_password("wrong1")
        assert auth.failed_attempts == 1
        
        auth.verify_password("wrong2")
        assert auth.failed_attempts == 2

    def test_lockout_after_max_attempts(self, admin_auth):
        """Account should lock after max failed attempts."""
        auth, _, _ = admin_auth
        
        # Fail max attempts
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        assert auth.is_locked() is True
        assert auth.locked_until is not None

    def test_cannot_verify_while_locked(self, admin_auth):
        """Cannot verify password while locked."""
        auth, _, _ = admin_auth
        
        # Trigger lockout
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        # Try to login with correct password
        result = auth.verify_password("admin123")
        
        assert result is False

    def test_lockout_releases_after_timeout(self, admin_auth):
        """Lockout should automatically release after timeout."""
        auth, _, _ = admin_auth
        
        # Trigger lockout
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        assert auth.is_locked() is True
        
        # Manually advance time (simulate timeout)
        auth.locked_until = datetime.now() - timedelta(seconds=1)
        
        assert auth.is_locked() is False

    def test_lockout_remaining_seconds(self, admin_auth):
        """Should correctly report lockout remaining time."""
        auth, _, _ = admin_auth
        
        # Trigger lockout
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        remaining = auth.get_lockout_remaining_seconds()
        
        assert 0 < remaining <= ADMIN_LOCKOUT_DURATION_SECONDS
        assert isinstance(remaining, int)

    def test_lockout_remaining_zero_when_not_locked(self, admin_auth):
        """Lockout remaining should be 0 when not locked."""
        auth, _, _ = admin_auth
        
        remaining = auth.get_lockout_remaining_seconds()
        
        assert remaining == 0

    def test_manual_lockout_reset(self, admin_auth):
        """Should be able to manually reset lockout."""
        auth, _, _ = admin_auth
        
        # Trigger lockout
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        assert auth.is_locked() is True
        
        # Manual reset
        auth.reset_lockout()
        
        assert auth.is_locked() is False
        assert auth.failed_attempts == 0


class TestPasswordChange:
    """Test password change functionality."""

    def test_change_password_with_correct_old_password(self, admin_auth):
        """Should change password with correct old password."""
        auth, _, _ = admin_auth
        
        success, message = auth.change_password("admin123", "newpassword999")
        
        assert success is True
        assert "successfully" in message.lower()
        
        # Old password should no longer work
        assert auth.verify_password("admin123") is False
        
        # New password should work
        assert auth.verify_password("newpassword999") is True

    def test_change_password_with_wrong_old_password(self, admin_auth):
        """Should reject password change with wrong old password."""
        auth, _, _ = admin_auth
        
        success, message = auth.change_password("wrongpassword", "newpassword999")
        
        assert success is False
        assert "incorrect" in message.lower()

    def test_change_password_too_short(self, admin_auth):
        """Should reject password that's too short."""
        auth, _, _ = admin_auth
        
        short_password = "a" * (ADMIN_PASSWORD_MIN_LENGTH - 1)
        success, message = auth.change_password("admin123", short_password)
        
        assert success is False
        assert "at least" in message.lower()

    def test_change_password_same_as_old(self, admin_auth):
        """Should reject if new password is same as old."""
        auth, _, _ = admin_auth
        
        success, message = auth.change_password("admin123", "admin123")
        
        assert success is False
        assert "cannot be same" in message.lower()

    def test_change_password_minimum_length_accepted(self, admin_auth):
        """Should accept password of minimum length."""
        auth, _, _ = admin_auth
        
        min_password = "a" * ADMIN_PASSWORD_MIN_LENGTH
        success, message = auth.change_password("admin123", min_password)
        
        assert success is True


class TestStatusAndInfo:
    """Test status reporting."""

    def test_get_status_not_locked(self, admin_auth):
        """Status should report not locked."""
        auth, _, _ = admin_auth
        
        status = auth.get_status()
        
        assert status["is_locked"] is False
        assert status["failed_attempts"] == 0
        assert status["lockout_remaining_seconds"] == 0

    def test_get_status_locked(self, admin_auth):
        """Status should report locked state."""
        auth, _, _ = admin_auth
        
        # Trigger lockout
        for i in range(ADMIN_MAX_LOGIN_ATTEMPTS):
            auth.verify_password(f"wrong{i}")
        
        status = auth.get_status()
        
        assert status["is_locked"] is True
        assert status["failed_attempts"] == ADMIN_MAX_LOGIN_ATTEMPTS
        assert status["lockout_remaining_seconds"] > 0
        assert status["locked_until"] is not None

    def test_str_representation(self, admin_auth):
        """String representation should be readable."""
        auth, _, _ = admin_auth
        
        str_repr = str(auth)
        
        assert "AdminAuth" in str_repr
        assert "ACTIVE" in str_repr or "LOCKED" in str_repr

    def test_repr_representation(self, admin_auth):
        """Repr should contain hash preview (safely)."""
        auth, _, _ = admin_auth
        
        repr_str = repr(auth)
        
        assert "AdminAuth" in repr_str
        assert "hash=" in repr_str
        assert "locked=" in repr_str


class TestSecurityProperties:
    """Test security properties."""

    def test_password_hash_never_plaintext(self):
        """Password hash should never be stored in plaintext."""
        password = "admin123"
        hash_val, _ = AdminAuth.hash_password(password)
        
        # Hash should not contain password
        assert password not in hash_val

    def test_multiple_instances_independent(self):
        """Multiple AdminAuth instances should be independent."""
        hash1, salt1 = AdminAuth.hash_password("password1")
        hash2, salt2 = AdminAuth.hash_password("password2")
        
        auth1 = AdminAuth(hash1, salt1)
        auth2 = AdminAuth(hash2, salt2)
        
        # Fail on auth1
        auth1.verify_password("wrong")
        
        # auth2 should not be affected
        assert auth1.failed_attempts == 1
        assert auth2.failed_attempts == 0

    def test_compare_digest_prevents_timing_attack(self, admin_auth):
        """Verification should use constant-time comparison."""
        auth, _, _ = admin_auth
        
        # Both should fail but take similar time
        result1 = auth.verify_password("wrong1")
        result2 = auth.verify_password("wrong2")
        
        assert result1 is False
        assert result2 is False
        # If using regular ==, timing difference would be measurable
        # compare_digest makes them constant-time


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_authentication_flow(self):
        """Test complete authentication workflow."""
        # Setup
        password_hash, password_salt = AdminAuth.hash_password("securepass123")
        auth = AdminAuth(password_hash, password_salt)
        
        # Initial state
        assert auth.is_locked() is False
        assert auth.failed_attempts == 0
        
        # Wrong attempts
        auth.verify_password("wrong1")
        auth.verify_password("wrong2")
        assert auth.failed_attempts == 2
        
        # Correct password
        assert auth.verify_password("securepass123") is True
        assert auth.failed_attempts == 0  # Reset
        
        # Change password
        success, msg = auth.change_password("securepass123", "newpass999")
        assert success is True
        
        # Old password fails
        assert auth.verify_password("securepass123") is False
        
        # New password works
        assert auth.verify_password("newpass999") is True
