"""
Integration tests for Etapa 3 - Full game round flow with RoundManager.
Tests end-to-end game mechanics with all services working together.
"""

import pytest
from app.quiz_app import QuizApp
from models import Question, Team, Round
from services.answer_checker import AnswerChecker
from services.round_manager import RoundManager


@pytest.fixture
def app_with_team():
    """Create app with a team."""
    app = QuizApp()
    app.add_team(Team("Test Team"))
    return app


@pytest.fixture
def test_question():
    """Create a test question."""
    # Test answer is "Steve Jobs" (after normalization: "stevejobs", length 9)
    answer_hash, salt = AnswerChecker.hash_answer("Steve Jobs")
    return Question(
        id="test_q1",
        image_id="img_test_1",
        answer_hash=answer_hash,
        answer_salt=salt,
        answer_length=9,
        category="Test",
        difficulty="easy"
    )


class TestStage3Integration:
    """Integration tests for complete round flow."""
    
    def test_start_round_returns_manager(self, app_with_team, test_question):
        """Test that start_round returns RoundManager."""
        manager = app_with_team.start_round(test_question)
        
        # Should return RoundManager, not None
        assert isinstance(manager, RoundManager)
        assert manager.question == test_question
        assert manager.team_name == "Test Team"
    
    def test_complete_round_flow(self, app_with_team, test_question):
        """Test complete round flow: reveal -> hint -> answer."""
        # Start round
        manager = app_with_team.start_round(test_question)
        manager.start()
        
        # Reveal cells
        cell1_new, cell1_penalty = manager.reveal_cell(0)  # First (free)
        assert cell1_new is True
        assert cell1_penalty == 0
        
        cell2_new, cell2_penalty = manager.reveal_cell(1)  # Second (-1)
        assert cell2_new is True
        assert cell2_penalty == -1
        
        # Get a hint
        letter = manager.request_hint_random()
        assert isinstance(letter, str)
        assert letter.isalpha()
        
        # Finalize round with correct answer
        score = manager.finalize(is_correct=True)
        
        assert score.is_correct is True
        assert score.final_points <= 120
        assert score.cells_revealed == 2
        assert score.letters_revealed >= 1
    
    def test_round_with_wrong_answer(self, app_with_team, test_question):
        """Test round with wrong answer."""
        manager = app_with_team.start_round(test_question)
        manager.start()
        
        # Try wrong answer
        is_correct = manager.check_answer("Wrong Answer")
        assert is_correct is False
        
        # Try correct answer
        is_correct = manager.check_answer("Steve Jobs")
        assert is_correct is True
        
        # Finalize
        score = manager.finalize(is_correct=True)
        assert score.is_correct is True
        assert score.wrong_attempts >= 1
    
    def test_multiple_teams_sequence(self):
        """Test game flow with multiple teams."""
        app = QuizApp()
        app.add_team(Team("Team A"))
        app.add_team(Team("Team B"))
        
        answer_hash, salt = AnswerChecker.hash_answer("Answer")
        question = Question(
            id="q1",
            image_id="img_1",
            answer_hash=answer_hash,
            answer_salt=salt,
            answer_length=6,
            category="Test",
            difficulty="easy"
        )
        
        # Team A plays
        assert app.get_current_team().name == "Team A"
        manager_a = app.start_round(question)
        assert isinstance(manager_a, RoundManager)
        
        # Move to Team B
        assert app.next_team() is True
        assert app.get_current_team().name == "Team B"
        manager_b = app.start_round(question)
        assert isinstance(manager_b, RoundManager)
    
    def test_round_state_tracking(self, app_with_team, test_question):
        """Test that QuizApp and RoundManager track round state correctly."""
        initial_round = app_with_team.current_round_number
        
        manager = app_with_team.start_round(test_question)
        
        # Round number should increase
        assert app_with_team.current_round_number == initial_round + 1
        
        # Current game state should be set immediately
        assert app_with_team.current_game_state is not None
        
        # manager.round is None until we start the manager
        assert manager.round is None
        
        # Start the manager
        manager.start()
        
        # Now round should exist
        assert manager.round is not None
        # Can set it on app if needed
        app_with_team.current_round = manager.round
        assert app_with_team.current_round is not None
    
    def test_scoring_summary(self):
        """Test team scoring tracking."""
        app = QuizApp()
        team_a = Team("Team A")
        team_b = Team("Team B")
        app.add_team(team_a)
        app.add_team(team_b)
        
        # Manually adjust scores using update_total_score method
        team_a.total_score = 100
        team_b.total_score = 85
        
        scores = app.get_scores_summary()
        
        # Should be sorted descending
        assert scores[0][0] == "Team A"
        assert scores[0][1] == 100
        assert scores[1][0] == "Team B"
        assert scores[1][1] == 85
    
    def test_game_completion_check(self):
        """Test game completion status."""
        app = QuizApp()
        
        # Not complete initially
        assert app.is_game_complete() is False
        
        # Check remaining rounds
        remaining = app.get_rounds_remaining()
        assert remaining == app.config.game.total_rounds
    
    def test_round_manager_integration_with_app(self, app_with_team, test_question):
        """Test RoundManager works correctly when called from QuizApp."""
        manager = app_with_team.start_round(test_question)
        
        # Verify RoundManager has correct question
        assert manager.question.id == test_question.id
        
        # Verify app tracks the round
        assert app_with_team.current_round_number == 1
        
        # Verify we can operate on manager
        manager.start()
        assert manager.timer.is_running is True
        
        # Verify app game_state is synced
        assert app_with_team.current_game_state == manager.game_state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
