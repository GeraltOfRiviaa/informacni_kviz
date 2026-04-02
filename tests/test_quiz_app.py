"""
Unit tests for QuizApp application controller.
"""

import pytest

from app import QuizApp
from config import AppConfig
from models import Question, Team


class TestQuizApp:
    """Tests for QuizApp controller."""
    
    def test_quiz_app_initialization(self):
        """Test app initialization."""
        config = AppConfig()
        app = QuizApp(config=config)
        
        assert app.config == config
        assert len(app.teams) == 0
        assert app.current_team_index == 0
        assert app.current_round_number == 0
    
    def test_add_team(self):
        """Test adding teams."""
        app = QuizApp()
        
        team1 = Team(name="Team A", members=["Alice", "Bob"])
        app.add_team(team1)
        
        assert len(app.teams) == 1
        assert app.teams[0].name == "Team A"
    
    def test_add_duplicate_team(self):
        """Test that duplicate team names raise error."""
        app = QuizApp()
        
        team1 = Team(name="Team A")
        app.add_team(team1)
        
        team2 = Team(name="Team A")
        with pytest.raises(ValueError):
            app.add_team(team2)
    
    def test_get_current_team(self):
        """Test getting current team."""
        app = QuizApp()
        
        # No teams yet
        assert app.get_current_team() is None
        
        # Add teams
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        app.add_team(team1)
        app.add_team(team2)
        
        # Current team is first
        assert app.get_current_team().name == "Team A"
    
    def test_next_team(self):
        """Test switching to next team."""
        app = QuizApp()
        
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        team3 = Team(name="Team C")
        
        app.add_team(team1)
        app.add_team(team2)
        app.add_team(team3)
        
        # Initial: Team A
        assert app.get_current_team().name == "Team A"
        
        # Next: Team B
        assert app.next_team() is True
        assert app.get_current_team().name == "Team B"
        
        # Next: Team C
        assert app.next_team() is True
        assert app.get_current_team().name == "Team C"
        
        # No more teams
        assert app.next_team() is False
    
    def test_start_round(self):
        """Test starting a round."""
        app = QuizApp()
        team = Team(name="Team A")
        app.add_team(team)
        
        question = Question(
            id="q1", image_id="img_001", answer_hash="hash",
            answer_salt="salt", answer_length=5,
            difficulty="easy", category="test"
        )
        
        manager = app.start_round(question)
        
        assert app.current_round_number == 1
        assert app.current_game_state is not None
        # manager.round is None until manager.start()
        assert manager.round is None
        
        # Start the manager
        manager.start()
        assert manager.round is not None
        assert manager.round.team_name == "Team A"
    
    def test_start_round_no_team(self):
        """Test that starting round without team raises error."""
        app = QuizApp()
        
        question = Question(
            id="q1", image_id="img_001", answer_hash="hash",
            answer_salt="salt", answer_length=5,
            difficulty="easy", category="test"
        )
        
        with pytest.raises(ValueError):
            app.start_round(question)
    
    def test_is_game_complete(self):
        """Test game completion check."""
        config = AppConfig()
        config.game.total_rounds = 3
        app = QuizApp(config=config)
        
        assert app.is_game_complete() is False
        
        app.current_round_number = 3
        assert app.is_game_complete() is True
    
    def test_get_rounds_remaining(self):
        """Test getting remaining rounds."""
        config = AppConfig()
        config.game.total_rounds = 5
        app = QuizApp(config=config)
        
        assert app.get_rounds_remaining() == 5
        
        app.current_round_number = 2
        assert app.get_rounds_remaining() == 3
        
        app.current_round_number = 5
        assert app.get_rounds_remaining() == 0
    
    def test_get_scores_summary(self):
        """Test getting sorted scores."""
        app = QuizApp()
        
        team_a = Team(name="Team A")
        team_b = Team(name="Team B")
        team_c = Team(name="Team C")
        
        app.add_team(team_a)
        app.add_team(team_b)
        app.add_team(team_c)
        
        team_a.add_round_score(100)
        team_b.add_round_score(150)
        team_c.add_round_score(120)
        
        scores = app.get_scores_summary()
        
        # Should be sorted descending by score
        assert scores[0] == ("Team B", 150)
        assert scores[1] == ("Team C", 120)
        assert scores[2] == ("Team A", 100)
    
    def test_get_total_teams(self):
        """Test getting team count."""
        app = QuizApp()
        assert app.get_total_teams() == 0
        
        app.add_team(Team(name="Team A"))
        assert app.get_total_teams() == 1
        
        app.add_team(Team(name="Team B"))
        assert app.get_total_teams() == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
