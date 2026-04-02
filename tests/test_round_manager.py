"""
Unit tests for RoundManager service.
"""

import pytest
from models.question import Question
from models.team import Team
from models.score import ScoreRecord
from services.round_manager import RoundManager


@pytest.fixture
def sample_question():
    """Create a sample question for testing."""
    from services.answer_checker import AnswerChecker
    
    # Create a test answer hash (for "Steve Jobs")
    answer_hash, salt = AnswerChecker.hash_answer("Steve Jobs")
    
    return Question(
        id="test_q1",
        image_id="img_test_1",
        answer_hash=answer_hash,
        answer_salt=salt,
        answer_length=10,  # Length of "stevejobs"
        category="IT Personalities",
        difficulty="easy"
    )


@pytest.fixture
def sample_team():
    """Create a sample team."""
    return Team(name="Team test")


class TestRoundManager:
    """Tests for RoundManager."""
    
    def test_initialization(self, sample_question, sample_team):
        """Test RoundManager initialization."""
        manager = RoundManager(sample_question, sample_team.name)
        
        assert manager.question == sample_question
        assert manager.team_name == sample_team.name
        assert manager.game_state is not None
    
    def test_start_round(self, sample_question, sample_team):
        """Test starting a round."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        assert manager.round is not None
        assert manager.game_state is not None
        assert manager.timer is not None
        assert manager.hint_system is not None
    
    def test_reveal_cell_first_free(self, sample_question, sample_team):
        """Test revealing first cell (free)."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        was_new, penalty = manager.reveal_cell(0)
        
        assert was_new is True
        assert penalty == 0  # First cell is free
    
    def test_reveal_cell_second_negative(self, sample_question, sample_team):
        """Test revealing second cell (-1)."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        manager.reveal_cell(0)  # First (free)
        was_new, penalty = manager.reveal_cell(1)  # Second
        
        assert was_new is True
        assert penalty == -1
    
    def test_reveal_cell_duplicate(self, sample_question, sample_team):
        """Test revealing already revealed cell."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        manager.reveal_cell(0)
        was_new, penalty = manager.reveal_cell(0)  # Reveal again
        
        assert was_new is False
        assert penalty == 0  # No additional penalty
    
    def test_request_hint_random(self, sample_question, sample_team):
        """Test requesting random hint."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        letter = manager.request_hint_random()
        
        # Should return a single character (can be uppercase or lowercase)
        assert isinstance(letter, str)
        assert len(letter) == 1
        # Should be a letter
        assert letter.isalpha()
    
    def test_check_answer_correct(self, sample_question, sample_team):
        """Test correct answer."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        # Correct answer
        is_correct = manager.check_answer("Steve Jobs")
        assert is_correct is True
    
    def test_check_answer_correct_variations(self, sample_question, sample_team):
        """Test correct answer with variations."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        # Different variations should all be correct
        assert manager.check_answer("steve jobs") is True
        assert manager.check_answer("STEVE JOBS") is True
        assert manager.check_answer("  Steve  Jobs  ") is True
    
    def test_check_answer_wrong(self, sample_question, sample_team):
        """Test wrong answer."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        is_correct = manager.check_answer("Bill Gates")
        assert is_correct is False
    
    def test_check_answer_applies_penalty(self, sample_question, sample_team):
        """Test that wrong answer applies penalty."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        score_before = manager.game_state.current_score
        
        manager.check_answer("Wrong Answer")
        
        score_after = manager.game_state.current_score
        assert score_after == score_before - 20
    
    def test_finalize(self, sample_question, sample_team):
        """Test finalizing a round."""
        manager = RoundManager(sample_question, sample_team.name)
        manager.start()
        
        # Do some actions
        manager.reveal_cell(0)
        manager.reveal_cell(1)
        
        score_record = manager.finalize(is_correct=True)
        
        assert isinstance(score_record, ScoreRecord)
        assert score_record.is_correct is True
        assert score_record.final_points >= 0
        assert score_record.round_number >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
