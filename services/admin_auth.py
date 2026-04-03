"""
AdminAuth Service - Handles administrator authentication with rate limiting.

Security Features:
- SHA256 password hashing with salt
- Rate limiting (3 failed attempts = 5 minute lockout)
- Time-based lockout mechanism
- Secure password change
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional

from admin.constants import (
    ADMIN_MAX_LOGIN_ATTEMPTS,
    ADMIN_LOCKOUT_DURATION_SECONDS,
    ADMIN_PASSWORD_MIN_LENGTH,
)

logger = logging.getLogger(__name__)


class AdminAuth:
    """Manages secure authentication for admin panel."""

    def __init__(self, password_hash: str, password_salt: str):
        """
        Initialize AdminAuth with stored password hash and salt.

        Args:
            password_hash: SHA256 hash of the admin password
            password_salt: Salt used with the password hash
        """
        self.stored_password_hash = password_hash
        self.stored_password_salt = password_salt
        
        self.failed_attempts = 0
        self.locked_until: Optional[datetime] = None
        
        logger.debug("AdminAuth initialized")

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password using SHA256 with salt.

        Args:
            password: Plain text password to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (hash, salt)

        Example:
            >>> hash_val, salt = AdminAuth.hash_password("admin123")
            >>> # Both hash_val and salt are hex strings
        """
        if salt is None:
            salt = secrets.token_hex(16)  # 32 character hex string
        
        # Normalize password
        password_normalized = password.strip().encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # SHA256 hash
        hash_obj = hashlib.sha256(salt_bytes + password_normalized)
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt

    def is_locked(self) -> bool:
        """
        Check if admin account is locked due to failed login attempts.

        Returns:
            True if locked, False otherwise
        """
        if self.locked_until is None:
            return False
        
        if datetime.now() > self.locked_until:
            # Lockout expired
            self.locked_until = None
            self.failed_attempts = 0
            return False
        
        return True

    def get_lockout_remaining_seconds(self) -> int:
        """
        Get remaining lockout time in seconds.

        Returns:
            Seconds until account is unlocked, 0 if not locked
        """
        if not self.is_locked():
            return 0
        
        remaining = self.locked_until - datetime.now()
        return max(0, int(remaining.total_seconds()))

    def _lock_for_duration(self, seconds: int) -> None:
        """
        Lock the admin account for specified duration.

        Args:
            seconds: Duration of lockout in seconds
        """
        self.locked_until = datetime.now() + timedelta(seconds=seconds)
        logger.warning(
            f"Admin account locked for {seconds} seconds until {self.locked_until}"
        )

    def verify_password(self, password: str) -> bool:
        """
        Verify the provided password against stored hash.

        Implements rate limiting:
        - 3 failed attempts = 5 minute lockout
        - Lockout expires automatically

        Args:
            password: Password to verify

        Returns:
            True if password is correct and account is not locked, False otherwise

        Security Notes:
            - Uses constant-time comparison to prevent timing attacks
            - Uses salted SHA256 hash, not vulnerable to rainbow tables
            - Implements rate limiting to prevent brute force
        """
        # Check if locked
        if self.is_locked():
            remaining = self.get_lockout_remaining_seconds()
            logger.warning(
                f"Admin login attempt while locked. {remaining}s remaining."
            )
            return False

        # Hash the provided password with stored salt
        provided_hash, _ = self.hash_password(password, self.stored_password_salt)

        # Constant-time comparison (prevents timing attack)
        is_correct = secrets.compare_digest(provided_hash, self.stored_password_hash)

        if is_correct:
            # Successful login - reset counters
            self.failed_attempts = 0
            self.locked_until = None
            logger.info("Admin authentication successful")
            return True
        else:
            # Failed attempt - increment counter
            self.failed_attempts += 1
            logger.warning(
                f"Failed admin login attempt {self.failed_attempts}/{ADMIN_MAX_LOGIN_ATTEMPTS}"
            )

            # Check if we should lock
            if self.failed_attempts >= ADMIN_MAX_LOGIN_ATTEMPTS:
                self._lock_for_duration(ADMIN_LOCKOUT_DURATION_SECONDS)
                logger.error("Admin account locked due to too many failed attempts")
                return False

            return False

    def change_password(
        self, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        """
        Change the admin password.

        Args:
            old_password: Current password (for verification)
            new_password: New password to set

        Returns:
            Tuple of (success: bool, message: str)

        Validation:
            - Old password must be correct
            - New password must meet minimum length requirement
            - New password cannot be same as old password
        """
        # Verify old password
        if not self.verify_password(old_password):
            return False, "Old password is incorrect"

        # Validate new password length
        if len(new_password) < ADMIN_PASSWORD_MIN_LENGTH:
            return (
                False,
                f"New password must be at least {ADMIN_PASSWORD_MIN_LENGTH} characters",
            )

        # Check if new password is same as old
        new_hash, _ = self.hash_password(new_password, self.stored_password_salt)
        if new_hash == self.stored_password_hash:
            return False, "New password cannot be same as old password"

        # Generate new salt and hash for new password
        new_hash, new_salt = self.hash_password(new_password)

        # Update stored values
        self.stored_password_hash = new_hash
        self.stored_password_salt = new_salt

        logger.info("Admin password changed successfully")
        return True, "Password changed successfully"

    def reset_lockout(self) -> None:
        """
        Manually reset lockout (for admin intervention).

        Should only be called by system/operator, not by authentication flow.
        """
        self.failed_attempts = 0
        self.locked_until = None
        logger.info("Admin lockout manually reset")

    def get_status(self) -> dict:
        """
        Get current authentication status.

        Returns:
            Dictionary with authentication status information
        """
        return {
            "is_locked": self.is_locked(),
            "failed_attempts": self.failed_attempts,
            "max_attempts": ADMIN_MAX_LOGIN_ATTEMPTS,
            "lockout_remaining_seconds": self.get_lockout_remaining_seconds(),
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
        }

    def __str__(self) -> str:
        """String representation."""
        status = "LOCKED" if self.is_locked() else "ACTIVE"
        return f"AdminAuth({status}, attempts={self.failed_attempts})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"AdminAuth(hash={self.stored_password_hash[:8]}..., "
            f"locked={self.is_locked()})"
        )
