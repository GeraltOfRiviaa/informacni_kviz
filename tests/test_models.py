"""
Unit tests for model classes.
"""

import pytest
from datetime import datetime

from models import Question, Team, Grid, GameState, Round, ScoreRecord


class TestQuestion:
    """Tests for Question model."""
    
    def test_question_creation(self):
        """Test basic question creation."""
        q = Question(
            id="q001",
            image_id="img_087",
            answer_hash="abc123hash",
            answer_salt="salt123",
            answer_length=5,
            difficulty="easy",
            category="personality",
        )
        assert q.id == "q001"
        assert q.image_id == "img_087"
        assert q.answer_length == 5
    
    def test_question_invalid_id(self):
        """Test that empty ID raises error."""
        with pytest.raises(ValueError):
            Question(
                id="",
                image_id="img_001",
                answer_hash="hash",
                answer_salt="salt",
                answer_length=5,
                difficulty="easy",
                category="test",
            )
    
    def test_question_invalid_length(self):
        """Test that invalid answer length raises error."""
        with pytest.raises(ValueError):
            Question(
                id="q001",
                image_id="img_001",
                answer_hash="hash",
                answer_salt="salt",
                answer_length=0,  # Invalid!
                difficulty="easy",
                category="test",
            )
    
    def test_question_invalid_difficulty(self):
        """Test that invalid difficulty raises error."""
        with pytest.raises(ValueError):
            Question(
                id="q001",
                image_id="img_001",
                answer_hash="hash",
                answer_salt="salt",
                answer_length=5,
                difficulty="impossible",  # Invalid!
                category="test",
            )


class TestTeam:
    """Tests for Team model."""
    
    def test_team_creation(self):
        """Test basic team creation."""
        team = Team(
            name="Team Alpha",
            members=["Alice", "Bob", "Charlie"],
        )
        assert team.name == "Team Alpha"
        assert len(team.members) == 3
        assert team.total_score == 0
    
    def test_team_invalid_members(self):
        """Test that team with > 3 members raises error."""
        with pytest.raises(ValueError):
            Team(
                name="Team",
                members=["A", "B", "C", "D"],  # Too many!
            )
    
    def test_team_add_round_score(self):
        """Test adding round score."""
        team = Team(name="Team A")
        team.add_round_score(95)
        assert team.total_score == 95
        assert team.rounds_played == 1
        
        team.add_round_score(80)
        assert team.total_score == 175
        assert team.rounds_played == 2
    
    def test_team_negative_score(self):
        """Test that negative score raises error."""
        team = Team(name="Team A")
        with pytest.raises(ValueError):
            team.add_round_score(-10)
    
    def test_team_reset_round(self):
        """Test resetting round score."""
        team = Team(name="Team A")
        team.add_round_score(100)
        team.reset_round()
        assert team.current_round_score == 0
        assert team.total_score == 100  # Total not affected


class TestGrid:
    """Tests for Grid model."""
    
    def test_grid_creation(self):
        """Test basic grid creation."""
        grid = Grid(size=4)
        assert grid.get_total_cells() == 16
        assert grid.get_revealed_count() == 0
        assert grid.get_hidden_count() == 16
    
    def test_grid_reveal_cell(self):
        """Test revealing a cell."""
        grid = Grid(size=4)
        
        # First reveal
        assert grid.reveal_cell(0) is True
        assert grid.get_revealed_count() == 1
        
        # Second reveal of same cell
        assert grid.reveal_cell(0) is False
        assert grid.get_revealed_count() == 1
    
    def test_grid_invalid_cell_index(self):
        """Test that invalid cell index raises error."""
        grid = Grid(size=4)
        
        with pytest.raises(ValueError):
            grid.reveal_cell(-1)
        
        with pytest.raises(ValueError):
            grid.reveal_cell(16)  # Only 0-15 valid
    
    def test_grid_is_revealed(self):
        """Test checking if cell is revealed."""
        grid = Grid(size=4)
        assert grid.is_revealed(0) is False
        
        grid.reveal_cell(0)
        assert grid.is_revealed(0) is True
    
    def test_grid_reset(self):
        """Test resetting grid."""
        grid = Grid(size=4)
        grid.reveal_cell(0)
        grid.reveal_cell(5)
        assert grid.get_revealed_count() == 2
        
        grid.reset()
        assert grid.get_revealed_count() == 0
    
    def test_grid_position_conversion(self):
        """Test converting between linear index and (row, col)."""
        grid = Grid(size=4)
        
        # Index 0 → (0, 0)
        assert grid.get_grid_position(0) == (0, 0)
        
        # Index 4 → (1, 0)
        assert grid.get_grid_position(4) == (1, 0)
        
        # Index 15 → (3, 3)
        assert grid.get_grid_position(15) == (3, 3)
    
    def test_grid_cell_index_conversion(self):
        """Test converting (row, col) to linear index."""
        grid = Grid(size=4)
        
        assert grid.get_cell_index(0, 0) == 0
        assert grid.get_cell_index(1, 0) == 4
        assert grid.get_cell_index(3, 3) == 15


