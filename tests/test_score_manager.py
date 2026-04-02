"""
Unit tests for ScoreManager service.
"""

import pytest
from config import ScoringConfig
from services.score_manager import ScoreManager


class TestScoreManager:
    """Tests for ScoreManager."""
    
    def test_initialization(self):
        """Test ScoreManager initialization."""
        sm = ScoreManager()
        assert sm.base_points == 120
    
    def test_get_cell_penalty(self):
        """Test getting cell penalties."""
        sm = ScoreManager()
        
        assert sm.get_cell_penalty(1) == 0   # First free
        assert sm.get_cell_penalty(2) == -1  # Second
        assert sm.get_cell_penalty(3) == -2  # Third
        assert sm.get_cell_penalty(16) == -15  # Last
    
    def test_calculate_cell_penalties(self):
        """Test calculating total cell penalties."""
        sm = ScoreManager()
        
        assert sm.calculate_cell_penalties(0) == 0      # None revealed
        assert sm.calculate_cell_penalties(1) == 0      # First free
        assert sm.calculate_cell_penalties(2) == -1     # 0 + -1
        assert sm.calculate_cell_penalties(3) == -3     # 0 + -1 + -2
        assert sm.calculate_cell_penalties(5) == -10    # Sum: 0-1-2-3-4
    
    def test_calculate_letter_penalties(self):
        """Test letter hint penalties."""
        sm = ScoreManager()
        
        assert sm.calculate_letter_penalties(0) == 0
        assert sm.calculate_letter_penalties(1) == -1
        assert sm.calculate_letter_penalties(3) == -3
        assert sm.calculate_letter_penalties(10) == -10
    
    def test_calculate_wrong_attempt_penalties(self):
        """Test wrong attempt penalties."""
        sm = ScoreManager()
        
        assert sm.calculate_wrong_attempt_penalties(0) == 0
        assert sm.calculate_wrong_attempt_penalties(1) == -20
        assert sm.calculate_wrong_attempt_penalties(2) == -40
    
    def test_calculate_final_score_perfect(self):
        """Test perfect score (no penalties)."""
        sm = ScoreManager()
        
        # No reveals, no hints, no wrong answers
        score = sm.calculate_final_score(0, 0, 0)
        assert score == 120
    
    def test_calculate_final_score_with_cells(self):
        """Test score with cell reveals."""
        sm = ScoreManager()
        
        # Reveal 5 cells: 0-1-2-3-4 = -10
        score = sm.calculate_final_score(5, 0, 0)
        assert score == 110  # 120 - 10
    
    def test_calculate_final_score_with_hints(self):
        """Test score with letter hints."""
        sm = ScoreManager()
        
        # 3 hints
        score = sm.calculate_final_score(0, 3, 0)
        assert score == 117  # 120 - 3
    
    def test_calculate_final_score_with_wrong(self):
        """Test score with wrong attempts."""
        sm = ScoreManager()
        
        # 2 wrong attempts
        score = sm.calculate_final_score(0, 0, 2)
        assert score == 80  # 120 - 40
    
    def test_calculate_final_score_combined(self):
        """Test combined penalties."""
        sm = ScoreManager()
        
        # 5 cells (-10) + 3 hints (-3) + 1 wrong (-20)
        score = sm.calculate_final_score(5, 3, 1)
        assert score == 87  # 120 - 10 - 3 - 20
    
    def test_final_score_never_negative(self):
        """Test that final score never goes below 0."""
        sm = ScoreManager()
        
        # Many penalties
        score = sm.calculate_final_score(16, 100, 10)
        assert score >= 0
    
    def test_get_scoring_summary(self):
        """Test scoring summary."""
        sm = ScoreManager()
        
        summary = sm.get_scoring_summary(5, 2, 1)
        
        assert summary['base_points'] == 120
        assert summary['cells_revealed'] == 5
        assert summary['cell_penalty'] == -10
        assert summary['letters_revealed'] == 2
        assert summary['letter_penalty'] == -2
        assert summary['wrong_attempts'] == 1
        assert summary['wrong_penalty'] == -20
        assert summary['final_score'] == 88


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
