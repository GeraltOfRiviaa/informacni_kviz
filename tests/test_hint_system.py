"""
Unit tests for HintSystem service.
"""

import pytest
from services.hint_system import HintSystem


class TestHintSystem:
    """Tests for HintSystem."""
    
    def test_initialization(self):
        """Test HintSystem initialization."""
        hint = HintSystem("steve", max_hints=10)
        
        assert hint.answer == "steve"
        assert hint.max_hints == 10
        assert len(hint.all_letters) == 4  # s, t, e, v
    
    def test_invalid_initialization(self):
        """Test invalid initialization."""
        with pytest.raises(ValueError):
            HintSystem("", max_hints=10)
        
        with pytest.raises(ValueError):
            HintSystem("hello", max_hints=0)
    
    def test_get_all_letters(self):
        """Test getting all letters."""
        hint = HintSystem("steve")
        letters = hint.get_all_letters()
        
        # Should be sorted unique letters
        assert set(letters) == {'s', 't', 'e', 'v'}
        assert letters == sorted(letters)
    
    def test_reveal_letter(self):
        """Test revealing a letter."""
        hint = HintSystem("steve")
        
        # Reveal S
        was_new = hint.reveal_letter('S')
        assert was_new is True
        assert 's' in hint.revealed_letters
        
        # Try to reveal again
        was_new = hint.reveal_letter('s')
        assert was_new is False
    
    def test_reveal_invalid_letter(self):
        """Test revealing letter not in answer."""
        hint = HintSystem("steve")
        
        with pytest.raises(ValueError):
            hint.reveal_letter('Z')
    
    def test_reveal_random_letter(self):
        """Test random letter reveal."""
        hint = HintSystem("steve")
        
        letter = hint.reveal_random_letter()
        assert letter.lower() in hint.all_letters
        assert letter.lower() in hint.revealed_letters
    
    def test_reveal_random_all_letters(self):
        """Test that random reveal fails when all revealed."""
        hint = HintSystem("abc")
        
        # Reveal all letters
        hint.reveal_letter('a')
        hint.reveal_letter('b')
        hint.reveal_letter('c')
        
        # Now should raise error
        with pytest.raises(RuntimeError):
            hint.reveal_random_letter()
    
    def test_is_letter_revealed(self):
        """Test checking if letter is revealed."""
        hint = HintSystem("hello")
        
        assert hint.is_letter_revealed('H') is False
        
        hint.reveal_letter('H')
        assert hint.is_letter_revealed('h') is True
    
    def test_get_display(self):
        """Test display string."""
        hint = HintSystem("steve")
        
        # Initially all hidden
        assert hint.get_display() == "_____"
        
        # Reveal S
        hint.reveal_letter('S')
        assert hint.get_display() == "s____"
        
        # Reveal all E
        hint.reveal_letter('E')
        assert hint.get_display() == "s_e_e"
    
    def test_is_completed(self):
        """Test completion check."""
        hint = HintSystem("abc")
        
        assert hint.is_completed() is False
        
        hint.reveal_letter('a')
        assert hint.is_completed() is False
        
        hint.reveal_letter('b')
        hint.reveal_letter('c')
        assert hint.is_completed() is True
    
    def test_hints_remaining(self):
        """Test remaining hints."""
        hint = HintSystem("steve", max_hints=5)
        
        assert hint.hints_remaining() == 5
        
        hint.reveal_letter('s')
        assert hint.hints_remaining() == 4
        
        hint.reveal_letter('t')
        assert hint.hints_remaining() == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