class TestGameState:
    """Tests for GameState model."""
    
    def test_game_state_creation(self):
        """Test basic game state creation."""
        q = Question(
            id="q1", image_id="img1", answer_hash="h", answer_salt="s",
            answer_length=5, difficulty="easy", category="test"
        )
        grid = Grid(size=4)
        
        state = GameState(question=q, grid=grid, time_remaining=600)
        assert state.is_active is True
        assert state.current_score == 120  # Initialized from base_score
        assert state.cells_revealed_count == 0
    
    def test_game_state_reduce_time(self):
        """Test reducing time."""
        q = Question(
            id="q1", image_id="img1", answer_hash="h", answer_salt="s",
            answer_length=5, difficulty="easy", category="test"
        )
        grid = Grid(size=4)
        state = GameState(question=q, grid=grid, time_remaining=100)
        
        state.reduce_time(30)
        assert state.time_remaining == 70
        
        state.reduce_time(70)
        assert state.time_remaining == 0
        assert state.is_active is False
    
    def test_game_state_reveal_letter(self):
        """Test revealing a letter."""
        q = Question(
            id="q1", image_id="img1", answer_hash="h", answer_salt="s",
            answer_length=5, difficulty="easy", category="test"
        )
        grid = Grid(size=4)
        state = GameState(question=q, grid=grid, time_remaining=600)
        
        initial_score = state.current_score
        state.add_revealed_letter("S", penalty=1)
        
        assert "S" in state.revealed_letters
        assert state.current_score == initial_score - 1


class TestScoreRecord:
    """Tests for ScoreRecord model."""
    
    def test_score_record_creation(self):
        """Test score record creation."""
        record = ScoreRecord(
            round_number=1,
            base_points=120,
            cells_revealed=5,
            penalty_cells=7,
            letters_revealed=2,
            penalty_letters=2,
            wrong_attempts=1,
            penalty_wrong=20,
            final_points=91,
        )
        assert record.round_number == 1
        assert record.final_points == 91
    
    def test_score_record_penalty_summary(self):
        """Test penalty summary calculation."""
        record = ScoreRecord(
            round_number=1,
            base_points=120,
            cells_revealed=5,
            penalty_cells=7,
            letters_revealed=2,
            penalty_letters=2,
            wrong_attempts=1,
            penalty_wrong=20,
            final_points=91,
        )
        
        summary = record.get_penalty_summary()
        assert summary["cells_penalty"] == 7
        assert summary["letters_penalty"] == 2
        assert summary["wrong_attempts_penalty"] == 20
        assert summary["total_penalty"] == 29


class TestRound:
    """Tests for Round model."""
    
    def test_round_creation(self):
        """Test round creation."""
        q = Question(
            id="q1", image_id="img1", answer_hash="h", answer_salt="s",
            answer_length=5, difficulty="easy", category="test"
        )
        grid = Grid(size=4)
        
        round_obj = Round(
            round_number=1,
            question=q,
            grid=grid,
            team_name="Team A",
        )
        
        assert round_obj.round_number == 1
        assert round_obj.team_name == "Team A"
        assert round_obj.is_completed is False
    
    def test_round_finalize(self):
        """Test finalizing a round."""
        q = Question(
            id="q1", image_id="img1", answer_hash="h", answer_salt="s",
            answer_length=5, difficulty="easy", category="test"
        )
        grid = Grid(size=4)
        round_obj = Round(
            round_number=1,
            question=q,
            grid=grid,
            team_name="Team A",
        )
        
        score_record = ScoreRecord(
            round_number=1, base_points=120, cells_revealed=5,
            penalty_cells=7, letters_revealed=2, penalty_letters=2,
            wrong_attempts=0, penalty_wrong=0, final_points=111, is_correct=True
        )
        
        round_obj.finalize(is_correct=True, score_record=score_record)
        
        assert round_obj.is_completed is True
        assert round_obj.is_correct is True
        assert round_obj.score_record == score_record


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
