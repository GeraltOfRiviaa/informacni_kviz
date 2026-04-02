"""
Unit tests for AnswerChecker service.
"""

import pytest
from services.answer_checker import AnswerChecker


class TestAnswerChecker:
    """Tests for AnswerChecker."""
    
    def test_normalize_answer_basic(self):
        """Test basic normalization."""
        assert AnswerChecker.normalize_answer("hello") == "hello"
        assert AnswerChecker.normalize_answer("HELLO") == "hello"
        assert AnswerChecker.normalize_answer("HeLLo") == "hello"
    
    def test_normalize_answer_spaces(self):
        """Test space removal."""
        assert AnswerChecker.normalize_answer("hello world") == "helloworld"
        assert AnswerChecker.normalize_answer("  hello  world  ") == "helloworld"
    
    def test_normalize_answer_diacritics(self):
        """Test diacritic removal."""
        assert AnswerChecker.normalize_answer("Štěpán") == "stepan"
        assert AnswerChecker.normalize_answer("JÓBS") == "jobs"
        assert AnswerChecker.normalize_answer("Ěčřžýáíé") == "ecrzyaie"
    
    def test_normalize_answer_combined(self):
        """Test combined normalization."""
        assert AnswerChecker.normalize_answer("Steve JÓBS") == "stevejobs"
        assert AnswerChecker.normalize_answer("  GOOGLE  ") == "google"
    
    def test_normalize_answer_empty(self):
        """Test error on empty answer."""
        with pytest.raises(ValueError):
            AnswerChecker.normalize_answer("")
        
        with pytest.raises(ValueError):
            AnswerChecker.normalize_answer("   ")
    
    def test_generate_salt(self):
        """Test salt generation."""
        salt1 = AnswerChecker.generate_salt()
        salt2 = AnswerChecker.generate_salt()
        
        # Should be hex string
        assert len(salt1) == 32  # 16 bytes = 32 hex chars
        assert len(salt2) == 32
        
        # Should be different each time
        assert salt1 != salt2
    
    def test_hash_answer(self):
        """Test hashing answers."""
        hash1, salt1 = AnswerChecker.hash_answer("Steve Jobs")
        hash2, salt2 = AnswerChecker.hash_answer("Steve Jobs")
        
        # Different salts = different hashes
        assert hash1 != hash2
        assert salt1 != salt2
    
    def test_hash_answer_with_salt(self):
        """Test hashing with specific salt."""
        hash1, salt1 = AnswerChecker.hash_answer("Steve Jobs")
        hash2, salt2 = AnswerChecker.hash_answer("Steve Jobs", salt1)
        
        # Same salt = same hash
        assert hash1 == hash2
        assert salt1 == salt2
    
    def test_verify_answer_correct(self):
        """Test verifying correct answer."""
        correct_hash, correct_salt = AnswerChecker.hash_answer("Steve Jobs")
        
        # Different capitalizations
        assert AnswerChecker.verify_answer("steve jobs", correct_hash, correct_salt) is True
        assert AnswerChecker.verify_answer("STEVE JOBS", correct_hash, correct_salt) is True
        assert AnswerChecker.verify_answer("Steve Jobs", correct_hash, correct_salt) is True
        assert AnswerChecker.verify_answer("  STEVE   JOBS  ", correct_hash, correct_salt) is True
    
    def test_verify_answer_wrong(self):
        """Test verifying wrong answer."""
        correct_hash, correct_salt = AnswerChecker.hash_answer("Steve Jobs")
        
        assert AnswerChecker.verify_answer("Bill Gates", correct_hash, correct_salt) is False
        assert AnswerChecker.verify_answer("Steve", correct_hash, correct_salt) is False
        assert AnswerChecker.verify_answer("Jobs", correct_hash, correct_salt) is False
    
    def test_verify_answer_with_diacritics(self):
        """Test verifying with diacritics."""
        correct_hash, correct_salt = AnswerChecker.hash_answer("JÓBS")
        
        # Should match normalized version
        assert AnswerChecker.verify_answer("JOBS", correct_hash, correct_salt) is True
        assert AnswerChecker.verify_answer("jobs", correct_hash, correct_salt) is True
    
    def test_get_answer_length(self):
        """Test getting answer length."""
        assert AnswerChecker.get_answer_length("Steve Jobs") == 9  # stevejobs (9 chars)
        assert AnswerChecker.get_answer_length("Google") == 6
        assert AnswerChecker.get_answer_length("  hello world  ") == 10  # helloworld


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
