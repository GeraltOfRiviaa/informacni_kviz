"""
AnswerChecker - Validates answers with security (hashing, normalization).
Core security component for the quiz application.
"""

import hashlib
import logging
import unicodedata
from typing import Tuple


logger = logging.getLogger(__name__)


class AnswerChecker:
    """
    Validates user answers securely using normalization and hashing.
    
    Security Features:
    - Text normalization (lowercase, remove diacritics, remove spaces)
    - SHA256 hashing for answer verification
    - Salt usage for additional security
    - Never stores plaintext answers in memory
    
    Example:
        >>> checker = AnswerChecker()
        >>> normalized = checker.normalize_answer("Steve JÓBS")
        >>> normalized
        'stevejobs'
        >>> 
        >>> # Hashing an answer
        >>> answer_hash, salt = checker.hash_answer("Steve Jobs")
        >>> # answer_hash is SHA256(stevejobs + salt)
        >>>
        >>> # Verifying a user input
        >>> is_correct = checker.verify_answer("STEVE jobs", answer_hash, salt)
        >>> is_correct
        True
    """
    
    def __init__(self):
        """Initialize AnswerChecker."""
        logger.debug("AnswerChecker initialized")
    
    @staticmethod
    def normalize_answer(answer: str) -> str:
        """
        Normalize answer for comparison.
        
        Normalization process:
        1. Strip whitespace
        2. Convert to lowercase
        3. Remove diacritical marks (ě→e, š→s, č→c, etc.)
        4. Remove all spaces
        
        Args:
            answer: Raw user answer
            
        Returns:
            Normalized answer
            
        Raises:
            ValueError: If answer is empty after normalization
            
        Example:
            >>> AnswerChecker.normalize_answer("Steve JÓBS")
            'stevejobs'
            >>> AnswerChecker.normalize_answer("  Štěpán  ")
            'stepan'
            >>> AnswerChecker.normalize_answer("GOOGLE")
            'google'
        """
        if not answer:
            raise ValueError("Answer cannot be empty")
        
        # Strip whitespace
        text = answer.strip()
        
        # Lowercase
        text = text.lower()
        
        # Remove diacritics using Unicode normalization
        # NFKD = Compatibility Decomposition
        nfkd_form = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
        
        # Remove all spaces
        text = text.replace(" ", "")
        
        if not text:
            raise ValueError("Answer is empty after normalization")
        
        return text
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """
        Generate random salt for hashing.
        
        Args:
            length: Length of salt in bytes (default 32)
            
        Returns:
            Hexadecimal random salt
            
        Example:
            >>> salt = AnswerChecker.generate_salt()
            >>> len(salt)
            64  # 32 bytes = 64 hex chars
        """
        import secrets
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def hash_answer(answer: str, salt: str = "") -> Tuple[str, str]:
        """
        Hash answer with optional salt.
        
        Args:
            answer: Answer to hash (will be normalized first)
            salt: Salt to use (if empty, generates new one)
            
        Returns:
            Tuple of (answer_hash, salt)
            
        Example:
            >>> hash1, salt1 = AnswerChecker.hash_answer("Steve Jobs")
            >>> hash2, salt2 = AnswerChecker.hash_answer("Steve Jobs", salt1)
            >>> hash1 == hash2  # Same input + same salt = same hash
            True
        """
        # Generate salt if not provided
        if not salt:
            salt = AnswerChecker.generate_salt()
        
        # Normalize answer
        normalized = AnswerChecker.normalize_answer(answer)
        
        # Hash with salt
        combined = normalized + salt
        answer_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return answer_hash, salt
    
    @staticmethod
    def verify_answer(
        user_answer: str,
        answer_hash: str,
        salt: str
    ) -> bool:
        """
        Verify if user answer matches stored hash.
        
        Args:
            user_answer: Answer provided by user (raw, not normalized)
            answer_hash: Stored SHA256 hash
            salt: Salt used in original hash
            
        Returns:
            True if answer is correct, False otherwise
            
        Raises:
            ValueError: If any parameter is invalid
            
        Example:
            >>> # Setup: Store hash during quiz preparation
            >>> correct_hash, correct_salt = AnswerChecker.hash_answer("Steve Jobs")
            >>> 
            >>> # During quiz: Check user input
            >>> is_correct = AnswerChecker.verify_answer(
            ...     "STEVE jobs",
            ...     correct_hash,
            ...     correct_salt
            ... )
            >>> is_correct
            True
            >>>
            >>> # Wrong answer
            >>> is_correct = AnswerChecker.verify_answer(
            ...     "Bill Gates",
            ...     correct_hash,
            ...     correct_salt
            ... )
            >>> is_correct
            False
        """
        if not user_answer or not answer_hash or not salt:
            raise ValueError("user_answer, answer_hash, and salt cannot be empty")
        
        try:
            # Hash the user's answer with the provided salt
            computed_hash, _ = AnswerChecker.hash_answer(user_answer, salt)
            
            # Compare hashes (constant-time comparison would be ideal for prod)
            return computed_hash == answer_hash
        
        except ValueError:
            # Answer normalization failed
            return False
    
    @staticmethod
    def get_answer_length(answer: str) -> int:
        """
        Get the length of normalized answer.
        
        Args:
            answer: Answer text
            
        Returns:
            Length after normalization
            
        Example:
            >>> AnswerChecker.get_answer_length("Steve Jobs")
            10  # "stevejobs" after normalization
        """
        normalized = AnswerChecker.normalize_answer(answer)
        return len(normalized)
